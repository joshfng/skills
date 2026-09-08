#!/usr/bin/env python3
"""Pull the Dortania guides and rewrite them as agent-friendly Markdown.

Downloads each upstream repo as a tarball (no git required), keeps only the
Markdown, strips site-generator syntax that wastes tokens, and writes the tree
into skills/hardware/opencore-expert/references/ along with INDEX.md and a manifest
recording the exact commit each file came from.

Usage:
    python3 scripts/sync_dortania.py [options]

    --repo NAME        Sync only this repo (repeatable)
    --ref REF          Branch/tag/SHA to pull (applies to every selected repo)
    --with-master-guide  Also emit the concatenated references/master_guide.md
    --dry-run          Report what would change without writing
    --check            Exit 1 if upstream has moved past the manifest
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REFERENCES = REPO_ROOT / "skills" / "hardware" / "opencore-expert" / "references"
MANIFEST = REFERENCES / ".sync-manifest.json"

USER_AGENT = "opencore-expert-skill-sync"
API = "https://api.github.com"
WORKERS = 4


@dataclass
class Source:
    """One upstream Dortania repo and how its files map into references/."""

    name: str
    owner: str = "dortania"
    branch: str = "master"
    site: str = ""
    # Only paths under one of these prefixes are kept ("" means repo root).
    include: tuple[str, ...] = ("",)
    # Prefixes stripped from the output path, longest match first.
    strip: tuple[str, ...] = ()
    skip: tuple[str, ...] = field(default_factory=lambda: ("CONTRIBUTING.md",))

    @property
    def site_url(self) -> str:
        return self.site or f"https://dortania.github.io/{self.name}"


SOURCES: dict[str, Source] = {
    s.name: s
    for s in (
        Source("OpenCore-Install-Guide"),
        Source("OpenCore-Post-Install"),
        Source("Getting-Started-With-ACPI"),
        Source(
            "OpenCore-Legacy-Patcher",
            branch="main",
            include=("docs/", "README.md"),
            strip=("docs/",),
            skip=("CONTRIBUTING.md", "CHANGELOG.md", "docs/DONATE.md", "SOURCE.md"),
        ),
    )
}

# --- markdown cleanup ------------------------------------------------------

FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
CONTAINER_OPEN = re.compile(r"^:::\s*(tip|note|info|warning|danger|details)\s*(.*)$", re.I)
CONTAINER_CLOSE = re.compile(r"^:::\s*$")
MD_IMAGE = re.compile(r"!\[([^\]]*)\]\([^)]*\)")
HTML_IMAGE = re.compile(r"<img\b[^>]*>", re.I)
IMG_ALT = re.compile(r'alt=["\']([^"\']*)["\']', re.I)
BLANK_RUN = re.compile(r"\n{3,}")

CONTAINER_LABEL = {
    "tip": "Tip",
    "note": "Note",
    "info": "Note",
    "warning": "Warning",
    "danger": "Danger",
    "details": "Details",
}


def clean_markdown(text: str) -> str:
    """Strip VitePress/mdBook syntax and image payloads an agent cannot use."""
    text = FRONTMATTER.sub("", text)
    text = HTML_COMMENT.sub("", text)
    text = HTML_IMAGE.sub(lambda m: _img_placeholder(IMG_ALT.search(m.group(0))), text)
    text = MD_IMAGE.sub(lambda m: _img_placeholder(m, group=1), text)

    out: list[str] = []
    in_code = False
    quoting = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
            out.append(line)
            continue
        if not in_code:
            opened = CONTAINER_OPEN.match(line.strip())
            if opened:
                kind, title = opened.group(1).lower(), opened.group(2).strip()
                label = title or CONTAINER_LABEL.get(kind, kind.title())
                out.append(f"> **{label}:**")
                quoting = True
                continue
            if quoting and CONTAINER_CLOSE.match(line.strip()):
                quoting = False
                continue
            if quoting:
                out.append(f"> {line}".rstrip())
                continue
        out.append(line.rstrip())

    return BLANK_RUN.sub("\n\n", "\n".join(out)).strip() + "\n"


def _img_placeholder(match, group: int = 1) -> str:
    alt = (match.group(group).strip() if match else "") or "image"
    return f"[image: {alt}]"


def title_of(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def page_url(source: Source, rel: str) -> str:
    path = rel[:-3] + ".html"
    if path.endswith("README.html"):
        path = path[: -len("README.html")] + "index.html"
    return f"{source.site_url}/{path}"


# --- fetching --------------------------------------------------------------


def read_url(url: str, attempts: int = 4) -> bytes:
    """GET a URL, retrying on the transient resets GitHub throws under load."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read()
        except (urllib.error.URLError, TimeoutError, OSError):
            if attempt == attempts:
                raise
            time.sleep(0.5 * attempt)
    raise RuntimeError("unreachable")


def get_json(url: str) -> dict:
    return json.loads(read_url(url))


def resolve_commit(source: Source, ref: str) -> tuple[str, str]:
    """Return (sha, committed_date) for ref, or ("", "") if the API is unavailable."""
    try:
        data = get_json(f"{API}/repos/{source.owner}/{source.name}/commits/{ref}")
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        print(f"  ! commit lookup failed ({exc}); continuing without a SHA")
        return "", ""
    return data["sha"], data["commit"]["committer"]["date"]


def wanted_paths(source: Source, ref: str) -> list[str]:
    """List the repo's Markdown paths that belong in references/."""
    tree = get_json(
        f"{API}/repos/{source.owner}/{source.name}/git/trees/{ref}?recursive=1"
    )
    if tree.get("truncated"):
        print("  ! tree listing truncated by GitHub; some pages may be missing")
    return [
        entry["path"]
        for entry in tree.get("tree", [])
        if entry["type"] == "blob"
        and entry["path"].endswith(".md")
        and entry["path"] not in source.skip
        and any(entry["path"].startswith(p) for p in source.include)
    ]


def output_path(source: Source, rel: str) -> str:
    for prefix in sorted(source.strip, key=len, reverse=True):
        if rel.startswith(prefix):
            return rel[len(prefix) :]
    return rel


def fetch_markdown(source: Source, ref: str) -> dict[str, str]:
    """Return {output_relative_path: raw markdown} for one repo at ref.

    Files are pulled individually from raw.githubusercontent rather than as a
    repo tarball: OCLP ships hundreds of megabytes of binaries we would only
    throw away.
    """
    paths = wanted_paths(source, ref)

    def download(rel: str) -> tuple[str, str]:
        url = f"https://raw.githubusercontent.com/{source.owner}/{source.name}/{ref}/{urllib.parse.quote(rel)}"
        return output_path(source, rel), read_url(url).decode("utf-8", errors="replace")

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        return dict(pool.map(download, paths))


# --- writing ---------------------------------------------------------------


def sync_source(source: Source, ref: str, dry_run: bool) -> dict:
    print(f"* {source.name} @ {ref}")
    sha, date = resolve_commit(source, ref)
    raw = fetch_markdown(source, ref)
    if not raw:
        raise SystemExit(f"no markdown found in {source.name}; check include/strip rules")

    pages = []
    for rel in sorted(raw):
        cleaned = clean_markdown(raw[rel])
        pages.append(
            {
                "path": f"{source.name}/{rel}",
                "title": title_of(cleaned, Path(rel).stem),
                "url": page_url(source, rel),
                "body": cleaned,
            }
        )

    print(f"  {len(pages)} pages")
    if not dry_run:
        target = REFERENCES / source.name
        if target.exists():
            shutil.rmtree(target)
        for page in pages:
            dest = REFERENCES / page["path"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(page["body"], encoding="utf-8")

    return {
        "repo": f"{source.owner}/{source.name}",
        "ref": ref,
        "commit": sha,
        "commit_date": date,
        "pages": len(pages),
        "license": "See the upstream repository. Dortania guides are CC BY-NC-SA 4.0.",
        "_pages": pages,
    }


def scan_references() -> list[tuple[Source, str, str, str]]:
    """Read every synced page back off disk as (source, relative path, title, body).

    Scanning beats reusing the sync results so that a partial `--repo` run still
    regenerates a complete index.
    """
    pages = []
    for name in sorted(SOURCES):
        source = SOURCES[name]
        root = REFERENCES / name
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*.md")):
            body = path.read_text(encoding="utf-8")
            rel = path.relative_to(root).as_posix()
            pages.append((source, rel, title_of(body, path.stem), body))
    return pages


def write_index(pages: list[tuple[Source, str, str, str]]) -> None:
    lines = [
        "# Reference Index",
        "",
        "Every synced Dortania page, by path. Grep this file to route to a file,",
        "then read only that file. Regenerate with `scripts/sync_dortania.py`.",
        "",
    ]
    current = None
    for source, rel, title, _ in pages:
        if source.name != current:
            current = source.name
            lines += [f"## {current}", ""]
        lines.append(f"- `{current}/{rel}` — {title}")
    lines.append("")
    (REFERENCES / "INDEX.md").write_text("\n".join(lines), encoding="utf-8")


def write_master_guide(pages: list[tuple[Source, str, str, str]]) -> None:
    chunks = []
    for source, rel, title, body in pages:
        parents = [p for p in Path(rel).parent.parts if p != "."]
        category = " > ".join([source.name, *parents])
        chunks.append(
            "---\n"
            f"title: {title}\n"
            f"original_url: {page_url(source, rel)}\n"
            f"category: {category}\n"
            "---\n\n"
            f"# {category} > {title}\n\n"
            f"{body}\n---\n"
        )
    (REFERENCES / "master_guide.md").write_text("\n".join(chunks), encoding="utf-8")


def load_manifest() -> dict:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {"sources": {}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", action="append", choices=sorted(SOURCES), default=None)
    parser.add_argument("--ref", default=None, help="branch, tag, or SHA to pull")
    parser.add_argument("--with-master-guide", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--check", action="store_true", help="only report drift")
    args = parser.parse_args()

    selected = [SOURCES[name] for name in (args.repo or sorted(SOURCES))]
    manifest = load_manifest()

    if args.check:
        stale = False
        for source in selected:
            recorded = manifest["sources"].get(source.name, {}).get("commit", "")
            sha, _ = resolve_commit(source, args.ref or source.branch)
            state = "current" if sha and sha == recorded else "STALE"
            stale = stale or state == "STALE"
            print(f"{source.name}: {state} (local {recorded[:8] or '-'}, upstream {sha[:8] or '?'})")
        return 1 if stale else 0

    REFERENCES.mkdir(parents=True, exist_ok=True)
    results = [sync_source(s, args.ref or s.branch, args.dry_run) for s in selected]

    if args.dry_run:
        print("dry run: nothing written")
        return 0

    pages = scan_references()
    write_index(pages)
    if args.with_master_guide:
        write_master_guide(pages)
    elif (REFERENCES / "master_guide.md").exists():
        (REFERENCES / "master_guide.md").unlink()

    for result in results:
        entry = {k: v for k, v in result.items() if not k.startswith("_")}
        manifest["sources"][result["repo"].split("/")[1]] = entry
    manifest["generator"] = "scripts/sync_dortania.py"
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    total = sum(r["pages"] for r in results)
    print(f"wrote {total} pages to {REFERENCES.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
