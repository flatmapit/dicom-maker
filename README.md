# DICOM Maker

A native Python CLI application for creating synthetic DICOM data and sending it to PACS systems.

Copyright (c) 2025 flatmapit.com - Licensed under the MIT License

## Overview

DICOM Maker is a command-line tool designed to generate synthetic DICOM studies, series, and images locally, then send them to specified PACS systems using DICOM C-STORE operations. The application provides a native Python implementation without external dependencies, offering full control over DICOM data generation and transmission.

## Features

- **Native Python Implementation**: No external tool dependencies
- **DICOM 3.0 Compliant**: Full support for DICOM standard with user-configurable fields
- **Realistic Synthetic Data**: Generate realistic but randomized DICOM data using dicom-fabricator style
- **Study Templates**: Predefined templates for common modalities (CT, MR, CR, US, DX, MG)
- **PACS Integration**: C-ECHO and C-STORE operations for complete PACS communication
- **Export Capabilities**: Export to PNG+text files or PDF with metadata
- **Burnt-in Text**: DICOM metadata overlaid directly on generated images
- **Comprehensive Logging**: CLI and file logging with detailed operation tracking
- **Configurable Generation**: Set parameters at patient, study, and series levels
- **CLI Interface**: Complete command-line interface for all operations
- **Study Management**: Create, view, manage, and export local DICOM studies
- **Convenience Scripts**: Ready-to-use shell scripts for common operations
- **Example Studies**: Pre-generated examples for testing and demonstration

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Virtual Environment Setup (Recommended)

It's strongly recommended to use a virtual environment to avoid conflicts with system packages:

```bash
# Clone the repository
git clone <repository-url>
cd dicom-maker

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Upgrade pip to the latest version
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

### Alternative: Direct Installation

If you prefer not to use a virtual environment (not recommended):

```bash
# Clone the repository
git clone <repository-url>
cd dicom-maker

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Quick Development Setup

For a quick setup with all dependencies, you can use the provided setup script:

```bash
# Clone the repository
git clone <repository-url>
cd dicom-maker

# Run the development setup script
python setup_dev.py

# Activate the virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
```

### Deactivating the Virtual Environment

When you're done working on the project:

```bash
deactivate
```

### Troubleshooting Virtual Environment Issues

**Problem**: `python` command not found
- **Solution**: Use `python3` instead of `python` in the commands above

**Problem**: Permission denied when creating virtual environment
- **Solution**: Ensure you have write permissions in the project directory

**Problem**: Virtual environment not activating
- **Solution**: Make sure you're using the correct activation command for your operating system

**Problem**: Package installation fails
- **Solution**: Make sure the virtual environment is activated before running `pip install` commands

**Problem**: `dicom-maker` command not found after installation
- **Solution**: Ensure the virtual environment is activated and the package was installed with `pip install -e .`

## Usage

### Basic Commands

```bash
# Create a synthetic DICOM study
dicom-maker create --study-count 1 --series-count 2 --image-count 10

# Create study from template
dicom-maker create --template chest-xray --series-count 1 --image-count 2

# View local studies
dicom-maker list

# Export study to PNG+text files
dicom-maker export --study-id <study-id> --format png --output-dir exports/

# Export study to PDF
dicom-maker export --study-id <study-id> --format pdf --output-file study.pdf

# Send study to PACS
dicom-maker send --study-id <study-id> --host <pacs-host> --port <port> --aec <aec> --aet <aet>

# Query PACS for studies
dicom-maker query --host <pacs-host> --port <port> --aec <aec> --aet <aet> --patient-id <patient-id>

# Verify PACS connection
dicom-maker verify --host <pacs-host> --port <port> --aec <aec> --aet <aet>
```

### Configuration

Create a configuration file to define default parameters:

```yaml
# config.yaml
default_pacs:
  host: "localhost"
  port: 11112
  aec: "DICOM_MAKER"
  aet: "PACS_SERVER"

study_templates:
  - name: "chest_xray"
    series_count: 1
    image_count: 2
    modality: "CR"
  - name: "ct_scan"
    series_count: 3
    image_count: 50
    modality: "CT"
```

## Development

### Project Structure

```
dicom-maker/
├── src/
│   └── dicom_maker/
│       ├── __init__.py
│       ├── cli.py
│       ├── dicom_generator.py
│       ├── pacs_client.py
│       └── study_manager.py
├── tests/
├── configs/
├── requirements.txt
├── setup.py
└── README.md
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/dicom_maker

# Run specific test file
pytest tests/test_dicom_generator.py
```

## Examples

### Quick Start Examples

The `bin/` directory contains convenience scripts for common operations:

```bash
# Generate example studies
./bin/generate-examples.sh

# Create a chest X-ray study
./bin/create-chest-xray.sh

# Create a CT study with 2 series
./bin/create-ct-study.sh

# Send study to PACS
./bin/send-to-pacs.sh <study-id> <host> <port> <aec> <aet>
```

### Example Studies

The `examples/` directory contains pre-generated studies:

- **Chest X-Ray**: `examples/chest-xray/` - Single series CR study
- **CT Abdomen**: `examples/ct-abdomen/` - Multi-series CT study
- **Ultrasound**: `examples/ultrasound/` - US study with multiple series
- **Mammography**: `examples/mammography/` - MG study with high-resolution images

Each example includes:
- DICOM files in `dicom/` subdirectory
- PNG exports in `png/` subdirectory
- PDF report in the root directory
- Study metadata in JSON format

### Command Examples

```bash
# Create a study with custom parameters
dicom-maker create \
  --modality CT \
  --series-count 2 \
  --image-count 5 \
  --patient-name "Doe^John" \
  --accession-number "CT-2025-001" \
  --study-description "CT Chest and Abdomen"

# Export study to PNG files
dicom-maker export \
  --study-id "1.2.826.0.1.3680043.8.498.123456789" \
  --format png \
  --output-dir "exports/ct-study"

# Export study to PDF
dicom-maker export \
  --study-id "1.2.826.0.1.3680043.8.498.123456789" \
  --format pdf \
  --output-file "ct-study-report.pdf"

# Send study to PACS
dicom-maker send \
  --study-id "1.2.826.0.1.3680043.8.498.123456789" \
  --host localhost \
  --port 4242 \
  --aec DICOM_MANAGER \
  --aet PACS1

# Verify PACS connection
dicom-maker verify \
  --host localhost \
  --port 4242 \
  --aec DICOM_MANAGER \
  --aet PACS1
```

### Study Templates

Available templates for quick study generation:

```bash
# List all available templates
dicom-maker list-templates

# Create study using template
dicom-maker create --template chest-xray --series-count 1 --image-count 2
dicom-maker create --template ct-chest --series-count 2 --image-count 10
dicom-maker create --template ultrasound-abdomen --series-count 1 --image-count 5
dicom-maker create --template mammography --series-count 1 --image-count 4
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## TODOs

### High Priority
- [x] Set up project structure and basic CLI framework
- [x] Create installation and packaging setup
- [x] Implement realistic DICOM data generation with dicom-fabricator style images
- [x] Add user-configurable DICOM fields with automatic mandatory data generation
- [ ] Implement C-FIND support for PACS querying
- [x] Add comprehensive logging system (CLI + file)
- [x] Create study templates for common modalities
- [x] Add export functionality (PNG+text, PDF)
- [x] Add burnt-in text with DICOM metadata
- [x] Fix PACS client UID handling and DX modality support
- [x] Create convenience shell scripts
- [x] Generate example studies and documentation

### Medium Priority
- [x] Implement DICOM field validation and error handling
- [x] Add progress indicators for long operations
- [x] Create example configurations and templates
- [ ] Performance optimization for large studies (thousands of images)
- [ ] Add comprehensive test suite
- [ ] Create documentation for study templates

### Low Priority
- [ ] Add GUI interface option
- [ ] Support for DICOM anonymization
- [ ] Integration with DICOM viewers
- [ ] Advanced study manipulation features
- [ ] Support for additional export formats

## Implementation Details

### DICOM Standards
- **DICOM 3.0** standard compliance
- Support for all common modalities (CT, MR, CR, US, DX, etc.)
- User-configurable DICOM fields with automatic generation of mandatory data
- Comprehensive logging when unspecified data is generated

### Data Generation
- **Realistic but randomized** synthetic data using dicom-fabricator style image generation
- **Configurable at patient, study, and series levels**
- **Study templates** for common examination types (chest X-ray, CT scan, MRI, etc.)
- **Customizable series and image counts** per study

### PACS Integration
- **C-ECHO** for connection verification
- **C-FIND** for querying PACS systems
- **C-STORE** for sending DICOM data
- **Single user, single study** operation model

### Export Capabilities
- **Local DICOM file storage** with organized directory structure
- **PNG + text file export** with metadata summaries
- **PDF export** with images and metadata on each page
- **Comprehensive logging** to both CLI and log files

### Error Handling
- **CLI reporting** for all operations
- **File logging** for detailed error tracking
- **Graceful handling** of PACS connection failures and network timeouts
- **Validation and retry mechanisms** for robust operation
