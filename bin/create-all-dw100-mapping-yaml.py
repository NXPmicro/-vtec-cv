#! /usr/bin/env python3

import yaml
from argparse import ArgumentParser, FileType

parser = ArgumentParser(
        description="Generate dewarper maps from individual mappings files"
    )

parser.add_argument(
    "inputFiles",
    help="Input mapping files",
    type=FileType('r'),
    nargs='+',
)

parser.add_argument(
    "--outputFile",
    help="Output file basename",
    default="Mappings"
    )


args = parser.parse_args()

mappings = []

for f in args.inputFiles:
    mappings.append(yaml.safe_load(f.read()))

doc = {}
doc['version'] = 1
doc['mappings'] = mappings

with open(f"{args.outputFile}.yaml", "w") as f:
    yaml.dump(doc, f, default_flow_style=True)
