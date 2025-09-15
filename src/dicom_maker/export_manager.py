"""
Export Manager - Handles DICOM study export to various formats
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import numpy as np
from PIL import Image
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib import colors
from pydicom.dataset import Dataset
from .logger import get_logger


class ExportManager:
    """Manages export of DICOM studies to various formats."""
    
    def __init__(self):
        """Initialize the export manager."""
        self.logger = get_logger()
    
    def export_to_png(self, study_data: Dict[str, Any], output_dir: str) -> bool:
        """
        Export DICOM study to PNG files with metadata text files.
        
        Args:
            study_data: Dictionary containing study information and DICOM datasets
            output_dir: Output directory for PNG files and metadata
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Exporting study to PNG files in {output_dir}")
            
            # Create study metadata file
            study_metadata = self._extract_study_metadata(study_data)
            metadata_file = output_path / "study_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(study_metadata, f, indent=2, default=str)
            
            self.logger.info(f"Created study metadata: {metadata_file}")
            
            # Export each series
            for series_idx, series in enumerate(study_data.get('series', []), 1):
                series_dir = output_path / f"series_{series_idx}"
                series_dir.mkdir(exist_ok=True)
                
                # Create series metadata
                series_metadata = self._extract_series_metadata(series, series_idx)
                series_metadata_file = series_dir / "series_metadata.json"
                with open(series_metadata_file, 'w') as f:
                    json.dump(series_metadata, f, indent=2, default=str)
                
                # Export each image in the series
                for image_idx, image_ds in enumerate(series.get('images', []), 1):
                    self._export_image_to_png(image_ds, series_dir, image_idx)
            
            self.logger.success(f"Successfully exported study to {output_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting to PNG: {e}")
            return False
    
    def export_to_pdf(self, study_data: Dict[str, Any], output_file: str) -> bool:
        """
        Export DICOM study to PDF with images and metadata.
        
        Args:
            study_data: Dictionary containing study information and DICOM datasets
            output_file: Output PDF file path
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            self.logger.info(f"Exporting study to PDF: {output_file}")
            
            # Create PDF document
            doc = SimpleDocTemplate(output_file, pagesize=A4)
            story = []
            
            # Define styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                textColor=colors.darkblue
            )
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=12,
                spaceAfter=12,
                textColor=colors.darkgreen
            )
            normal_style = styles['Normal']
            
            # Add study title
            study_title = f"DICOM Study Report - {study_data.get('patient_name', 'Unknown Patient')}"
            story.append(Paragraph(study_title, title_style))
            story.append(Spacer(1, 20))
            
            # Add study metadata
            study_metadata = self._extract_study_metadata(study_data)
            story.append(Paragraph("Study Information", heading_style))
            for key, value in study_metadata.items():
                story.append(Paragraph(f"<b>{key}:</b> {value}", normal_style))
            story.append(Spacer(1, 20))
            
            # Keep track of all temporary files for cleanup
            temp_files = []
            
            # Add series information
            for series_idx, series in enumerate(study_data.get('series', []), 1):
                story.append(Paragraph(f"Series {series_idx}", heading_style))
                
                # Series metadata
                series_metadata = self._extract_series_metadata(series, series_idx)
                for key, value in series_metadata.items():
                    story.append(Paragraph(f"<b>{key}:</b> {value}", normal_style))
                
                story.append(Spacer(1, 10))
                
                # Add images from this series (limit to first 4 images to avoid huge PDFs)
                images_to_show = series.get('images', [])[:4]
                for image_idx, image_ds in enumerate(images_to_show, 1):
                    # Create temporary PNG for this image
                    temp_png = self._create_temp_png(image_ds)
                    if temp_png:
                        temp_files.append(temp_png)  # Add to list for cleanup later
                        # Add image to PDF
                        img = RLImage(temp_png, width=4*inch, height=4*inch)
                        story.append(Paragraph(f"Image {image_idx} (Instance {image_ds.get('InstanceNumber', 'N/A')})", normal_style))
                        story.append(img)
                        story.append(Spacer(1, 10))
                
                if len(series.get('images', [])) > 4:
                    story.append(Paragraph(f"... and {len(series.get('images', [])) - 4} more images", normal_style))
                
                story.append(PageBreak())
            
            # Build PDF
            doc.build(story)
            
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except Exception as e:
                    self.logger.warning(f"Could not clean up temp file {temp_file}: {e}")
            
            self.logger.success(f"Successfully exported study to PDF: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting to PDF: {e}")
            return False
    
    def _extract_study_metadata(self, study_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract study-level metadata."""
        # Get metadata from first image if available
        study_time = 'N/A'
        accession_number = 'N/A'
        
        if study_data.get('series') and study_data['series'][0].get('images'):
            first_image = study_data['series'][0]['images'][0]
            if hasattr(first_image, 'StudyTime'):
                study_time = str(first_image.StudyTime)
            if hasattr(first_image, 'AccessionNumber'):
                accession_number = str(first_image.AccessionNumber)
        
        metadata = {
            "Study Instance UID": study_data.get('study_uid', 'N/A'),
            "Patient Name": study_data.get('patient_name', 'N/A'),
            "Patient ID": study_data.get('patient_id', 'N/A'),
            "Study Date": study_data.get('study_date', 'N/A'),
            "Study Time": study_time,
            "Accession Number": accession_number,
            "Number of Series": len(study_data.get('series', [])),
            "Total Images": sum(len(series.get('images', [])) for series in study_data.get('series', []))
        }
        return metadata
    
    def _extract_series_metadata(self, series: Dict[str, Any], series_number: int) -> Dict[str, Any]:
        """Extract series-level metadata."""
        metadata = {
            "Series Number": series_number,
            "Series Instance UID": series.get('series_uid', 'N/A'),
            "Modality": series.get('modality', 'N/A'),
            "Number of Images": len(series.get('images', []))
        }
        
        # Get additional metadata from first image if available
        if series.get('images'):
            first_image = series['images'][0]
            if hasattr(first_image, 'SeriesInstanceUID'):
                metadata["Series Instance UID"] = str(first_image.SeriesInstanceUID)
            if hasattr(first_image, 'Modality'):
                metadata["Modality"] = str(first_image.Modality)
            if hasattr(first_image, 'SeriesDescription'):
                metadata["Series Description"] = str(first_image.SeriesDescription)
            if hasattr(first_image, 'StudyDescription'):
                metadata["Study Description"] = str(first_image.StudyDescription)
        
        return metadata
    
    def _export_image_to_png(self, image_ds: Dataset, output_dir: Path, image_number: int) -> None:
        """Export a single DICOM image to PNG format."""
        try:
            # Extract pixel data
            pixel_array = image_ds.pixel_array
            
            # Normalize pixel values to 0-255 range
            if pixel_array.dtype != np.uint8:
                # Normalize to 0-255 range
                pixel_array = ((pixel_array - pixel_array.min()) / 
                             (pixel_array.max() - pixel_array.min()) * 255).astype(np.uint8)
            
            # Create PIL Image
            pil_image = Image.fromarray(pixel_array, mode='L')
            
            # Save PNG
            png_filename = f"image_{image_number:03d}_instance_{image_ds.get('InstanceNumber', image_number)}.png"
            png_path = output_dir / png_filename
            pil_image.save(png_path)
            
            # Create metadata text file for this image
            metadata_filename = f"image_{image_number:03d}_metadata.txt"
            metadata_path = output_dir / metadata_filename
            
            with open(metadata_path, 'w') as f:
                f.write(f"DICOM Image Metadata\n")
                f.write(f"====================\n\n")
                f.write(f"Instance Number: {image_ds.get('InstanceNumber', 'N/A')}\n")
                f.write(f"SOP Instance UID: {image_ds.get('SOPInstanceUID', 'N/A')}\n")
                f.write(f"Modality: {image_ds.get('Modality', 'N/A')}\n")
                f.write(f"Rows: {image_ds.get('Rows', 'N/A')}\n")
                f.write(f"Columns: {image_ds.get('Columns', 'N/A')}\n")
                f.write(f"Bits Allocated: {image_ds.get('BitsAllocated', 'N/A')}\n")
                f.write(f"Bits Stored: {image_ds.get('BitsStored', 'N/A')}\n")
                f.write(f"Photometric Interpretation: {image_ds.get('PhotometricInterpretation', 'N/A')}\n")
                f.write(f"Patient Name: {image_ds.get('PatientName', 'N/A')}\n")
                f.write(f"Patient ID: {image_ds.get('PatientID', 'N/A')}\n")
                f.write(f"Study Date: {image_ds.get('StudyDate', 'N/A')}\n")
                f.write(f"Study Time: {image_ds.get('StudyTime', 'N/A')}\n")
                f.write(f"Accession Number: {image_ds.get('AccessionNumber', 'N/A')}\n")
            
            self.logger.info(f"Exported image {image_number} to {png_path}")
            
        except Exception as e:
            self.logger.error(f"Error exporting image {image_number}: {e}")
    
    def _create_temp_png(self, image_ds: Dataset) -> Optional[str]:
        """Create a temporary PNG file for PDF inclusion."""
        try:
            # Extract pixel data
            pixel_array = image_ds.pixel_array
            
            # Normalize pixel values to 0-255 range
            if pixel_array.dtype != np.uint8:
                pixel_array = ((pixel_array - pixel_array.min()) / 
                             (pixel_array.max() - pixel_array.min()) * 255).astype(np.uint8)
            
            # Create PIL Image
            pil_image = Image.fromarray(pixel_array, mode='L')
            
            # Create temporary file
            import tempfile
            temp_fd, temp_path = tempfile.mkstemp(suffix='.png')
            os.close(temp_fd)
            
            # Save PNG
            pil_image.save(temp_path)
            
            return temp_path
            
        except Exception as e:
            self.logger.error(f"Error creating temporary PNG: {e}")
            return None
