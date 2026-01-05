from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Ref:
    md_path: Path
    md_dir: Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_md_files(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip some common heavy folders if they exist
        dn = set(dirnames)
        for skip in [".git", "node_modules"]:
            if skip in dn:
                dirnames.remove(skip)
        for fn in filenames:
            if fn.lower().endswith(".md"):
                yield Path(dirpath) / fn


def read_text(path: Path) -> str:
    # Obsidian vault can contain mixed encodings; try utf-8 then fallback.
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig", errors="replace")


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def find_refs(root: Path, png_name: str) -> list[Ref]:
    refs: list[Ref] = []
    needle = png_name
    for md in iter_md_files(root):
        try:
            txt = read_text(md)
        except OSError:
            continue
        if needle in txt:
            refs.append(Ref(md_path=md, md_dir=md.parent))
    return refs


def relpath_posix(from_dir: Path, to_file: Path) -> str:
    rel = os.path.relpath(to_file, start=from_dir)
    return Path(rel).as_posix()


def update_md_links(md_path: Path, png_name: str, new_png_path: Path) -> bool:
    """
    Updates:
    - Obsidian wikilinks: ![[file.png]] / [[file.png]] (also keeps alias part if present)
    - Markdown links: ![](path/to/file.png) and [text](path/to/file.png)
    """
    txt = read_text(md_path)
    before = txt

    target = relpath_posix(md_path.parent, new_png_path)  # e.g. _assets/foo.png or ../_assets/foo.png
    name_re = re.escape(png_name)

    # 1) Obsidian wikilinks: ![[...]] or [[...]]
    # Handle alias: ![[file.png|ALT]] → ![[<target>|ALT]]
    # Only update if the inside is exactly png_name (or ends with /png_name or \\png_name)
    def wl_repl(m: re.Match) -> str:
        bang = m.group(1) or ""
        inside = m.group(2)
        # Split alias if any
        if "|" in inside:
            link_part, alias = inside.split("|", 1)
            alias = "|" + alias
        else:
            link_part, alias = inside, ""

        norm = link_part.replace("\\", "/")
        if norm == png_name or norm.endswith("/" + png_name):
            return f"{bang}[[{target}{alias}]]"
        return m.group(0)

    txt = re.sub(r"(!?)\[\[([^\]]+?)\]\]", wl_repl, txt)

    # 2) Markdown (...) links where URL ends with basename
    #   ![](Pasted image ....png)
    #   ![](../Pasted image ....png)
    #   [](some/path/Pasted image ....png)
    # We only touch the URL inside (...) and only when it ends with the png name.
    def md_repl(m: re.Match) -> str:
        inside = m.group(1)
        if inside.endswith(png_name):
            return f"({target})"
        return m.group(0)

    txt = re.sub(rf"\(([^)\n]*?{name_re})\)", md_repl, txt)

    if txt != before:
        write_text(md_path, txt)
        return True
    return False


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="Move root-level PNGs to folders where they're referenced.")
    ap.add_argument("--vault", default=".", help="Obsidian vault root (default: .)")
    ap.add_argument("--apply", action="store_true", help="Actually move files and edit markdown (default: dry-run)")
    ap.add_argument("--report-dir", default="03-워크플로우자동화", help="Where to write the report markdown")
    ap.add_argument("--assets-dirname", default="_assets", help="Assets folder name to create under caller note dir")
    ap.add_argument(
        "--unreferenced-subdir",
        default="_unreferenced",
        help="Subfolder under root assets dir where unreferenced PNGs are moved",
    )
    args = ap.parse_args()

    root = Path(args.vault).resolve()
    report_dir = (root / args.report_dir).resolve()
    ensure_dir(report_dir)
    report_path = report_dir / f"루트_png_정리_리포트_{date.today().isoformat()}.md"

    root_pngs = sorted([p for p in root.glob("*.png") if p.is_file()])

    moved: list[tuple[Path, Path, list[Path]]] = []
    ambiguous: list[tuple[Path, list[Path]]] = []
    unreferenced: list[Path] = []
    unchanged_due_to_conflict: list[tuple[Path, Path]] = []
    md_updates: list[Path] = []

    for png in root_pngs:
        png_name = png.name
        refs = find_refs(root, png_name)
        ref_dirs = sorted({r.md_dir for r in refs})

        if not refs:
            # Move to root assets/_unreferenced to keep vault root clean, but keep it discoverable.
            unreferenced.append(png)
            dest_dir = root / args.assets_dirname / args.unreferenced_subdir
            dest = dest_dir / png_name
            ensure_dir(dest_dir)
            if args.apply:
                if dest.exists():
                    # If same content, drop source; else keep as ambiguous
                    try:
                        if sha256(dest) == sha256(png):
                            png.unlink()
                            unchanged_due_to_conflict.append((png, dest))
                        else:
                            ambiguous.append((png, []))
                    except OSError:
                        ambiguous.append((png, []))
                else:
                    shutil.move(str(png), str(dest))
            moved.append((png, dest, []))
            continue

        if len(ref_dirs) != 1:
            ambiguous.append((png, [r.md_path for r in refs]))
            continue

        caller_dir = ref_dirs[0]
        dest_dir = caller_dir / args.assets_dirname
        ensure_dir(dest_dir)
        dest = dest_dir / png_name

        # If file already exists, prefer keeping existing if identical.
        if dest.exists():
            try:
                if sha256(dest) == sha256(png):
                    if args.apply:
                        png.unlink()
                    unchanged_due_to_conflict.append((png, dest))
                else:
                    # Conflict with different content — do not move automatically.
                    ambiguous.append((png, [r.md_path for r in refs]))
                continue
            except OSError:
                ambiguous.append((png, [r.md_path for r in refs]))
                continue

        if args.apply:
            shutil.move(str(png), str(dest))
            # Update links (Obsidian wikilinks + markdown links)
            for r in refs:
                if update_md_links(r.md_path, png_name, dest):
                    md_updates.append(r.md_path)

        moved.append((png, dest, [r.md_path for r in refs]))

    # Write report
    lines: list[str] = []
    lines.append("# 루트 PNG 정리 리포트")
    lines.append("")
    lines.append(f"- **Vault**: `{root}`")
    lines.append(f"- **대상(루트 PNG)**: {len(root_pngs)}개")
    lines.append(f"- **실행 모드**: {'APPLY(이동/수정 실행)' if args.apply else 'DRY-RUN(분석만)'}")
    lines.append(f"- **Assets 폴더명**: `{args.assets_dirname}`")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## 1) 이동 대상(참조 폴더가 1곳으로 확정)")
    if moved:
        for src, dst, ref_mds in moved:
            # src may no longer exist after move; keep name only
            lines.append(f"- **{src.name}** → `{dst.relative_to(root)}`")
            for md in sorted(set(ref_mds)):
                lines.append(f"  - 참조: `{md.relative_to(root)}`")
    else:
        lines.append("- (없음)")
    lines.append("")

    lines.append("## 2) 애매함(여러 폴더/여러 문서에서 참조됨 → 자동 이동 보류)")
    if ambiguous:
        for png, ref_mds in ambiguous:
            lines.append(f"- **{png.name}**")
            for md in sorted(set(ref_mds)):
                lines.append(f"  - 참조: `{md.relative_to(root)}`")
    else:
        lines.append("- (없음)")
    lines.append("")

    lines.append("## 3) 미참조(어떤 문서에서도 호출되지 않음)")
    if unreferenced:
        for png in unreferenced:
            lines.append(f"- `{png.name}`")
    else:
        lines.append("- (없음)")
    lines.append("")

    lines.append("## 4) Markdown 링크 갱신(괄호 링크만)")
    if md_updates:
        for md in sorted(set(md_updates)):
            lines.append(f"- `{md.relative_to(root)}`")
    else:
        lines.append("- (변경 없음)")
    lines.append("")

    lines.append("## 5) 동일 파일 존재(내용 동일)로 소스만 제거")
    if unchanged_due_to_conflict:
        for src, dst in unchanged_due_to_conflict:
            lines.append(f"- `{src.name}`: 대상 `{dst.relative_to(root)}`와 동일 → 루트 파일 제거")
    else:
        lines.append("- (없음)")
    lines.append("")

    lines.append("## 6) 참고")
    lines.append("- Obsidian 위키링크(`![[...]]`, `[[...]]`)는 `...|alias`(별칭)이 있으면 별칭을 유지합니다.")
    lines.append("- 괄호 링크(`![](...)`, `[](...)`)는 URL이 `.../<파일명>.png`로 끝나는 경우만 상대경로로 갱신합니다.")
    lines.append("")

    write_text(report_path, "\n".join(lines).rstrip() + "\n")
    print(f"Wrote report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


