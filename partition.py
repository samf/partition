#! /usr/bin/env python3

import argparse
import os.path
import shutil


def partition(max_size, source_dir, dest_dir):
    dcount = 0
    current_size = 0
    max_blocks = max_size << 11  # 1 for 512 to 1K, 10 more for K to M

    final_dir = dname(dest_dir, dcount)
    for fent in sorted(os.scandir(source_dir), key=lambda e: e.name):
        if current_size + fent.stat().st_blocks > max_blocks:
            current_size = 0
            dcount += 1
            final_dir = dname(dest_dir, dcount)

        src_file = os.path.join(source_dir, fent.name)
        shutil.copy2(src_file, final_dir)
        current_size += fent.stat().st_blocks


def dname(dest_dir, counter):
    ddir = os.path.join(dest_dir, f"{counter:03}")
    os.makedirs(ddir)
    return ddir


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


def main():
    args = cli.parse_args()
    partition(args.max_size, args.source_dir, args.dest_dir)


if __name__ == "__main__":
    main()
