#!/usr/bin/env bash
# -*- mode: sh; coding: us-ascii-unix -*-

source libstacktrace || true
set -e -u -E

MANUAL="
Usage: $0 INFILE OUTFILE

Takes a document scan INFILE (an image) and produces a monochromatized
output file version.

"

if [[ "${1:-}" = "-?" ]] || [[ "${1:-}" = "-h" ]] || [[ "${1:-}" = "--help" ]]; then 
    echo "$MANUAL"
    exit 0
fi

BLURRADIUS="20"
INFILE="$(greadlink -m "$1")"
OUTFILE="$(greadlink -m "$2")"
TMPDIR="$(mktemp -d)"
ORIG_DIR=$(dirname $0)
CROPPER_PATH="python $ORIG_DIR/document-scanner/scanner.py"
cd "$TMPDIR"

touch cropped1.jpg
# First crop the image
# convert -crop 2979x2184+822+45 $INFILE cropped1.jpg
# convert $INFILE -resize 20% resized1.jpg
cp $INFILE resized1.jpg 
$CROPPER_PATH resized1.jpg cropped2.jpg
# cp $INFILE cropped.jpg

convert cropped2.jpg -colorspace Gray 01.png
cp 01.png 03.tif
touch 02.tif

convert 01.png -blur "${BLURRADIUS}x${BLURRADIUS}" 02.tif
convert 01.png 02.tif -compose Divide_Src -composite 03.tif 
cp 01.png 02.tif 03.tif ~/temp
# convert 03.tif -threshold 90% -type bilevel -compress group4 "$OUTFILE"
# convert 03.tif $OUTFILE

if [ "${@: -1}" = "highcontrast" ]
then
  convert 03.tif -threshold 90% -type bilevel "$OUTFILE"
else
  convert 03.tif $OUTFILE
fi

# rm 01.png 02.tif 03.tif cropped1.jpg cropped2.jpg
open "$TMPDIR"
