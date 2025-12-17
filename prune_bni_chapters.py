import os
import re
from typing import Dict, List


def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "chapter"


def load_existing_slugs(*dirs: str) -> set[str]:
    existing: set[str] = set()
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if fn.endswith(".json"):
                existing.add(fn[:-5])
    return existing


def write_bni_chapters_py(chapters: List[Dict[str, str]]) -> None:
    lines = ["CHAPTERS = ["]
    for c in chapters:
        chap = c["chapter"].replace('"', '\\"')
        url = c["url"].replace('"', '\\"')
        lines.append(f'    {{"chapter": "{chap}", "url": "{url}"}},')
    lines.append("]")
    lines.append("")
    with open("bni_chapters.py", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main() -> None:
    import bni_chapters

    chapters = list(bni_chapters.CHAPTERS)
    existing = load_existing_slugs("output_bni", "output_bni_chapterdetails")

    remaining = [c for c in chapters if slugify(c["chapter"]) not in existing]
    write_bni_chapters_py(remaining)

    print(f"Total chapters in config: {len(chapters)}")
    print(f"Existing output slugs: {len(existing)}")
    print(f"Remaining chapters written to bni_chapters.py: {len(remaining)}")


if __name__ == "__main__":
    main()


