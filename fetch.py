#!/usr/bin/env python3
from pathlib import Path
from dataclasses import dataclass
from argparse import ArgumentParser
from collections import defaultdict

parser = ArgumentParser()
parser.add_argument('input', type=Path, default="man.txt")

args = parser.parse_args()

items_by_hash = defaultdict(lambda: [])

@dataclass
class Item():
    name: str
    size: int
    path: str
    nar_hash: str

f = open(str(args.input), 'r')

for line in f:
    try:
        [name, size, _, *path] = [x for x in line.strip().split(' ') if len(x) > 0]
        path = "/".join(" ".join(path).split('/')[4:])
        size = int(size.replace(',', ''))
        nar_hash = path.split('/')[3].split('-')[0]
        item = Item(name=name, size=size, path=path, nar_hash=nar_hash)
        print(item)
        exit(0)
        items_by_hash[nar_hash].append(item)
    except ValueError as e:
        print(e, line)

print(len(items_by_hash))
