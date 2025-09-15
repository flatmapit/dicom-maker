#!/usr/bin/env python3
"""
Command Line Interface for DICOM Maker
"""

import click
import sys
from pathlib import Path
from typing import Optional

from .dicom_generator import DICOMGenerator
from .pacs_client import PACSClient
from .study_manager import StudyManager
from .logger import setup_logging, get_logger


@click.group()
@click.version_option()
@click.option('--log-file', help='Log file path')
@click.option('--log-level', default='INFO', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']))
@click.pass_context
def cli(ctx, log_file, log_level):
    """DICOM Maker - Create synthetic DICOM data and send to PACS systems."""
    # Set up logging
    setup_logging(log_file, log_level)
    ctx.ensure_object(dict)


@cli.command()
@click.option('--study-count', default=1, help='Number of studies to create')
@click.option('--series-count', default=1, help='Number of series per study')
@click.option('--image-count', default=1, help='Number of images per series')
@click.option('--modality', default='CR', help='DICOM modality (CR, CT, MR, etc.)')
@click.option('--template', help='Study template name')
@click.option('--anatomical-region', default='chest', help='Anatomical region for image generation')
@click.option('--patient-id', help='Patient ID')
@click.option('--patient-name', help='Patient name')
@click.option('--accession-number', help='Accession number')
@click.option('--study-description', help='Study description')
@click.option('--output-dir', default='studies', help='Output directory for studies')
@click.option('--config', help='Configuration file path')
def create(study_count: int, series_count: int, image_count: int, 
          modality: str, template: Optional[str], anatomical_region: str,
          patient_id: Optional[str], patient_name: Optional[str], 
          accession_number: Optional[str], study_description: Optional[str], 
          output_dir: str, config: Optional[str]):
    """Create synthetic DICOM studies."""
    try:
        logger = get_logger()
        generator = DICOMGenerator()
        study_manager = StudyManager(output_dir)
        
        # Prepare user fields
        user_fields = {}
        if patient_id:
            user_fields['patient_id'] = patient_id
        if patient_name:
            user_fields['patient_name'] = patient_name
        if accession_number:
            user_fields['accession_number'] = accession_number
        if study_description:
            user_fields['study_description'] = study_description
        
        logger.info(f"Creating {study_count} study(ies) with {series_count} series each...")
        
        for study_idx in range(study_count):
            study_id = generator.create_study(
                series_count=series_count,
                image_count=image_count,
                modality=modality,
                user_fields=user_fields,
                anatomical_region=anatomical_region,
                template=template
            )
            
            # Save study to local storage
            study_manager.save_study(study_id, generator.get_study(study_id))
            logger.success(f"Created study {study_id}")
        
        logger.success(f"Successfully created {study_count} study(ies) in {output_dir}/")
        
    except Exception as e:
        logger = get_logger()
        logger.error(f"Error creating studies: {e}")
        sys.exit(1)


@cli.command()
@click.option('--output-dir', default='studies', help='Studies directory')
def list_studies(output_dir: str):
    """List local DICOM studies."""
    try:
        logger = get_logger()
        study_manager = StudyManager(output_dir)
        studies = study_manager.list_studies()
        
        if not studies:
            logger.info("No studies found.")
            return
        
        logger.info(f"Found {len(studies)} study(ies):")
        for study_id, study_info in studies.items():
            logger.info(f"  {study_id}: {study_info}")
            
    except Exception as e:
        logger = get_logger()
        logger.error(f"Error listing studies: {e}")
        sys.exit(1)


@cli.command()
def list_templates():
    """List available study templates."""
    try:
        logger = get_logger()
        generator = DICOMGenerator()
        templates = generator.get_available_templates()
        
        logger.info("Available study templates:")
        for template in templates:
            logger.info(f"  {template}")
            
    except Exception as e:
        logger = get_logger()
        logger.error(f"Error listing templates: {e}")
        sys.exit(1)


@cli.command()
@click.option('--study-id', required=True, help='Study ID to export')
@click.option('--format', 'export_format', type=click.Choice(['png', 'pdf']), required=True, help='Export format')
@click.option('--output-dir', help='Output directory for PNG export')
@click.option('--output-file', help='Output file for PDF export')
@click.option('--studies-dir', default='studies', help='Studies directory')
def export(study_id: str, export_format: str, output_dir: Optional[str], 
          output_file: Optional[str], studies_dir: str):
    """Export DICOM study to PNG or PDF format."""
    try:
        logger = get_logger()
        study_manager = StudyManager(studies_dir)
        
        # Load study
        study = study_manager.load_study(study_id)
        if not study:
            logger.error(f"Study {study_id} not found!")
            sys.exit(1)
        
        if export_format == 'png':
            if not output_dir:
                output_dir = f"exports/{study_id}"
            logger.info(f"Exporting study {study_id} to PNG files in {output_dir}")
            # TODO: Implement PNG export
            logger.warning("PNG export not yet implemented")
            
        elif export_format == 'pdf':
            if not output_file:
                output_file = f"{study_id}.pdf"
            logger.info(f"Exporting study {study_id} to PDF: {output_file}")
            # TODO: Implement PDF export
            logger.warning("PDF export not yet implemented")
            
    except Exception as e:
        logger = get_logger()
        logger.error(f"Error exporting study: {e}")
        sys.exit(1)


@cli.command()
@click.option('--host', required=True, help='PACS host address')
@click.option('--port', default=11112, help='PACS port')
@click.option('--aec', required=True, help='Application Entity Caller')
@click.option('--aet', required=True, help='Application Entity Title')
def verify(host: str, port: int, aec: str, aet: str):
    """Verify PACS connection with C-ECHO."""
    try:
        logger = get_logger()
        pacs_client = PACSClient(host, port, aec, aet)
        
        logger.info(f"Verifying connection to {host}:{port}...")
        success = pacs_client.verify_connection()
        
        if success:
            logger.success("Connection verified successfully!")
        else:
            logger.failure("Connection failed!")
            sys.exit(1)
            
    except Exception as e:
        logger = get_logger()
        logger.error(f"Error verifying connection: {e}")
        sys.exit(1)


@cli.command()
@click.option('--study-id', required=True, help='Study ID to send')
@click.option('--host', required=True, help='PACS host address')
@click.option('--port', default=11112, help='PACS port')
@click.option('--aec', required=True, help='Application Entity Caller')
@click.option('--aet', required=True, help='Application Entity Title')
@click.option('--output-dir', default='studies', help='Studies directory')
def send(study_id: str, host: str, port: int, aec: str, aet: str, output_dir: str):
    """Send DICOM study to PACS."""
    try:
        logger = get_logger()
        
        # First verify connection
        pacs_client = PACSClient(host, port, aec, aet)
        logger.info("Verifying connection...")
        if not pacs_client.verify_connection():
            logger.failure("Connection verification failed!")
            sys.exit(1)
        
        # Load study
        study_manager = StudyManager(output_dir)
        study = study_manager.load_study(study_id)
        if not study:
            logger.error(f"Study {study_id} not found!")
            sys.exit(1)
        
        # Send study
        logger.info(f"Sending study {study_id} to {host}:{port}...")
        success = pacs_client.send_study(study)
        
        if success:
            logger.success("Study sent successfully!")
        else:
            logger.failure("Failed to send study!")
            sys.exit(1)
            
    except Exception as e:
        logger = get_logger()
        logger.error(f"Error sending study: {e}")
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()
