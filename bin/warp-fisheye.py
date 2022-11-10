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


""" blablab """

from math import pi
import argparse
from PIL import Image
import numpy as np
from os.path import splitext

parser = argparse.ArgumentParser(
                    prog='Warp-fisheye',
                    description='Dewarp a fisheye lens'
                    )

parser.add_argument('filename')
parser.add_argument('--dsize', nargs=2, type=int, help="width height")
args = parser.parse_args()

im = Image.open(args.filename)
data = np.asarray(im)
(h, w, c) = data.shape

maxRadius = min(w, h) / 2
if args.dsize is None:
    dsize = (round(maxRadius * pi), round(maxRadius))
else:
    dsize = args.dsize

dwidth = dsize[0]
dheight = dsize[1]

center = (h / 2, w / 2)

print(f"Generating {dwidth}x{dheight} @ {center[1]}x{center[0]} with radius {maxRadius} panorama")  # noqa: E501

rho = np.linspace(0, maxRadius, dheight + 1, dtype=np.float32)
phi = np.linspace(0, -2 * pi, dwidth + 1, dtype=np.float32)

cp = np.cos(phi)
sp = np.sin(phi)

x = np.outer(rho, cp) + center[1]
y = np.outer(rho, sp) + center[0]

remap = np.dstack((y, x))

img = np.zeros((dheight, dwidth, 3), dtype=np.uint8)
for y in range(dheight):
    for x in range(dwidth):
        ny, nx = remap[y, x]
        img[y, x] = data[round(ny), round(nx)]

# show image
im2 = Image.fromarray(img)
im2.show()
name, ext = splitext(args.filename)
im2.save(f"{name}-panorama.ppm")
