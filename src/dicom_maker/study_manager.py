"""
Study Manager - Manages local DICOM studies

Copyright (c) 2025 flatmapit.com
Licensed under the MIT License
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import pydicom
from pydicom.dataset import Dataset


class StudyManager:
    """Manages local DICOM study storage and retrieval."""
    
    def __init__(self, base_dir: str = "studies"):
        """
        Initialize study manager.
        
        Args:
            base_dir: Base directory for storing studies
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # Create metadata file path
        self.metadata_file = self.base_dir / "studies.json"
        self._load_metadata()
    
    def _load_metadata(self):
        """Load study metadata from file."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}
    
    def _save_metadata(self):
        """Save study metadata to file."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def save_study(self, study_uid: str, study_data: Dict[str, Any]) -> bool:
        """
        Save a study to local storage.
        
        Args:
            study_uid: Study Instance UID
            study_data: Study data containing series and images
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Create study directory
            study_dir = self.base_dir / study_uid
            study_dir.mkdir(exist_ok=True)
            
            # Save each image as a DICOM file
            for series in study_data.get("series", []):
                series_dir = study_dir / f"series_{series['series_number']}"
                series_dir.mkdir(exist_ok=True)
                
                for image in series.get("images", []):
                    # Save as DICOM file
                    filename = f"{image.SOPInstanceUID}.dcm"
                    filepath = series_dir / filename
                    image.save_as(str(filepath))
            
            # Update metadata
            self.metadata[study_uid] = {
                "study_uid": study_uid,
                "patient_id": study_data.get("patient_id"),
                "patient_name": study_data.get("patient_name"),
                "study_date": study_data.get("study_date"),
                "series_count": len(study_data.get("series", [])),
                "total_images": sum(len(s.get("images", [])) for s in study_data.get("series", [])),
                "created_at": str(Path().cwd())
            }
            
            self._save_metadata()
            return True
            
        except Exception as e:
            print(f"Error saving study {study_uid}: {e}")
            return False
    
    def load_study(self, study_uid: str) -> Optional[Dict[str, Any]]:
        """
        Load a study from local storage.
        
        Args:
            study_uid: Study Instance UID
            
        Returns:
            Study data or None if not found
        """
        try:
            study_dir = self.base_dir / study_uid
            if not study_dir.exists():
                return None
            
            study_data = {
                "study_uid": study_uid,
                "series": []
            }
            
            # Load metadata
            if study_uid in self.metadata:
                study_data.update(self.metadata[study_uid])
            
            # Load series and images
            for series_dir in study_dir.iterdir():
                if series_dir.is_dir() and series_dir.name.startswith("series_"):
                    series_number = int(series_dir.name.split("_")[1])
                    series_data = {
                        "series_number": series_number,
                        "images": []
                    }
                    
                    # Load images in series
                    for dcm_file in series_dir.glob("*.dcm"):
                        try:
                            image = pydicom.dcmread(str(dcm_file), force=True)
                            series_data["images"].append(image)
                        except Exception as e:
                            print(f"Error loading {dcm_file}: {e}")
                    
                    study_data["series"].append(series_data)
            
            return study_data
            
        except Exception as e:
            print(f"Error loading study {study_uid}: {e}")
            return None
    
    def list_studies(self) -> Dict[str, Dict[str, Any]]:
        """
        List all local studies.
        
        Returns:
            Dictionary of study metadata
        """
        return self.metadata.copy()
    
    def delete_study(self, study_uid: str) -> bool:
        """
        Delete a study from local storage.
        
        Args:
            study_uid: Study Instance UID
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            study_dir = self.base_dir / study_uid
            if study_dir.exists():
                import shutil
                shutil.rmtree(study_dir)
            
            # Remove from metadata
            if study_uid in self.metadata:
                del self.metadata[study_uid]
                self._save_metadata()
            
            return True
            
        except Exception as e:
            print(f"Error deleting study {study_uid}: {e}")
            return False
    
    def get_study_info(self, study_uid: str) -> Optional[Dict[str, Any]]:
        """
        Get study information without loading full study data.
        
        Args:
            study_uid: Study Instance UID
            
        Returns:
            Study metadata or None if not found
        """
        return self.metadata.get(study_uid)
    
    def cleanup_empty_studies(self) -> int:
        """
        Remove studies that have no images.
        
        Returns:
            Number of studies cleaned up
        """
        cleaned = 0
        for study_uid in list(self.metadata.keys()):
            study_data = self.load_study(study_uid)
            if not study_data or not study_data.get("series"):
                if self.delete_study(study_uid):
                    cleaned += 1
        
        return cleaned
