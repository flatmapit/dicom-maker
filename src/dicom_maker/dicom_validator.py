"""
DICOM Field Validator and Generator

Copyright (c) 2025 flatmapit.com
Licensed under the MIT License
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import pydicom
from pydicom.dataset import Dataset
from pydicom.uid import generate_uid
from .logger import log_dicom_field_generation


class DICOMFieldValidator:
    """Validates and generates DICOM fields according to DICOM 3.0 standard."""
    
    # Mandatory fields by module
    MANDATORY_FIELDS = {
        "patient": {
            "0010,0010": "PatientName",
            "0010,0020": "PatientID",
            "0010,0030": "PatientBirthDate",
        },
        "study": {
            "0020,000D": "StudyInstanceUID",
            "0008,0020": "StudyDate",
            "0008,0030": "StudyTime",
            "0008,0050": "AccessionNumber",
        },
        "series": {
            "0020,000E": "SeriesInstanceUID",
            "0020,0011": "SeriesNumber",
            "0008,0060": "Modality",
        },
        "image": {
            "0008,0018": "SOPInstanceUID",
            "0008,0016": "SOPClassUID",
            "0020,0013": "InstanceNumber",
        }
    }
    
    # Field validation rules
    FIELD_RULES = {
        "0010,0010": {"type": str, "required": True, "max_length": 64},
        "0010,0020": {"type": str, "required": True, "max_length": 64},
        "0010,0030": {"type": str, "required": False, "format": "YYYYMMDD"},
        "0010,0040": {"type": str, "required": False, "values": ["M", "F", "O"]},
        "0020,000D": {"type": str, "required": True, "format": "uid"},
        "0008,0020": {"type": str, "required": True, "format": "YYYYMMDD"},
        "0008,0030": {"type": str, "required": True, "format": "HHMMSS"},
        "0008,0050": {"type": str, "required": True, "max_length": 16},
        "0020,000E": {"type": str, "required": True, "format": "uid"},
        "0020,0011": {"type": int, "required": True, "min": 1},
        "0008,0060": {"type": str, "required": True, "values": ["CR", "CT", "MR", "US", "DX", "NM", "PT", "RF", "SC", "MG", "XA", "XC"]},
        "0008,0018": {"type": str, "required": True, "format": "uid"},
        "0008,0016": {"type": str, "required": True, "format": "uid"},
        "0020,0013": {"type": int, "required": True, "min": 1},
    }
    
    def __init__(self):
        """Initialize the validator."""
        self.generated_fields = {}
    
    def validate_and_generate(self, dataset: Dataset, user_fields: Dict[str, Any], 
                            module: str = "image") -> Dataset:
        """
        Validate and generate DICOM fields.
        
        Args:
            dataset: DICOM dataset to validate
            user_fields: User-specified field values
            module: DICOM module (patient, study, series, image)
            
        Returns:
            Validated dataset with generated fields
        """
        # Get mandatory fields for the module
        mandatory_fields = self.MANDATORY_FIELDS.get(module, {})
        
        # Process each mandatory field
        for tag, field_name in mandatory_fields.items():
            if not hasattr(dataset, field_name):
                # Generate field if not present
                generated_value = self._generate_field(tag, field_name, user_fields, module)
                setattr(dataset, field_name, generated_value)
                log_dicom_field_generation(tag, field_name, str(generated_value))
        
        # Process user-specified fields
        for field_name, value in user_fields.items():
            # Skip non-DICOM fields (like patient_name, study_uid, etc.)
            if field_name in ['patient_name', 'patient_id', 'study_uid', 'study_date', 
                            'study_time', 'accession_number', 'series_uid', 'series_number', 
                            'modality', 'sop_instance_uid', 'instance_number', 'study_description',
                            'series_description', 'rows', 'columns']:
                continue
                
            if self._is_valid_field(field_name, value):
                setattr(dataset, field_name, value)
            else:
                # Generate valid field if user value is invalid
                generated_value = self._generate_field(field_name, field_name, user_fields, module)
                setattr(dataset, field_name, generated_value)
                log_dicom_field_generation(field_name, field_name, str(generated_value), "invalid user value")
        
        return dataset
    
    def _is_valid_field(self, field_name: str, value: Any) -> bool:
        """Check if a field value is valid according to DICOM rules."""
        # Map field names to tags for validation
        field_to_tag = {
            "PatientName": "0010,0010",
            "PatientID": "0010,0020",
            "PatientBirthDate": "0010,0030",
            "PatientSex": "0010,0040",
            "StudyInstanceUID": "0020,000D",
            "StudyDate": "0008,0020",
            "StudyTime": "0008,0030",
            "AccessionNumber": "0008,0050",
            "SeriesInstanceUID": "0020,000E",
            "SeriesNumber": "0020,0011",
            "Modality": "0008,0060",
            "SOPInstanceUID": "0008,0018",
            "SOPClassUID": "0008,0016",
            "InstanceNumber": "0020,0013",
        }
        
        tag = field_to_tag.get(field_name)
        if not tag or tag not in self.FIELD_RULES:
            return True  # Unknown fields are allowed
        
        rule = self.FIELD_RULES[tag]
        
        # Check type
        if not isinstance(value, rule["type"]):
            return False
        
        # Check required
        if rule.get("required", False) and not value:
            return False
        
        # Check max length
        if "max_length" in rule and len(str(value)) > rule["max_length"]:
            return False
        
        # Check allowed values
        if "values" in rule and value not in rule["values"]:
            return False
        
        # Check format
        if "format" in rule:
            if not self._validate_format(value, rule["format"]):
                return False
        
        # Check min value
        if "min" in rule and value < rule["min"]:
            return False
        
        return True
    
    def _validate_format(self, value: str, format_type: str) -> bool:
        """Validate field format."""
        if format_type == "YYYYMMDD":
            try:
                datetime.strptime(value, "%Y%m%d")
                return True
            except ValueError:
                return False
        elif format_type == "HHMMSS":
            try:
                datetime.strptime(value, "%H%M%S")
                return True
            except ValueError:
                return False
        elif format_type == "uid":
            # Basic UID validation
            return len(value) > 0 and value.replace(".", "").isdigit()
        
        return True
    
    def _generate_field(self, tag: str, field_name: str, user_fields: Dict[str, Any], 
                       module: str) -> Any:
        """Generate a field value based on tag and context."""
        if tag == "0010,0010":  # PatientName
            return user_fields.get("patient_name", f"Patient_{uuid.uuid4().hex[:8]}")
        elif tag == "0010,0020":  # PatientID
            return user_fields.get("patient_id", str(uuid.uuid4())[:8])
        elif tag == "0010,0030":  # PatientBirthDate
            return user_fields.get("patient_birth_date", self._generate_random_dob())
        elif tag == "0010,0040":  # PatientSex
            return user_fields.get("patient_sex", "O")
        elif tag == "0020,000D":  # StudyInstanceUID
            return user_fields.get("study_uid", generate_uid())
        elif tag == "0008,0020":  # StudyDate
            return user_fields.get("study_date", datetime.now().strftime("%Y%m%d"))
        elif tag == "0008,0030":  # StudyTime
            return user_fields.get("study_time", datetime.now().strftime("%H%M%S"))
        elif tag == "0008,0050":  # AccessionNumber
            return user_fields.get("accession_number", self._generate_accession_number())
        elif tag == "0020,000E":  # SeriesInstanceUID
            return user_fields.get("series_uid", generate_uid())
        elif tag == "0020,0011":  # SeriesNumber
            return user_fields.get("series_number", 1)
        elif tag == "0008,0060":  # Modality
            return user_fields.get("modality", "CR")
        elif tag == "0008,0018":  # SOPInstanceUID
            return user_fields.get("sop_instance_uid", generate_uid())
        elif tag == "0008,0016":  # SOPClassUID
            return self._get_sop_class_uid(user_fields.get("modality", "CR"))
        elif tag == "0020,0013":  # InstanceNumber
            return user_fields.get("instance_number", 1)
        else:
            # Generate default value based on type
            if tag in self.FIELD_RULES:
                field_type = self.FIELD_RULES[tag]["type"]
                if field_type == str:
                    return f"Generated_{tag.replace(',', '_')}"
                elif field_type == int:
                    return 1
            return "Generated"
    
    def _get_sop_class_uid(self, modality: str) -> str:
        """Get SOP Class UID based on modality."""
        sop_class_mapping = {
            "CR": "1.2.840.10008.5.1.4.1.1.1",  # Computed Radiography Image Storage
            "CT": "1.2.840.10008.5.1.4.1.1.2",  # CT Image Storage
            "MR": "1.2.840.10008.5.1.4.1.1.4",  # MR Image Storage
            "US": "1.2.840.10008.5.1.4.1.1.6.1", # Ultrasound Image Storage
            "DX": "1.2.840.10008.5.1.4.1.1.1.1", # Digital X-Ray Image Storage
            "NM": "1.2.840.10008.5.1.4.1.1.20",  # Nuclear Medicine Image Storage
            "PT": "1.2.840.10008.5.1.4.1.1.128", # Positron Emission Tomography Image Storage
            "RF": "1.2.840.10008.5.1.4.1.1.6",   # Radiofluoroscopic Image Storage
            "SC": "1.2.840.10008.5.1.4.1.1.7",   # Secondary Capture Image Storage
            "MG": "1.2.840.10008.5.1.4.1.1.1.2", # Mammography Image Storage
            "XA": "1.2.840.10008.5.1.4.1.1.12.1", # X-Ray Angiographic Image Storage
            "XC": "1.2.840.10008.5.1.4.1.1.1.3", # External Camera Photography Storage
        }
        return sop_class_mapping.get(modality, "1.2.840.10008.5.1.4.1.1.1")
    
    def _generate_accession_number(self) -> str:
        """Generate a realistic accession number."""
        # Generate accession number in format: YYYYMMDD-XXXX
        # Where YYYYMMDD is the current date and XXXX is a 4-digit sequence number
        date_prefix = datetime.now().strftime("%Y%m%d")
        sequence = str(uuid.uuid4().int % 10000).zfill(4)
        return f"{date_prefix}-{sequence}"
    
    def _generate_random_dob(self) -> str:
        """Generate a random patient date of birth."""
        import random
        from datetime import datetime, timedelta
        
        # Generate random age between 18 and 80 years
        current_date = datetime.now()
        min_age = 18
        max_age = 80
        
        # Calculate date range
        max_birth_date = current_date - timedelta(days=min_age * 365)
        min_birth_date = current_date - timedelta(days=max_age * 365)
        
        # Generate random date within range
        time_between = max_birth_date - min_birth_date
        days_between = time_between.days
        random_days = random.randint(0, days_between)
        
        random_birth_date = min_birth_date + timedelta(days=random_days)
        
        return random_birth_date.strftime("%Y%m%d")
    
    def get_generated_fields(self) -> Dict[str, Any]:
        """Get list of fields that were automatically generated."""
        return self.generated_fields.copy()
    
    def clear_generated_fields(self):
        """Clear the list of generated fields."""
        self.generated_fields.clear()
