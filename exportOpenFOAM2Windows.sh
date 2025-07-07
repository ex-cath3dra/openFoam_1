#!/bin/bash

# --------- USAGE ----------
# ./exportToWindows.sh mycase             -> uses ./mycase and exports to default Windows folder
# ./exportToWindows.sh mycase /mnt/c/Users/You/Documents/CustomCase -> custom source & target

# --------- INPUTS ----------
SRC_RELATIVE="$1"
DST_CUSTOM="$2"

# --------- VALIDATION ----------
if [ -z "$SRC_RELATIVE" ]; then
    echo "[ERROR] No source case folder given."
    echo "Usage: $0 <source-relative-path> [destination-path]"
    exit 1
fi

# --------- PATHS ----------
SRC_ABS="$(realpath "$SRC_RELATIVE")"
CASE_NAME="$(basename "$SRC_ABS")"

if [ -z "$DST_CUSTOM" ]; then
    DST_ABS="/mnt/c/Users/rafra/Documents/Projects/CAE_Projects/outSync/$CASE_NAME"
else
    # Original was on the idea that I would give a lot of the path...
    # DST_ABS="$(realpath "$DST_CUSTOM")"
    DST_ABS="/mnt/c/Users/rafra/Documents/Projects/CAE_Projects/outSync/$DST_CUSTOM"
fi

# --------- LOG ----------
echo "[INFO] Source folder:      $SRC_ABS"
echo "[INFO] Destination folder: $DST_ABS"

# --------- PREPARE ---------
mkdir -p "$DST_ABS"

# Add .OpenFOAM pointer if missing
OPENFOAM_FILE="$SRC_ABS/$CASE_NAME.OpenFOAM"
if [ ! -f "$OPENFOAM_FILE" ]; then
    echo "[INFO] Creating pointer file: $CASE_NAME.OpenFOAM"
    touch "$OPENFOAM_FILE"
fi

# --------- SYNC ---------
echo "[INFO] Syncing case with rsync..."
rsync -avh --delete "$SRC_ABS/" "$DST_ABS/"

echo "[DONE] Case exported successfully."
echo "       Open '$CASE_NAME.OpenFOAM' in ParaView from: $DST_ABS"

