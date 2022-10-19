#! /usr/bin/env python3

import argparse
import os.path
import shutil


class DestDir:
    dir_number = 0

    def __init__(self, parent_dir):
        DestDir.dir_number += 1
        self.name = f"{DestDir.dir_number:03}"
        self.parent_dir = parent_dir
        self.path = os.path.join(parent_dir, self.name)

        self.blocks = 0
        self.first = None
        self.last = None

        self.makedirs()

    def copy2(self, source_path, blocks):
        "copy source_path into this DestDir"
        name = os.path.basename(source_path)
        shutil.copy2(source_path, self.path)
        self.blocks += blocks
        if not self.first:
            self.first = name
        self.last = name

    def makedirs(self):
        os.makedirs(self.path)

    def rename(self):
        first = os.path.splitext(self.first)[0].replace("-", "_")
        last = os.path.splitext(self.last)[0].replace("-", "_")
        new_name = f"{first}-{last}"
        new_path = os.path.join(self.parent_dir, new_name)
        os.rename(self.path, new_path)


def partition(max_size, source_dir, dest_parent, rename):
    max_blocks = max_size << 11  # 1 for 512 to 1K, 10 more for K to M
    dest = DestDir(dest_parent)

    for fent in sorted(os.scandir(source_dir), key=lambda e: str.lower(e.name)):
        blocks = fent.stat().st_blocks
        if dest.blocks + blocks > max_blocks:
            if rename:
                dest.rename()
            dest = DestDir(dest_parent)

        src_file = os.path.join(source_dir, fent.name)
        dest.copy2(src_file, blocks)

    if rename:
        dest.rename()


def dir_path(dname):
    if os.path.isdir(dname):
        return dname
    raise argparse.ArgumentTypeError(f"{dname}: not a valid directory")


cli = argparse.ArgumentParser(description="split a directory into parts")
cli.add_argument("source_dir", type=dir_path)
cli.add_argument(
    "--dest-dir",
    "-d",
    type=dir_path,
    default=".",
    help="directory to put the parts into",
)
cli.add_argument(
    "--max-size",
    "-m",
    type=int,
    default="23",
    help="maximum size of each subdir in megabytes",
)
cli.add_argument(
    "--rename-dirs",
    "-r",
    type=bool,
    action=argparse.BooleanOptionalAction,
    help="rename created dirs based on file names within",
)


def main():
    args = cli.parse_args()
    partition(args.max_size, args.source_dir, args.dest_dir, args.rename_dirs)


if __name__ == "__main__":
    main()
