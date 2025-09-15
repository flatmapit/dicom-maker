# DICOM Maker

A native Python CLI application for creating synthetic DICOM data and sending it to PACS systems.

## Overview

DICOM Maker is a command-line tool designed to generate synthetic DICOM studies, series, and images locally, then send them to specified PACS systems using DICOM C-STORE operations. The application provides a native Python implementation without external dependencies, offering full control over DICOM data generation and transmission.

## Features

- **Native Python Implementation**: No external tool dependencies
- **Synthetic DICOM Generation**: Create studies, series, and images based on configuration
- **PACS Integration**: Send DICOM data via C-STORE after C-ECHO verification
- **Configurable Parameters**: Specify host, port, AEC (Application Entity Caller), and AET (Application Entity Title)
- **CLI Interface**: View and manage DICOM studies from the command line
- **Study Management**: Create, view, and manage local DICOM studies

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

# View local studies
dicom-maker list

# Send study to PACS
dicom-maker send --study-id <study-id> --host <pacs-host> --port <port> --aec <aec> --aet <aet>

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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## License

[License information to be added]

---

## TODOs

### High Priority
- [ ] Research existing DICOM generation tools and libraries
- [ ] Set up project structure and basic CLI framework
- [ ] Implement DICOM data generation (studies, series, images)
- [ ] Implement PACS communication (C-ECHO, C-STORE)
- [ ] Create configuration system for study templates
- [ ] Add comprehensive test suite
- [ ] Create installation and packaging setup

### Medium Priority
- [ ] Add support for different DICOM modalities (CR, CT, MR, etc.)
- [ ] Implement study validation and verification
- [ ] Add progress indicators for long operations
- [ ] Create example configurations and templates
- [ ] Add logging and error handling
- [ ] Performance optimization for large studies

### Low Priority
- [ ] Add GUI interface option
- [ ] Support for DICOM anonymization
- [ ] Batch processing capabilities
- [ ] Integration with DICOM viewers
- [ ] Advanced study manipulation features

## Questions for Clarification

### Technical Specifications
1. **DICOM Standards**: Which DICOM standard version should be supported? (DICOM 3.0, specific parts like PS3.3, PS3.6, etc.)

2. **Study Complexity**: What level of DICOM data complexity is needed?
   - Basic patient demographics and study info?
   - Full DICOM headers with all standard attributes?
   - Support for specific modalities (CT, MR, CR, US, etc.)?

3. **Data Sources**: Should the synthetic data be:
   - Completely random/generated?
   - Based on templates or real anonymized data?
   - Configurable per study/series?

4. **PACS Compatibility**: Are there specific PACS systems or DICOM implementations that need to be supported?

### Configuration and Usage
5. **Study Templates**: What kind of study templates are needed?
   - Predefined study types (chest X-ray, CT scan, etc.)?
   - Customizable series and image counts?
   - Specific DICOM attributes per template?
  A: All of these.

6. **CLI Interface**: What specific CLI commands and options are needed?
   - Study creation parameters?
   - PACS connection management?
   - Study viewing and management?

7. **Output Formats**: Besides sending to PACS, should the tool support:
   - Saving studies to local DICOM files?
   - Exporting to other formats?
   - Generating reports or summaries?

### Integration and Dependencies
8. **DICOM Libraries**: Are there preferences for DICOM libraries?
   - pydicom (Python DICOM library)?
   - Other specific libraries?
   - Any restrictions on dependencies?

9. **PACS Communication**: What DICOM services are needed?
   - Just C-ECHO and C-STORE?
   - C-FIND for querying?
   - C-MOVE for retrieval?

10. **Error Handling**: How should the application handle:
    - PACS connection failures?
    - Invalid DICOM data generation?
    - Network timeouts and retries?

### Performance and Scale
11. **Study Size**: What are the expected study sizes?
    - Small studies (1-10 images)?
    - Large studies (hundreds of images)?
    - Very large studies (thousands of images)?

12. **Concurrent Operations**: Should the tool support:
    - Multiple concurrent PACS connections?
    - Batch processing of multiple studies?
    - Parallel study generation?

Please provide answers to these questions to help refine the implementation approach and ensure the tool meets your specific requirements.
