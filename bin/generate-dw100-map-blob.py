#! /usr/bin/env python3

# Copyright 2022 NXP
#
# SPDX-License-Identifier: BSD-3-Clause
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# Neither the name of the NXP Semiconductors nor the names of its
# contributors may be used to endorse or promote products derived from this
# software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import numpy as np
import cv2 as cv
from argparse import ArgumentParser, ArgumentError


USECASES = [
        'identity',
        'distortion',
        'fisheye-distortion',
        'stereo'
    ]


def min(a, b):
    return a if a < b else b


def max(a, b):
    return a if a > b else b


def generateDW100Map(sw, sh, dw, dh, mapFull=None):
    DW100_BLOCK_SIZE = 16

    def dw_get_n_vertices_from_length(length):
        n = length // DW100_BLOCK_SIZE + 1
        if (length % DW100_BLOCK_SIZE):
            n += 1

        return n

    def dw_map_convert_to_UQ12_4(a):
        return int((a * (1 << 4)))

    def dw_map_format_coordinates(x, y):
        xq = dw_map_convert_to_UQ12_4(x)
        yq = dw_map_convert_to_UQ12_4(y)

        return (yq << 16) + xq

    mw = dw_get_n_vertices_from_length(dw)
    mh = dw_get_n_vertices_from_length(dh)

    dx = sw // (mw - 1)
    dy = sh // (mh - 1)

    def dw_get_texture_coordinate(vx, vy):
        if mapFull is not None:
            r = min(vy * DW100_BLOCK_SIZE, dh - 1)
            c = min(vx * DW100_BLOCK_SIZE, dw - 1)
            x, y = mapFull[r][c]
            x, y = sw * x / dw, sh * y / dh
        else:
            x = vx * dx
            y = vy * dy

        if args.vflip:
            x = sw - x

        if args.hflip:
            y = sh - y

        return max(0, min(x, sw)), max(0, min(y, sh))

    mapping = []
    for i in range(mh):
        for j in range(mw):
            mapping.append(
                dw_map_format_coordinates(
                    *dw_get_texture_coordinate(j, i)
                    )
                )
    return mapping


def writeMapToFile(mapping, filename):
    from struct import pack
    with open(filename, 'wb') as f:
        for d in mapping:
            f.write(pack("I", d))


def writeMapToYaml(mapping, filename):
    from yaml import dump
    with open(filename, 'w') as f:
        dump(mapping, f, default_flow_style=True)


parser = ArgumentParser(description="Generate dewarper map for dw100 device")

parser.add_argument(
    "--sourceResolution",
    help="Source image resolution",
    type=int,
    nargs=2,
    metavar=('width', 'height'),
    default=[640, 480],
)

parser.add_argument(
    "--destinationResolution",
    help="Destination image resolution",
    type=int,
    nargs=2,
    metavar=('width', 'height'),
    default=[640, 480],
)

parser.add_argument(
    "--yaml",
    help="Write mapping table to yaml file",
    action='store_true'
)

parser.add_argument(
    "--hflip",
    help="Enable horizontal flip",
    action='store_true'
)

parser.add_argument(
    "--vflip",
    help="Enable vertical flip",
    action='store_true'
)

parser.add_argument(
    "--outputFile",
    help="Output file basename",
    )

parser.add_argument(
    "usecase",
    help="Camera usecase",
    choices=USECASES,
)

calArgs = parser.add_argument(
    "calibrationFile",
    help="Camera calibration file",
    nargs='?',
    type=str,
)

args = parser.parse_args()

sw = args.sourceResolution[0]
sh = args.sourceResolution[1]

dw = args.destinationResolution[0]
dh = args.destinationResolution[1]

cv_file = None
maps = []
mappings = []

if not args.calibrationFile and args.usecase != 'identity':
    raise ArgumentError(calArgs, f"Usecase {args.usecase} requires a calibration file")

cv_file = cv.FileStorage()
if args.calibrationFile:
    cv_file.open(args.calibrationFile, cv.FileStorage_READ)

if args.usecase == 'identity':
    pass
elif args.usecase == 'distortion':
    M = cv_file.getNode('M').mat()
    D = cv_file.getNode('D').mat()
    I = np.identity(3)  # noqa: E741
    map1, _ = cv.initUndistortRectifyMap(M, D, I, None, (dw, dh), cv.CV_32FC2)
    maps.append(map1)

elif args.usecase == 'stereo':
    M1 = cv_file.getNode('M1').mat()
    D1 = cv_file.getNode('D1').mat()
    P1 = cv_file.getNode('P1').mat()
    R1 = cv_file.getNode('R1').mat()
    map1, _ = cv.initUndistortRectifyMap(M1, D1, R1, P1, (dw, dh), cv.CV_32FC2)
    maps.append(map1)

    M2 = cv_file.getNode('M2').mat()
    D2 = cv_file.getNode('D2').mat()
    P2 = cv_file.getNode('P2').mat()
    R2 = cv_file.getNode('R2').mat()
    map2, _ = cv.initUndistortRectifyMap(M2, D2, R2, P2, (dw, dh), cv.CV_32FC2)
    maps.append(map2)

elif args.usecase == 'fisheye-distortion':
    D = cv_file.getNode('D').mat()
    M = cv_file.getNode('M').mat()
    I = np.identity(3)  # noqa: E741
    mapx, mapy = cv.fisheye.initUndistortRectifyMap(M, D, I, M, (dw, dh),
                                                    cv.CV_32FC1)
    map_ = np.dstack((mapx, mapy))
    maps.append(map_)

else:
    raise RuntimeError("Invalid usecase")


for mapFull in maps:
    mappings.append(generateDW100Map(sw, sh, dw, dh, mapFull=mapFull))

if not mappings:
    mappings.append(generateDW100Map(sw, sh, dw, dh))

for idx, mapping in enumerate(mappings):
    outFile = "map-dw100"
    if args.outputFile is not None:
        outFile = args.outputFile

    if len(mappings) > 1:
        outFile += f"-{idx}"

    outFile += f"-{sw}x{sh}_{dw}x{dh}"

    writeMapToFile(mapping, f"{outFile}.bin")
    print(f"{args.usecase} mapping ({sw}x{sh}->{dw}x{dh}) written to {outFile}")  # noqa E501

    if args.yaml:
        mappingDict = {}
        mappingDict["input-resolution"] = [sw, sh]
        mappingDict["output-resolution"] = [dw, dh]
        mappingDict["mapping"] = mapping
        writeMapToYaml(mappingDict, f"{outFile}.yaml")
