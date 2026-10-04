#!/usr/bin/env bash
# Recursively reports H.264 video metadata by bitrate, then encodes the top N as H.265 10-bit.
#
# Requirements: ffmpeg, ffprobe and jq
# Usage:
#   ./scanner_switches_v2.sh -dir /path/to/directory [-top 0] [-kbps 0] [-report report.tsv]
#
# Options may be passed in any order. With the default -top 0, the script scans
# and writes the report but does not encode any files.

set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 -dir DIRECTORY [-top NUMBER] [-kbps NUMBER] [-report FILE.tsv]

  -dir     Directory to scan recursively (required)
  -top     Number of highest-bitrate candidates to encode (default: 0)
  -kbps    Ignore files below this bitrate in kbps (default: 0)
  -report  TSV report path (default: h264_video_report_v2.tsv)
  -h, --help  Show this help
EOF
}

DIRECTORY=""
TOP_N=0
MIN_BITRATE_KBPS=0
REPORT="h264_video_report_v2.tsv"

while (( $# > 0 )); do
  case "$1" in
    -dir)
      (( $# >= 2 )) || { echo "Missing value after -dir." >&2; usage >&2; exit 2; }
      DIRECTORY="$2"
      shift 2
      ;;
    -top)
      (( $# >= 2 )) || { echo "Missing value after -top." >&2; usage >&2; exit 2; }
      TOP_N="$2"
      shift 2
      ;;
    -kbps)
      (( $# >= 2 )) || { echo "Missing value after -kbps." >&2; usage >&2; exit 2; }
      MIN_BITRATE_KBPS="$2"
      shift 2
      ;;
    -report)
      (( $# >= 2 )) || { echo "Missing value after -report." >&2; usage >&2; exit 2; }
      REPORT="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

[[ -n "$DIRECTORY" ]] || { echo "-dir is required." >&2; usage >&2; exit 2; }
[[ -d "$DIRECTORY" ]] || { echo "Not a directory: $DIRECTORY" >&2; exit 2; }
[[ "$TOP_N" =~ ^[0-9]+$ ]] || { echo "-top must be a non-negative integer." >&2; exit 2; }
[[ "$MIN_BITRATE_KBPS" =~ ^[0-9]+$ ]] || { echo "-kbps must be a non-negative integer." >&2; exit 2; }

MIN_BITRATE_BPS=$((MIN_BITRATE_KBPS * 1000))

# Restrict the scan to common video containers so image files are not probed.
EXTENSIONS=(
  -iname '*.mkv' -o -iname '*.avi' -o -iname '*.mp4' -o -iname '*.mpg'
  -o -iname '*.mpeg' -o -iname '*.ts' -o -iname '*.m2ts' -o -iname '*.vob'
  -o -iname '*.mov' -o -iname '*.wmv'
)

CANDIDATES=$(mktemp "${TMPDIR:-/tmp}/h264_candidates.XXXXXX")
trap 'rm -f "$CANDIDATES"' EXIT

# find is recursive by default: this includes DIRECTORY and all its subdirectories.
find "$DIRECTORY" -type f \( "${EXTENSIONS[@]}" \) -print0 |
while IFS= read -r -d '' file; do
  json=$(ffprobe -v error -select_streams v:0 \
    -show_entries 'stream=codec_name,profile,bit_rate,width,height,avg_frame_rate,r_frame_rate,pix_fmt,bits_per_raw_sample,color_primaries,color_transfer,color_space,field_order:format=bit_rate,duration,size' \
    -of json "$file" 2>/dev/null) || continue

  codec=$(jq -r '.streams[0].codec_name // empty' <<<"$json")
  [[ "$codec" == "h264" ]] || continue

  video_bitrate=$(jq -r '.streams[0].bit_rate // empty' <<<"$json")
  total_bitrate=$(jq -r '.format.bit_rate // empty' <<<"$json")
  profile=$(jq -r '.streams[0].profile // "?"' <<<"$json")
  width=$(jq -r '.streams[0].width // "?"' <<<"$json")
  height=$(jq -r '.streams[0].height // "?"' <<<"$json")
  frame_rate=$(jq -r '(.streams[0].avg_frame_rate // empty) as $avg | if $avg != "" and $avg != "0/0" then $avg else (.streams[0].r_frame_rate // "?") end' <<<"$json")
  pixel_format=$(jq -r '.streams[0].pix_fmt // "?"' <<<"$json")
  bit_depth=$(jq -r '.streams[0].bits_per_raw_sample // empty' <<<"$json")
  duration=$(jq -r '.format.duration // "?"' <<<"$json")
  size=$(jq -r '.format.size // "?"' <<<"$json")
  color_primaries=$(jq -r '.streams[0].color_primaries // "?"' <<<"$json")
  color_transfer=$(jq -r '.streams[0].color_transfer // "?"' <<<"$json")
  color_space=$(jq -r '.streams[0].color_space // "?"' <<<"$json")
  field_order=$(jq -r '.streams[0].field_order // "?"' <<<"$json")

  if [[ "$video_bitrate" =~ ^[0-9]+$ ]]; then
    bitrate="$video_bitrate"
    bitrate_source="video"
  elif [[ "$total_bitrate" =~ ^[0-9]+$ ]]; then
    bitrate="$total_bitrate"
    bitrate_source="container"
  else
    bitrate=0
    bitrate_source="unknown"
  fi

  if [[ ! "$bit_depth" =~ ^[0-9]+$ ]]; then
    if [[ "$pixel_format" =~ p([0-9]+)(le|be)?$ ]]; then
      bit_depth="${BASH_REMATCH[1]}"
    elif [[ "$pixel_format" =~ ^(yuv420p|yuv422p|yuv444p|nv12|yuyv422|uyvy422)$ ]]; then
      bit_depth=8
    else
      bit_depth="?"
    fi
  fi

  (( bitrate >= MIN_BITRATE_BPS )) || continue
  printf '%s\t%s\t%s\t%s\t%sx%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$bitrate" "$bitrate_source" "$codec" "$profile" "$width" "$height" \
    "$frame_rate" "$pixel_format" "$bit_depth" "$duration" "$size" \
    "$color_primaries" "$color_transfer" "$color_space" "$field_order" "$file"
done | sort -t $'\t' -k1,1nr > "$CANDIDATES"

total=$(wc -l < "$CANDIDATES" | tr -d '[:space:]')

# The report is TSV with one row per H.264 candidate.
{
  printf 'bitrate_bps\tbitrate_source\tcodec\tprofile\tresolution\tframe_rate\tpixel_format\tbit_depth\tduration_s\tsize_bytes\tcolor_primaries\tcolor_transfer\tcolor_space\tfield_order\tpath\n'
  cat "$CANDIDATES"
} > "$REPORT"

echo "Found $total H.264 file(s); report written to: $REPORT"
echo "Encoding up to the top $TOP_N bitrate candidates."

compressed_path() {
  local input="$1"
  local folder filename stem
  folder=$(dirname "$input")
  filename=$(basename "$input")
  stem="${filename%.*}"
  # A file with no extension should retain its entire filename as the stem.
  [[ "$stem" == "$filename" ]] && stem="$filename"
  printf '%s/%s_compressed.mp4\n' "$folder" "$stem"
}

encoded=0
while IFS=$'\t' read -r bitrate bitrate_source codec profile resolution frame_rate pixel_format bit_depth duration size color_primaries color_transfer color_space field_order file; do
  [[ -n "$file" ]] || continue
  output=$(compressed_path "$file")

  if [[ -e "$output" ]]; then
    echo "Skipping existing output: $output"
    continue
  fi

  echo "Encoding: $file"
  # -nostdin is essential here: otherwise ffmpeg can consume the next TSV
  # row (its stdin) as an interactive command, skipping a batch candidate.
  if ffmpeg -nostdin -hide_banner -n -i "$file" \
    -map 0:v:0 -map 0:a? \
    -map_metadata 0 -map_chapters 0 \
    -c:v libx265 -pix_fmt yuv420p10le -preset slow -crf 22 \
    -fps_mode vfr -tag:v hvc1 \
    -c:a aac -b:a 160k \
    -movflags +faststart \
    "$output"; then
    ((encoded += 1))
    echo "Created: $output"
  else
    echo "FAILED: $file" >&2
  fi
done < <(head -n "$TOP_N" "$CANDIDATES")

echo "Finished. Successfully encoded $encoded file(s)."
