#!/bin/bash
# Create a chest X-ray study

set -e

echo "📸 Creating Chest X-Ray Study"
echo "============================="

# Create studies directory if it doesn't exist
mkdir -p studies

# Generate chest X-ray study
python3 -m dicom_maker.cli create \
  --template chest-xray \
  --series-count 1 \
  --image-count 2 \
  --patient-name "Chest^XRay^Patient" \
  --accession-number "CHEST-$(date +%Y%m%d)-001" \
  --study-description "Chest X-Ray Study"

# Get the study ID from the last created study
STUDY_ID=$(python3 -m dicom_maker.cli list-studies | grep -o '1\.2\.[0-9\.]*' | tail -1)

if [ -n "$STUDY_ID" ]; then
    echo "✅ Chest X-Ray study created successfully!"
    echo "📋 Study ID: $STUDY_ID"
    echo ""
    echo "Available commands:"
    echo "  Export to PNG:  python3 -m dicom_maker.cli export --study-id \"$STUDY_ID\" --format png --output-dir \"chest-xray-png\""
    echo "  Export to PDF:  python3 -m dicom_maker.cli export --study-id \"$STUDY_ID\" --format pdf --output-file \"chest-xray-report.pdf\""
    echo "  Send to PACS:   python3 -m dicom_maker.cli send --study-id \"$STUDY_ID\" --host <host> --port <port> --aec <aec> --aet <aet>"
    echo "  List studies:   python3 -m dicom_maker.cli list-studies"
else
    echo "❌ Failed to create chest X-ray study"
    exit 1
fi
