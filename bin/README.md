# dw100

[generate-dw100-map-blob.py](./generate-dw100-map-blob.py) generates dw100
dewarping map table intented to be used with dedicated dw100 linux kernel m2m
driver.

```console
[foo@bar vtec-cv]$ bin/generate-dw100-map-blob.py --help
usage: generate-dw100-map-blob.py [-h] [--sourceResolution width height] [--destinationResolution width height] [--hflip] [--vflip] [--calibrationFile CALIBRATIONFILE]
                                  [--stereoCalibrationFile STEREOCALIBRATIONFILE] [--outputFile OUTPUTFILE]

Generate dewarper map for dw100 device

options:
  -h, --help            show this help message and exit
  --sourceResolution width height
                        Source image resolution
  --destinationResolution width height
                        Destination image resolution
  --hflip               Enable horizontal flip
  --vflip               Enable vertical flip
  --calibrationFile CALIBRATIONFILE
                        Camera calibration file
  --stereoCalibrationFile STEREOCALIBRATIONFILE
                        Stereo camera calibration file
  --outputFile OUTPUTFILE
                        Output file basename
```

The script can generate identity map, with or without hflip/vflip mirroring
which can be combined.

```console
[foo@bar vtec-cv]$ bin/generate-dw100-map-blob.py  --hflip --vflip
Identity mapping (640x480->640x480) written to map-dw100-640x480_640x480.bin
```

The script can generate dewarping map to correct lens distorsion.
The calibration file should hold the intrinsic camera parameters and the lens
distorsion coefficients as M and D entries.

Those parameters are estimated during the [optical system calibration process](https://docs.opencv.org/4.5.5/dc/dbb/tutorial_py_calibration.html),
and are saved in a [openCV storage file](https://docs.opencv.org/4.5.5/da/d56/classcv_1_1FileStorage.html#details).

```console
[foo@bar vtec-cv]$ bin/generate-dw100-map-blob.py  \
                --calibrationFile camera-ACME.xml
Dewarping mapping (640x480->640x480) written to map-dw100-640x480_640x480.bin
```

The script can generate rectification and dewarping maps of a stereo vision
camera system thanks to parameters (M1, M2, D1, D2, P1, P2, R1, R2) returned by
[openCV stereoRectify](https://docs.opencv.org/4.5.5/d9/d0c/group__calib3d.html#ga617b1685d4059c6040827800e72ad2b6)

```console
[foo@bar vtec-cv]$ bin/generate-dw100-map-blob.py  \
                --stereoCalibrationFile camera-ACME-stereo.xml
Stereo rectification mapping (640x480->640x480) written to map-dw100-0-640x480_640x480.bin
Stereo rectification mapping (640x480->640x480) written to map-dw100-1-640x480_640x480.bin
```
