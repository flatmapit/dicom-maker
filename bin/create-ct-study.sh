#!/bin/bash
# Create a CT study with multiple series

set -e

echo "🩻 Creating CT Study"
echo "==================="

# Create studies directory if it doesn't exist
mkdir -p studies

# Generate CT study
python3 -m dicom_maker.cli create \
  --template ct-chest \
  --series-count 2 \
  --image-count 5 \
  --patient-name "CT^Scan^Patient" \
  --accession-number "CT-$(date +%Y%m%d)-001" \
  --study-description "CT Chest and Abdomen Study"

# Get the study ID from the last created study
STUDY_ID=$(python3 -m dicom_maker.cli list-studies | grep -o '1\.2\.[0-9\.]*' | tail -1)

if [ -n "$STUDY_ID" ]; then
    echo "✅ CT study created successfully!"
    echo "📋 Study ID: $STUDY_ID"
    echo ""
    echo "Available commands:"
    echo "  Export to PNG:  python3 -m dicom_maker.cli export --study-id \"$STUDY_ID\" --format png --output-dir \"ct-study-png\""
    echo "  Export to PDF:  python3 -m dicom_maker.cli export --study-id \"$STUDY_ID\" --format pdf --output-file \"ct-study-report.pdf\""
    echo "  Send to PACS:   python3 -m dicom_maker.cli send --study-id \"$STUDY_ID\" --host <host> --port <port> --aec <aec> --aet <aet>"
    echo "  List studies:   python3 -m dicom_maker.cli list-studies"
else
    echo "❌ Failed to create CT study"
    exit 1
fi
