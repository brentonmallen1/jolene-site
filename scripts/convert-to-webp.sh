#!/usr/bin/env bash
#
# convert-to-webp.sh - Batch convert images in a directory to WebP.
#
# Usage:
#   ./convert-to-webp.sh <input_dir> <output_dir> [quality]
#
#   quality: 0-100 (default 80). Higher = better quality, larger file.
#
# Requires: cwebp (brew install webp)

set -euo pipefail

INPUT_DIR="${1:-}"
OUTPUT_DIR="${2:-}"
QUALITY="${3:-80}"

if [[ -z "$INPUT_DIR" || -z "$OUTPUT_DIR" ]]; then
  echo "Usage: $0 <input_dir> <output_dir> [quality=80]" >&2
  exit 1
fi

if ! command -v cwebp >/dev/null 2>&1; then
  echo "Error: cwebp not found. Install it with: brew install webp" >&2
  exit 1
fi

if [[ ! -d "$INPUT_DIR" ]]; then
  echo "Error: input directory '$INPUT_DIR' does not exist" >&2
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

# Supported source extensions (cwebp natively reads these)
EXTENSIONS=("jpg" "jpeg" "png" "tif" "tiff")

count=0
skipped=0
total_in=0
total_out=0

echo "Converting images from '$INPUT_DIR' to '$OUTPUT_DIR' (quality=$QUALITY)..."

while IFS= read -r -d '' file; do
  # Path of the file relative to INPUT_DIR, so subdirectory structure is preserved
  rel_path="${file#"$INPUT_DIR"/}"
  rel_dir="$(dirname "$rel_path")"
  base_name="$(basename "$rel_path")"
  name_no_ext="${base_name%.*}"

  dest_dir="$OUTPUT_DIR"
  if [[ "$rel_dir" != "." ]]; then
    dest_dir="$OUTPUT_DIR/$rel_dir"
    mkdir -p "$dest_dir"
  fi

  dest_file="$dest_dir/$name_no_ext.webp"

  if cwebp -quiet -q "$QUALITY" "$file" -o "$dest_file"; then
    in_size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file")
    out_size=$(stat -f%z "$dest_file" 2>/dev/null || stat -c%s "$dest_file")
    total_in=$((total_in + in_size))
    total_out=$((total_out + out_size))
    count=$((count + 1))
    echo "  ✓ $rel_path -> ${dest_file#"$OUTPUT_DIR"/} ($((in_size / 1024))KB -> $((out_size / 1024))KB)"
  else
    echo "  ✗ Failed to convert: $rel_path" >&2
    skipped=$((skipped + 1))
  fi
done < <(find "$INPUT_DIR" -type f \( \
    -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.tif" -o -iname "*.tiff" \
  \) -print0)

echo ""
echo "Done. Converted: $count, Skipped/failed: $skipped"
if [[ $total_in -gt 0 ]]; then
  saved_pct=$(( (total_in - total_out) * 100 / total_in ))
  echo "Total size: $((total_in / 1024))KB -> $((total_out / 1024))KB (${saved_pct}% reduction)"
fi
