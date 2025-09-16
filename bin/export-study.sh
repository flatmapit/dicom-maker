#!/bin/bash
# Export a study to PNG or PDF

set -e

if [ $# -lt 2 ]; then
    echo "Usage: $0 <study-id> <format> [output-path]"
    echo ""
    echo "Arguments:"
    echo "  study-id    : DICOM Study Instance UID"
    echo "  format      : Export format (png or pdf)"
    echo "  output-path : Output directory (PNG) or file (PDF) [optional]"
    echo ""
    echo "Examples:"
    echo "  $0 1.2.826.0.1.3680043.8.498.123456789 png"
    echo "  $0 1.2.826.0.1.3680043.8.498.123456789 png exports/my-study"
    echo "  $0 1.2.826.0.1.3680043.8.498.123456789 pdf"
    echo "  $0 1.2.826.0.1.3680043.8.498.123456789 pdf my-study-report.pdf"
    exit 1
fi

STUDY_ID=$1
FORMAT=$2
OUTPUT_PATH=$3

echo "📤 Exporting Study"
echo "=================="
echo "Study ID: $STUDY_ID"
echo "Format: $FORMAT"
echo ""

if [ "$FORMAT" = "png" ]; then
    if [ -n "$OUTPUT_PATH" ]; then
        OUTPUT_DIR="$OUTPUT_PATH"
    else
        OUTPUT_DIR="exports/${STUDY_ID:0:20}"
    fi
    
    echo "📁 Output directory: $OUTPUT_DIR"
    echo ""
    
    python3 -m dicom_maker.cli export \
      --study-id "$STUDY_ID" \
      --format png \
      --output-dir "$OUTPUT_DIR"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Study exported to PNG successfully!"
        echo "📁 Check directory: $OUTPUT_DIR"
    else
        echo ""
        echo "❌ Failed to export study to PNG"
        exit 1
    fi

elif [ "$FORMAT" = "pdf" ]; then
    if [ -n "$OUTPUT_PATH" ]; then
        OUTPUT_FILE="$OUTPUT_PATH"
    else
        OUTPUT_FILE="${STUDY_ID:0:20}-report.pdf"
    fi
    
    echo "📄 Output file: $OUTPUT_FILE"
    echo ""
    
    python3 -m dicom_maker.cli export \
      --study-id "$STUDY_ID" \
      --format pdf \
      --output-file "$OUTPUT_FILE"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Study exported to PDF successfully!"
        echo "📄 Check file: $OUTPUT_FILE"
    else
        echo ""
        echo "❌ Failed to export study to PDF"
        exit 1
    fi

else
    echo "❌ Invalid format. Use 'png' or 'pdf'"
    exit 1
fi
