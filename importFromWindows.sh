#!/bin/bash

# -------- CONFIG --------
# Hardcoded Windows base path (adjust this!)
WIN_BASE="/mnt/c/Users/rafra/Documents/Projects/CAE_Projects"
LINUX_BASE="$HOME/CFD"

# -------- INPUT ARGUMENTS --------
SRC_REL="$1"   # Relative to WIN_BASE
DST_REL="$2"   # Relative to LINUX_BASE

# -------- VALIDATION --------
if [[ -z "$SRC_REL" ]]; then
  echo "[ERROR] No source path provided."
  echo "Usage: $0 <relative-windows-path> <relative-linux-destination>"
  echo "Example: $0 pump_v3.unv projects/pump-test01/constant/triSurface"
  exit 1
fi

if [[ -z "$DST_REL" ]]; then
  echo "[ERROR] No destination path provided."
  echo "Usage: $0 <relative-windows-path> <relative-linux-destination>"
  exit 1
fi

# -------- RESOLVE FULL PATHS --------
SRC_PATH="$WIN_BASE/$SRC_REL"
DST_PATH="$(realpath "$DST_REL")"

# -------- CHECK SOURCE --------
if [[ ! -e "$SRC_PATH" ]]; then
  echo "[ERROR] Source does not exist: $SRC_PATH"
  exit 1
fi

# -------- CREATE DESTINATION --------
mkdir -p "$DST_PATH"

# -------- COPY --------
echo "[INFO] Importing from: $SRC_PATH"
echo "[INFO] To:             $DST_PATH"

# If source is file, copy it directly
if [[ -f "$SRC_PATH" ]]; then
  cp -v "$SRC_PATH" "$DST_PATH/"
else
  # Source is a directory
  rsync -avh "$SRC_PATH/" "$DST_PATH/"
fi

echo "[DONE] Imported successfully."
