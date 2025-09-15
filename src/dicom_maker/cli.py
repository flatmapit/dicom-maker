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


@click.group()
@click.version_option()
def cli():
    """DICOM Maker - Create synthetic DICOM data and send to PACS systems."""
    pass


@cli.command()
@click.option('--study-count', default=1, help='Number of studies to create')
@click.option('--series-count', default=1, help='Number of series per study')
@click.option('--image-count', default=1, help='Number of images per series')
@click.option('--modality', default='CR', help='DICOM modality (CR, CT, MR, etc.)')
@click.option('--output-dir', default='studies', help='Output directory for studies')
@click.option('--config', help='Configuration file path')
def create(study_count: int, series_count: int, image_count: int, 
          modality: str, output_dir: str, config: Optional[str]):
    """Create synthetic DICOM studies."""
    try:
        generator = DICOMGenerator()
        study_manager = StudyManager(output_dir)
        
        click.echo(f"Creating {study_count} study(ies) with {series_count} series each...")
        
        for study_idx in range(study_count):
            study_id = generator.create_study(
                series_count=series_count,
                image_count=image_count,
                modality=modality
            )
            
            # Save study to local storage
            study_manager.save_study(study_id, generator.get_study(study_id))
            click.echo(f"Created study {study_id}")
        
        click.echo(f"Successfully created {study_count} study(ies) in {output_dir}/")
        
    except Exception as e:
        click.echo(f"Error creating studies: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--output-dir', default='studies', help='Studies directory')
def list_studies(output_dir: str):
    """List local DICOM studies."""
    try:
        study_manager = StudyManager(output_dir)
        studies = study_manager.list_studies()
        
        if not studies:
            click.echo("No studies found.")
            return
        
        click.echo(f"Found {len(studies)} study(ies):")
        for study_id, study_info in studies.items():
            click.echo(f"  {study_id}: {study_info}")
            
    except Exception as e:
        click.echo(f"Error listing studies: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--host', required=True, help='PACS host address')
@click.option('--port', default=11112, help='PACS port')
@click.option('--aec', required=True, help='Application Entity Caller')
@click.option('--aet', required=True, help='Application Entity Title')
def verify(host: str, port: int, aec: str, aet: str):
    """Verify PACS connection with C-ECHO."""
    try:
        pacs_client = PACSClient(host, port, aec, aet)
        
        click.echo(f"Verifying connection to {host}:{port}...")
        success = pacs_client.verify_connection()
        
        if success:
            click.echo("✓ Connection verified successfully!")
        else:
            click.echo("✗ Connection failed!", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Error verifying connection: {e}", err=True)
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
        # First verify connection
        pacs_client = PACSClient(host, port, aec, aet)
        click.echo("Verifying connection...")
        if not pacs_client.verify_connection():
            click.echo("Connection verification failed!", err=True)
            sys.exit(1)
        
        # Load study
        study_manager = StudyManager(output_dir)
        study = study_manager.load_study(study_id)
        if not study:
            click.echo(f"Study {study_id} not found!", err=True)
            sys.exit(1)
        
        # Send study
        click.echo(f"Sending study {study_id} to {host}:{port}...")
        success = pacs_client.send_study(study)
        
        if success:
            click.echo("✓ Study sent successfully!")
        else:
            click.echo("✗ Failed to send study!", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Error sending study: {e}", err=True)
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()
