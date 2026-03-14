#!/usr/bin/env nix-shell
#! nix-shell -i python3 -p python3Packages.tqdm
from pathlib import Path
from dataclasses import dataclass
from argparse import ArgumentParser
from collections import defaultdict
from urllib.request import urlopen
from tempfile import mkdtemp
from subprocess import run, PIPE
from sys import stderr, stdout
from shutil import rmtree, copy
from tqdm import tqdm

parser = ArgumentParser()
parser.add_argument('-i,--input', dest="input", type=Path, default="man.txt")
parser.add_argument('-o,--output', dest="output", type=Path, default=f"{Path(__file__).parent / 'data'}")

args = parser.parse_args()


@dataclass
class Item():
    name: str
    size: int
    path: str
    nar_hash: str


def report_error(e: Exception, context: str = ""):
    """Centralized error reporting function."""
    import traceback
    print(f"ERROR: {context}", file=stderr)
    traceback.print_exception(type(e), e, e.__traceback__, file=stderr)


def parse_manifest_lines(input_file: Path) -> tuple[dict, int]:
    print("Fetching manuals available by using nix-index", file=stderr)
    item_amount = 0
    items_by_hash = defaultdict(list)
    with input_file.open('r') as f:
        for line in f:
            try:
                parts = [x for x in line.strip().split(' ') if len(x) > 0]
                if len(parts) < 3:
                    continue
                name, size_str, kind = parts[0], parts[1], parts[2]
                path_parts = parts[3:]
                path = " ".join(path_parts)
                norm_path = "/".join(path.split('/')[4:])
                size = int(size_str.replace(',', ''))
                if kind != 'r':
                    continue
                nar_hash = path.split('/')[3].split('-')[0]
                item = Item(name=name, size=size, path=norm_path, nar_hash=nar_hash)
                items_by_hash[nar_hash].append(item)
                item_amount += 1
            except ValueError as e:
                report_error(e, f"Failed to parse line: {line.strip()}")
            except IndexError as e:
                report_error(e, f"Malformed line: {line.strip()}")
    return items_by_hash, item_amount

def dump_manifest_metadata(items_by_hash: dict, output_file: Path, ops: tqdm):
    ops.set_description("Dumping metadata to a json manifest")
    from json import dump
    obj = []
    for nar_hash, items in items_by_hash.items():
        for item in items:
            obj.append(dict(
                man="/".join(item.path.split('/')[-2:]),
                name=item.name,
                path="/".join(item.path.split('/')[0:5]),
                size=item.size
            ))
    with output_file.open('w') as f:
        dump(obj, f)

def fetch_and_extract_nars(items_by_hash: dict, out_by_hash_dir: Path, ops: tqdm):
    for drv_hash, v in items_by_hash.items():
        ops.set_description(f"Fetching {drv_hash}")
        folder_with_hash = out_by_hash_dir / drv_hash
        if not folder_with_hash.exists():
            try:
                narinfo = urlopen(f"https://cache.nixos.org/{drv_hash}.narinfo")
                nar_url = [ x.split(":")[1].strip() for x in narinfo.read().decode('utf-8').split('\n') if x.startswith("URL:") ]
                if len(nar_url) != 1:
                    continue
                nar_url = f"https://cache.nixos.org/{nar_url[0]}"
                tempdir = Path(mkdtemp())
                tempfile_download = tempdir / f"{nar_url.split('/')[-1]}"

                with tempfile_download.open('wb') as f:
                    ops.set_description(f"Downloading '{nar_url}'")
                    res = urlopen(nar_url)
                    CHUNK_SIZE = 128 * 1024
                    while True:
                        data = res.read(CHUNK_SIZE)
                        if not data:
                            break
                        stderr.write(".")
                        stderr.flush()
                        f.write(data)
                    stderr.write("\n")
                ops.set_description(f"Extracting '{tempfile_download}' with xz")
                run(['xz', '-d', str(tempfile_download)], stderr=stderr, stdout=stdout, check=True)
                for item in v:
                    folder_with_hash.mkdir(exist_ok=True, parents=True)
                    man_name = item.path.split('/')[-1]
                    man_file_name = folder_with_hash / man_name
                    tempfile_extracted = str(tempfile_download).replace('.xz', '')
                    ops.set_description(f"Extracting '{item.path}' from '{tempfile_extracted}'")
                    run(f"nix nar cat '{str(tempfile_extracted)}' '/{item.path}' > '{str(man_file_name.resolve())}'", shell=True, stderr=stderr, stdout=stdout, check=True)
                    ops.update(1)
            except Exception as e:
                report_error(e, f"Failed to fetch/extract nar for {drv_hash}")
            finally:
                if 'tempdir' in locals() and tempdir.exists():
                    rmtree(str(tempdir))
        else:
            ops.update(len(v))

def main():
    items_by_hash, item_amount = parse_manifest_lines(args.input)

    ops = tqdm(total=item_amount)

    out_by_hash_dir = args.output / "by-hash"
    out_by_hash_dir.mkdir(exist_ok=True, parents=True)

    manifest_file = args.output / "man2prog.json"
    dump_manifest_metadata(items_by_hash, manifest_file, ops)

    fetch_and_extract_nars(items_by_hash, out_by_hash_dir, ops)

if __name__ == '__main__':
    main()

