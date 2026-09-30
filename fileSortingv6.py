import argparse
import os
import shutil
import logging
from pathlib import Path
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    handlers=[logging.StreamHandler()]
)

def load_and_prepare_names(filepath: str, pmv: str) -> list[str]:
    """Read names, clean them, sort, ensure pmv is first, and save back."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Names file not found: {filepath}")

    names = []
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            cleaned = line.strip().title()
            if cleaned:  # Skip empty lines
                names.append(cleaned)

    names.sort()
    names = [n for n in names if n != pmv]
    names.insert(0, pmv)

    # Safely overwrite the file
    with path.open('w', encoding='utf-8') as f:
        f.write('\n'.join(names) + '\n')

    return names

def file_sorting(person_names: list[str], src_path: Path, dst_path: Path, filename: Path) -> bool:
    """Sort a single file into a person's directory. Returns True if moved."""
    ext = filename.suffix.lower()
    valid_exts = {'.mp4', '.avi', '.mkv', '.icloud', '.wmv' ,'.m4v'}
    if ext not in valid_exts:
        return False

    # Simplify filename stem for matching
    name_part = filename.stem
    simplified = re.sub(r'[.\-_+]', ' ', name_part).lower()

    for person in person_names:
        if person.lower() in simplified:
            person_dir = dst_path / person
            person_dir.mkdir(parents=True, exist_ok=True)

            dest = person_dir / filename.name
            src = filename  # filename is already the full path

            if dest.exists():
                src_size = src.stat().st_size
                dest_size = dest.stat().st_size

                if src_size > dest_size:
                    dest.unlink()
                    shutil.move(src, dest)
                    logging.info(f"Replaced {dest.name} with larger file ({src_size} bytes).")
                elif src_size < dest_size:
                    src.unlink()
                    logging.info(f"Deleted smaller duplicate {src.name} ({src_size} bytes).")
                else:
                    src.unlink()
                    logging.info(f"Deleted duplicate {src.name} with equal size.")
                return True

            shutil.move(src, dest)
            logging.info(f"Moved {filename.name} → {person}/")
            return True  # Successfully moved
    return False

def process_directory(src_path: Path, dst_path: Path, person_names: list[str]):
    """Walk source directory and sort files."""
    logging.info(f"\n{'='*60}")
    logging.info(f"Scanning source directory: {src_path}")
    logging.info(f"{'='*60}")

    file_count = 0
    for root, _, files in os.walk(src_path):
        for filename in files:
            file_count += 1
            file_path = Path(root) / filename
            logging.info(f"Processing: {file_path}")
            file_sorting(person_names, Path(root), dst_path, file_path)

    logging.info(f"\nTotal files scanned: {file_count}")
    logging.info(f"{'='*60}\n")

def get_default_paths() -> tuple[Path, Path]:
    """Return default source and destination paths for the current platform."""
    if os.name == 'nt':
        return Path(r"E:\7_XYZ\_TO_BE_CAT"), Path(r"E:\7_XYZ")

    return Path("/mnt/e/7_XYZ/_TO_BE_CAT"), Path("/mnt/e/7_XYZ")

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-usedefaults',
        '--usedefaults',
        action='store_true',
        help='Use the platform-specific default paths without prompting.'
    )
    args = parser.parse_args(argv)

    default_src, default_dst = get_default_paths()

    names_file = Path("/mnt/c/Users/rafavcc/iCloudDrive/Programming/projects/fileSorting") / "pornstars.txt"
    pmv = "Pmv Compilation"

    if args.usedefaults:
        src_path = default_src
        dst_path = default_dst
    else:
        src_input = input(f"Enter source directory (default: {default_src}): ").strip()
        src_path = Path(src_input) if src_input else default_src

        dst_input = input(f"Enter destination directory (default: {default_dst}): ").strip()
        dst_path = Path(dst_input) if dst_input else default_dst

    if not src_path.exists():
        logging.error(f"Source path does not exist: {src_path}")
        return
    if not dst_path.exists():
        logging.error(f"Destination path does not exist: {dst_path}")
        return
    if not names_file.exists():
        logging.error(f"Names file not found: {names_file}")
        return

    try:
        person_names = load_and_prepare_names(names_file, pmv)
        process_directory(src_path, dst_path, person_names)
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
