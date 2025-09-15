"""
DICOM Generator - Creates synthetic DICOM data
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import pydicom
from pydicom.dataset import Dataset
from pydicom.uid import generate_uid
from .dicom_validator import DICOMFieldValidator
from .image_generator import DICOMImageGenerator
from .logger import get_logger


class DICOMGenerator:
    """Generates synthetic DICOM studies, series, and images."""
    
    def __init__(self):
        self.studies: Dict[str, Dict[str, Any]] = {}
        self.validator = DICOMFieldValidator()
        self.image_generator = DICOMImageGenerator()
        self.logger = get_logger()
    
    def create_study(self, series_count: int = 1, image_count: int = 1, 
                    modality: str = "CR", user_fields: Optional[Dict[str, Any]] = None,
                    anatomical_region: str = "chest", template: Optional[str] = None) -> str:
        """
        Create a synthetic DICOM study.
        
        Args:
            series_count: Number of series in the study
            image_count: Number of images per series
            modality: DICOM modality (CR, CT, MR, etc.)
            user_fields: User-specified DICOM field values
            anatomical_region: Anatomical region for image generation
            template: Study template name (optional)
            
        Returns:
            Study Instance UID
        """
        if user_fields is None:
            user_fields = {}
        
        # Apply template if specified
        if template:
            template_fields = self._get_template_fields(template)
            user_fields = {**template_fields, **user_fields}
        
        study_uid = user_fields.get("study_uid", generate_uid())
        study_date = user_fields.get("study_date", datetime.now().strftime("%Y%m%d"))
        study_time = user_fields.get("study_time", datetime.now().strftime("%H%M%S"))
        
        study_data = {
            "study_uid": study_uid,
            "study_date": study_date,
            "study_time": study_time,
            "patient_id": user_fields.get("patient_id", str(uuid.uuid4())[:8]),
            "patient_name": user_fields.get("patient_name", f"Patient_{study_uid[:8]}"),
            "series": []
        }
        
        self.logger.info(f"Creating study {study_uid} with {series_count} series, {image_count} images each")
        
        # Create series
        for series_idx in range(series_count):
            series_uid = generate_uid()
            series_data = {
                "series_uid": series_uid,
                "series_number": series_idx + 1,
                "modality": modality,
                "images": []
            }
            
            self.logger.progress(f"Creating series {series_idx + 1}/{series_count}")
            
            # Create images
            for image_idx in range(image_count):
                image_uid = generate_uid()
                image_data = self._create_image_dataset(
                    study_data, series_data, image_uid, image_idx + 1,
                    user_fields, anatomical_region
                )
                series_data["images"].append(image_data)
            
            study_data["series"].append(series_data)
        
        self.studies[study_uid] = study_data
        self.logger.success(f"Created study {study_uid} with {len(study_data['series'])} series")
        return study_uid
    
    def _create_image_dataset(self, study_data: Dict, series_data: Dict, 
                            image_uid: str, instance_number: int,
                            user_fields: Dict[str, Any], anatomical_region: str) -> Dataset:
        """Create a DICOM dataset for an image."""
        ds = Dataset()
        
        # Prepare user fields for validation
        image_user_fields = {
            "patient_id": study_data["patient_id"],
            "patient_name": study_data["patient_name"],
            "study_uid": study_data["study_uid"],
            "study_date": study_data["study_date"],
            "study_time": study_data["study_time"],
            "series_uid": series_data["series_uid"],
            "series_number": series_data["series_number"],
            "modality": series_data["modality"],
            "sop_instance_uid": image_uid,
            "instance_number": instance_number,
            **user_fields
        }
        
        # Validate and generate patient fields
        ds = self.validator.validate_and_generate(ds, image_user_fields, "patient")
        
        # Validate and generate study fields
        ds = self.validator.validate_and_generate(ds, image_user_fields, "study")
        
        # Validate and generate series fields
        ds = self.validator.validate_and_generate(ds, image_user_fields, "series")
        
        # Validate and generate image fields
        ds = self.validator.validate_and_generate(ds, image_user_fields, "image")
        
        # Add additional fields
        ds.StudyID = study_data["study_uid"][:8]
        ds.StudyDescription = user_fields.get("study_description", f"Synthetic Study {study_data['study_uid'][:8]}")
        ds.SeriesDescription = user_fields.get("series_description", f"Synthetic Series {series_data['series_number']}")
        
        # Image Properties
        ds.Rows = user_fields.get("rows", 512)
        ds.Columns = user_fields.get("columns", 512)
        ds.BitsAllocated = 16
        ds.BitsStored = 16
        ds.HighBit = 15
        ds.PixelRepresentation = 0
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        
        # Generate realistic pixel data
        pixel_data = self.image_generator.generate_image(
            width=ds.Columns,
            height=ds.Rows,
            modality=series_data["modality"],
            anatomical_region=anatomical_region
        )
        ds.PixelData = pixel_data.tobytes()
        
        # Transfer Syntax - must be set before adding to dataset
        ds.file_meta = Dataset()
        ds.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
        ds.file_meta.MediaStorageSOPClassUID = ds.SOPClassUID
        ds.file_meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID
        ds.file_meta.ImplementationClassUID = pydicom.uid.PYDICOM_IMPLEMENTATION_UID
        
        # Set the transfer syntax in the dataset
        ds.is_implicit_VR = True
        ds.is_little_endian = True
        
        return ds
    
    def _get_template_fields(self, template: str) -> Dict[str, Any]:
        """Get template fields for a study template."""
        templates = {
            "chest-xray": {
                "modality": "CR",
                "anatomical_region": "chest",
                "study_description": "Chest X-Ray",
                "series_description": "PA Chest",
                "rows": 512,
                "columns": 512,
            },
            "ct-chest": {
                "modality": "CT",
                "anatomical_region": "chest",
                "study_description": "CT Chest",
                "series_description": "Axial CT Chest",
                "rows": 512,
                "columns": 512,
            },
            "ct-abdomen": {
                "modality": "CT",
                "anatomical_region": "abdomen",
                "study_description": "CT Abdomen",
                "series_description": "Axial CT Abdomen",
                "rows": 512,
                "columns": 512,
            },
            "mri-head": {
                "modality": "MR",
                "anatomical_region": "head",
                "study_description": "MRI Head",
                "series_description": "T1 Axial MRI",
                "rows": 256,
                "columns": 256,
            },
            "ultrasound-abdomen": {
                "modality": "US",
                "anatomical_region": "abdomen",
                "study_description": "Ultrasound Abdomen",
                "series_description": "Abdominal Ultrasound",
                "rows": 480,
                "columns": 640,
            },
            "mammography": {
                "modality": "MG",
                "anatomical_region": "chest",
                "study_description": "Mammography",
                "series_description": "CC View",
                "rows": 1024,
                "columns": 1024,
            },
        }
        
        return templates.get(template, {})
    
    def get_available_templates(self) -> List[str]:
        """Get list of available study templates."""
        return list(self._get_template_fields("").keys()) if hasattr(self, '_templates') else [
            "chest-xray", "ct-chest", "ct-abdomen", "mri-head", 
            "ultrasound-abdomen", "mammography"
        ]
    
    def get_study(self, study_uid: str) -> Optional[Dict[str, Any]]:
        """Get study data by UID."""
        return self.studies.get(study_uid)
    
    def list_studies(self) -> Dict[str, Dict[str, Any]]:
        """List all created studies."""
        return self.studies.copy()
