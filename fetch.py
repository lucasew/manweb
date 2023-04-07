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


f = open(str(args.input), 'r')

print("Fetching manuals available by using nix-index", file=stderr)
item_amount = 0

items_by_hash = defaultdict(lambda: [])
for line in f:
    try:
        [name, size, kind, *path] = [x for x in line.strip().split(' ') if len(x) > 0]
        path = " ".join(path)
        norm_path = "/".join(path.split('/')[4:])
        size = int(size.replace(',', ''))
        if kind != 'r':
            continue
        nar_hash = path.split('/')[3].split('-')[0]
        item = Item(name=name, size=size, path=norm_path, nar_hash=nar_hash)
        items_by_hash[nar_hash].append(item)
        item_amount += 1
    except ValueError as e:
        print(e, line, file=stderr)

ops = tqdm(total=item_amount)

OUT_BY_HASH = args.output / "by-hash"
OUT_BY_HASH.mkdir(exist_ok=True, parents=True)

with (args.output / "man2prog.json").open('w') as f:
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
    dump(obj, f)


for drv_hash, v in items_by_hash.items():
    ops.set_description(f"Fetching {drv_hash}")
    folder_with_hash = OUT_BY_HASH / drv_hash
    if not folder_with_hash.exists(): # if the hash was not looked yet, download the nar and get the stuff
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
            while True:
                data = res.read(128*1024)
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
        rmtree(str(tempdir))
    ops.update(len(v))
    # then position the files in the man folder not keyed by hash

