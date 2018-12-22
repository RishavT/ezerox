#!/bin/bash
# Downloads an image from IP Camera and then edits it.
# Can also print if required.

source libstacktrace || true
set -e -u -E

URL="http://172.20.10.2:8080/photoaf.jpg"
ORIG_DIR=$(pwd)
TMPDIR="$(mktemp -d)"

cd $TMPDIR

# Download image (take snapshow)
wget $URL

# Edit the image
$ORIG_DIR/edit_image.sh ./photoaf.jpg ./scanned.jpg $@

# Copy to Downloads
cp ./scanned.jpg $HOME/Downloads/scanned.jpg

# Clean up
rm photoaf.jpg scanned.jpg
cd "$ORIG_DIR"
rmdir "$TMPDIR"

# Open in preview
open $HOME/Downloads/scanned.jpg

