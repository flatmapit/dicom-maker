#!/bin/bash
# Generate example studies for demonstration

set -e

echo "🎯 Generating DICOM Maker Example Studies"
echo "========================================"

# Create examples directory
mkdir -p examples

# Generate Chest X-Ray example
echo "📸 Creating Chest X-Ray example..."
python3 -m dicom_maker.cli create \
  --template chest-xray \
  --series-count 1 \
  --image-count 2 \
  --patient-name "Example^Chest^Patient" \
  --accession-number "CHEST-2025-001" \
  --study-description "Example Chest X-Ray Study"

# Get the study ID from the last created study
STUDY_ID=$(python3 -m dicom_maker.cli list-studies | grep -o '1\.2\.[0-9\.]*' | tail -1)

if [ -n "$STUDY_ID" ]; then
    echo "📁 Organizing Chest X-Ray example..."
    mkdir -p examples/chest-xray
    cp -r studies/$STUDY_ID examples/chest-xray/dicom
    
    # Export to PNG
    python3 -m dicom_maker.cli export \
      --study-id "$STUDY_ID" \
      --format png \
      --output-dir "examples/chest-xray/png"
    
    # Export to PDF
    python3 -m dicom_maker.cli export \
      --study-id "$STUDY_ID" \
      --format pdf \
      --output-file "examples/chest-xray/chest-xray-report.pdf"
    
    echo "✅ Chest X-Ray example created: examples/chest-xray/"
fi

# Generate CT Abdomen example
echo "🩻 Creating CT Abdomen example..."
python3 -m dicom_maker.cli create \
  --template ct-abdomen \
  --series-count 2 \
  --image-count 5 \
  --patient-name "Example^CT^Patient" \
  --accession-number "CT-2025-001" \
  --study-description "Example CT Abdomen Study"

# Get the study ID from the last created study
STUDY_ID=$(python3 -m dicom_maker.cli list-studies | grep -o '1\.2\.[0-9\.]*' | tail -1)

if [ -n "$STUDY_ID" ]; then
    echo "📁 Organizing CT Abdomen example..."
    mkdir -p examples/ct-abdomen
    cp -r studies/$STUDY_ID examples/ct-abdomen/dicom
    
    # Export to PNG
    python3 -m dicom_maker.cli export \
      --study-id "$STUDY_ID" \
      --format png \
      --output-dir "examples/ct-abdomen/png"
    
    # Export to PDF
    python3 -m dicom_maker.cli export \
      --study-id "$STUDY_ID" \
      --format pdf \
      --output-file "examples/ct-abdomen/ct-abdomen-report.pdf"
    
    echo "✅ CT Abdomen example created: examples/ct-abdomen/"
fi

# Generate Ultrasound example
echo "🔊 Creating Ultrasound example..."
python3 -m dicom_maker.cli create \
  --template ultrasound-abdomen \
  --series-count 2 \
  --image-count 3 \
  --patient-name "Example^US^Patient" \
  --accession-number "US-2025-001" \
  --study-description "Example Ultrasound Study"

# Get the study ID from the last created study
STUDY_ID=$(python3 -m dicom_maker.cli list-studies | grep -o '1\.2\.[0-9\.]*' | tail -1)

if [ -n "$STUDY_ID" ]; then
    echo "📁 Organizing Ultrasound example..."
    mkdir -p examples/ultrasound
    cp -r studies/$STUDY_ID examples/ultrasound/dicom
    
    # Export to PNG
    python3 -m dicom_maker.cli export \
      --study-id "$STUDY_ID" \
      --format png \
      --output-dir "examples/ultrasound/png"
    
    # Export to PDF
    python3 -m dicom_maker.cli export \
      --study-id "$STUDY_ID" \
      --format pdf \
      --output-file "examples/ultrasound/ultrasound-report.pdf"
    
    echo "✅ Ultrasound example created: examples/ultrasound/"
fi

# Generate Mammography example
echo "🩺 Creating Mammography example..."
python3 -m dicom_maker.cli create \
  --template mammography \
  --series-count 1 \
  --image-count 2 \
  --patient-name "Example^MG^Patient" \
  --accession-number "MG-2025-001" \
  --study-description "Example Mammography Study"

# Get the study ID from the last created study
STUDY_ID=$(python3 -m dicom_maker.cli list-studies | grep -o '1\.2\.[0-9\.]*' | tail -1)

if [ -n "$STUDY_ID" ]; then
    echo "📁 Organizing Mammography example..."
    mkdir -p examples/mammography
    cp -r studies/$STUDY_ID examples/mammography/dicom
    
    # Export to PNG
    python3 -m dicom_maker.cli export \
      --study-id "$STUDY_ID" \
      --format png \
      --output-dir "examples/mammography/png"
    
    # Export to PDF
    python3 -m dicom_maker.cli export \
      --study-id "$STUDY_ID" \
      --format pdf \
      --output-file "examples/mammography/mammography-report.pdf"
    
    echo "✅ Mammography example created: examples/mammography/"
fi

# Clean up studies directory
echo "🧹 Cleaning up temporary studies..."
rm -rf studies/

echo ""
echo "🎉 All example studies generated successfully!"
echo "📁 Check the examples/ directory for organized studies with DICOM, PNG, and PDF files."
echo ""
echo "Example directory structure:"
echo "examples/"
echo "├── chest-xray/"
echo "│   ├── dicom/          # DICOM files"
echo "│   ├── png/            # PNG exports"
echo "│   └── chest-xray-report.pdf"
echo "├── ct-abdomen/"
echo "│   ├── dicom/"
echo "│   ├── png/"
echo "│   └── ct-abdomen-report.pdf"
echo "├── ultrasound/"
echo "│   ├── dicom/"
echo "│   ├── png/"
echo "│   └── ultrasound-report.pdf"
echo "└── mammography/"
echo "    ├── dicom/"
echo "    ├── png/"
echo "    └── mammography-report.pdf"
