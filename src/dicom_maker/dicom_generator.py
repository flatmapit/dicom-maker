"""
DICOM Generator - Creates synthetic DICOM data
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import pydicom
from pydicom.dataset import Dataset
from pydicom.uid import generate_uid


class DICOMGenerator:
    """Generates synthetic DICOM studies, series, and images."""
    
    def __init__(self):
        self.studies: Dict[str, Dict[str, Any]] = {}
    
    def create_study(self, series_count: int = 1, image_count: int = 1, 
                    modality: str = "CR") -> str:
        """
        Create a synthetic DICOM study.
        
        Args:
            series_count: Number of series in the study
            image_count: Number of images per series
            modality: DICOM modality (CR, CT, MR, etc.)
            
        Returns:
            Study Instance UID
        """
        study_uid = generate_uid()
        study_date = datetime.now().strftime("%Y%m%d")
        study_time = datetime.now().strftime("%H%M%S")
        
        study_data = {
            "study_uid": study_uid,
            "study_date": study_date,
            "study_time": study_time,
            "patient_id": str(uuid.uuid4())[:8],
            "patient_name": f"Patient_{study_uid[:8]}",
            "series": []
        }
        
        # Create series
        for series_idx in range(series_count):
            series_uid = generate_uid()
            series_data = {
                "series_uid": series_uid,
                "series_number": series_idx + 1,
                "modality": modality,
                "images": []
            }
            
            # Create images
            for image_idx in range(image_count):
                image_uid = generate_uid()
                image_data = self._create_image_dataset(
                    study_data, series_data, image_uid, image_idx + 1
                )
                series_data["images"].append(image_data)
            
            study_data["series"].append(series_data)
        
        self.studies[study_uid] = study_data
        return study_uid
    
    def _create_image_dataset(self, study_data: Dict, series_data: Dict, 
                            image_uid: str, instance_number: int) -> Dataset:
        """Create a DICOM dataset for an image."""
        ds = Dataset()
        
        # Patient Information
        ds.PatientID = study_data["patient_id"]
        ds.PatientName = study_data["patient_name"]
        ds.PatientBirthDate = "19900101"  # Default birth date
        ds.PatientSex = "O"  # Other/Unknown
        
        # Study Information
        ds.StudyInstanceUID = study_data["study_uid"]
        ds.StudyDate = study_data["study_date"]
        ds.StudyTime = study_data["study_time"]
        ds.StudyID = study_data["study_uid"][:8]
        ds.StudyDescription = f"Synthetic Study {study_data['study_uid'][:8]}"
        
        # Series Information
        ds.SeriesInstanceUID = series_data["series_uid"]
        ds.SeriesNumber = series_data["series_number"]
        ds.Modality = series_data["modality"]
        ds.SeriesDescription = f"Synthetic Series {series_data['series_number']}"
        
        # Image Information
        ds.SOPInstanceUID = image_uid
        ds.InstanceNumber = instance_number
        ds.SOPClassUID = self._get_sop_class_uid(series_data["modality"])
        
        # Image Properties
        ds.Rows = 512
        ds.Columns = 512
        ds.BitsAllocated = 16
        ds.BitsStored = 16
        ds.HighBit = 15
        ds.PixelRepresentation = 0
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        
        # Create synthetic pixel data
        import numpy as np
        pixel_data = np.random.randint(0, 65535, (512, 512), dtype=np.uint16)
        ds.PixelData = pixel_data.tobytes()
        
        # Transfer Syntax
        ds.file_meta = Dataset()
        ds.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
        ds.file_meta.MediaStorageSOPClassUID = ds.SOPClassUID
        ds.file_meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID
        ds.file_meta.ImplementationClassUID = pydicom.uid.PYDICOM_IMPLEMENTATION_UID
        
        return ds
    
    def _get_sop_class_uid(self, modality: str) -> str:
        """Get SOP Class UID based on modality."""
        sop_class_mapping = {
            "CR": "1.2.840.10008.5.1.4.1.1.1",  # Computed Radiography Image Storage
            "CT": "1.2.840.10008.5.1.4.1.1.2",  # CT Image Storage
            "MR": "1.2.840.10008.5.1.4.1.1.4",  # MR Image Storage
            "US": "1.2.840.10008.5.1.4.1.1.6.1", # Ultrasound Image Storage
            "DX": "1.2.840.10008.5.1.4.1.1.1.1", # Digital X-Ray Image Storage
        }
        return sop_class_mapping.get(modality, "1.2.840.10008.5.1.4.1.1.1")
    
    def get_study(self, study_uid: str) -> Optional[Dict[str, Any]]:
        """Get study data by UID."""
        return self.studies.get(study_uid)
    
    def list_studies(self) -> Dict[str, Dict[str, Any]]:
        """List all created studies."""
        return self.studies.copy()
