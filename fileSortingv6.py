import argparse
import logging
import os
import re
import shutil
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    handlers=[logging.StreamHandler()]
)

NAMES_FILE = Path(__file__).resolve().parent / "pornstars.txt"
PMV = "Pmv Compilation"  # always checked first
VALID_EXTS = {'.mp4', '.avi', '.mkv', '.icloud', '.wmv', '.m4v', '.mov', '.webm'}


def normalize(text: str) -> str:
    """Lowercase, turn every run of non-alphanumerics (. - _ + , & ( ) ...) into one space."""
    return ' '.join(re.sub(r'[\W_]+', ' ', text.lower()).split())


def load_and_prepare_names(path: Path, pmv: str, write: bool = True) -> list[str]:
    """Read names, title-case, de-duplicate, sort with pmv first; rewrite the file only if that changed it."""
    if not path.exists():
        raise FileNotFoundError(f"Names file not found: {path}")

    original = path.read_text(encoding='utf-8')
    names = sorted({line.strip().title() for line in original.splitlines() if line.strip()} - {pmv})
    names.insert(0, pmv)

    cleaned = '\n'.join(names) + '\n'
    if write and cleaned != original:
        path.write_text(cleaned, encoding='utf-8')
        logging.info(f"Cleaned up {path.name} ({len(names)} names).")
    return names


def build_matchers(person_names: list[str]) -> list[tuple[str, re.Pattern]]:
    """One whole-word pattern per name, in priority order (pmv first, then alphabetical).
    Whole-word means 'Ai' no longer matches inside 'maid' or 'Kincaid'."""
    return [(name, re.compile(rf'(?<!\w){re.escape(normalize(name))}(?!\w)'))
            for name in person_names if normalize(name)]


def match_person(matchers: list[tuple[str, re.Pattern]], filename: Path) -> str | None:
    text = normalize(filename.stem)
    return next((name for name, pattern in matchers if pattern.search(text)), None)


def move_into_place(src: Path, dest: Path):
    """Move src to dest, replacing dest in a single step so a failure never loses both files."""
    try:
        os.replace(src, dest)
    except OSError:  # different drive: copy next to dest first, then swap
        tmp = dest.with_name(f".{dest.name}.partial")
        shutil.move(src, tmp)
        os.replace(tmp, dest)


def file_sorting(matchers: list[tuple[str, re.Pattern]], dst_path: Path, filename: Path, dry_run: bool = False) -> bool:
    """Sort a single file into a person's directory. Returns True if it was moved or removed as a duplicate."""
    if filename.name.startswith('._') or filename.suffix.lower() not in VALID_EXTS:
        return False  # macOS metadata stubs (._name.mp4) or non-video files

    person = match_person(matchers, filename)
    if person is None:
        return False

    person_dir = dst_path / person
    dest = person_dir / filename.name
    src = filename

    if dest.exists():
        src_size, dest_size = src.stat().st_size, dest.stat().st_size
        if src_size > dest_size:
            action = f"Replaced {person}/{dest.name} with larger file ({src_size} > {dest_size} bytes)."
            if not dry_run:
                move_into_place(src, dest)
        else:
            kind = "smaller" if src_size < dest_size else "equal-size"
            action = f"Deleted {kind} duplicate {src.name} (kept {person}/{dest.name})."
            if not dry_run:
                src.unlink()
    else:
        action = f"Moved {filename.name} → {person}/"
        if not dry_run:
            person_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(src, dest)

    logging.info(("[dry run] " if dry_run else "") + action)
    return True


def process_directory(src_path: Path, dst_path: Path, person_names: list[str], dry_run: bool = False):
    """Walk source directory and sort files; one bad file doesn't stop the rest."""
    logging.info(f"Scanning {src_path} → {dst_path}")
    matchers = build_matchers(person_names)
    scanned = sorted_count = errors = 0
    unmatched = []

    for root, dirs, files in os.walk(src_path):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for name in files:
            file_path = Path(root) / name
            scanned += 1
            try:
                if file_sorting(matchers, dst_path, file_path, dry_run):
                    sorted_count += 1
                elif file_path.suffix.lower() in VALID_EXTS and not name.startswith('._'):
                    unmatched.append(name)
            except Exception as e:
                errors += 1
                logging.error(f"{name}: {e}")

    for name in unmatched:
        logging.info(f"No name match, left in place: {name}")
    logging.info(f"Scanned {scanned} files: sorted={sorted_count} unmatched={len(unmatched)} errors={errors}")


def get_default_paths() -> tuple[Path, Path]:
    """Return default source and destination paths for the current platform."""
    if os.name == 'nt':
        return Path(r"D:\7_XYZ\_TO_BE_CAT"), Path(r"D:\7_XYZ")
    return Path("/mnt/d/7_XYZ/_TO_BE_CAT"), Path("/mnt/d/7_XYZ")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('-usedefaults', '--usedefaults', action='store_true',
                        help='Use the platform-specific default paths without prompting.')
    parser.add_argument('--src', type=Path, help='Folder to sort (no prompt).')
    parser.add_argument('--dst', type=Path, help='Folder holding the person folders (no prompt).')
    parser.add_argument('--dry-run', action='store_true', help='Show what would happen without moving anything.')
    args = parser.parse_args(argv)

    default_src, default_dst = get_default_paths()
    if args.usedefaults or args.src or args.dst:
        src_path = args.src or default_src
        dst_path = args.dst or default_dst
    else:
        src_input = input(f"Enter source directory (default: {default_src}): ").strip()
        src_path = Path(src_input) if src_input else default_src
        dst_input = input(f"Enter destination directory (default: {default_dst}): ").strip()
        dst_path = Path(dst_input) if dst_input else default_dst

    for label, path in (("Source", src_path), ("Destination", dst_path), ("Names file", NAMES_FILE)):
        if not path.exists():
            logging.error(f"{label} does not exist: {path}")
            return 1

    person_names = load_and_prepare_names(NAMES_FILE, PMV, write=not args.dry_run)
    process_directory(src_path, dst_path, person_names, args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
