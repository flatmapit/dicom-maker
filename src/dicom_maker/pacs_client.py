"""
PACS Client - Handles DICOM network communication
"""

import logging
from typing import List, Optional, Dict, Any
from pynetdicom import AE
from pynetdicom.sop_class import (
    Verification, StorageServiceClass,
    CTImageStorage, MRImageStorage, ComputedRadiographyImageStorage
)
from pydicom.dataset import Dataset


class PACSClient:
    """Client for communicating with PACS systems."""
    
    def __init__(self, host: str, port: int, aec: str, aet: str):
        """
        Initialize PACS client.
        
        Args:
            host: PACS host address
            port: PACS port number
            aec: Application Entity Caller (our AE title)
            aet: Application Entity Title (PACS AE title)
        """
        self.host = host
        self.port = port
        self.aec = aec
        self.aet = aet
        self.ae = None
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _create_ae(self) -> AE:
        """Create and configure Application Entity."""
        # Always create a new AE to avoid UID issues
        # Ensure AE titles are strings and properly formatted
        aec_title = str(self.aec).strip()
        if len(aec_title) > 16:
            aec_title = aec_title[:16]
        
        ae = AE(ae_title=aec_title)
        
        # Add requested presentation contexts
        from pydicom.uid import ImplicitVRLittleEndian
        
        # Add verification context (both supported and requested)
        ae.add_supported_context(Verification, ImplicitVRLittleEndian)
        ae.add_requested_context(Verification, ImplicitVRLittleEndian)
        
        # Add storage contexts (both supported and requested)
        ae.add_supported_context(StorageServiceClass, ImplicitVRLittleEndian)
        ae.add_requested_context(StorageServiceClass, ImplicitVRLittleEndian)
        ae.add_supported_context(CTImageStorage, ImplicitVRLittleEndian)
        ae.add_requested_context(CTImageStorage, ImplicitVRLittleEndian)
        ae.add_supported_context(MRImageStorage, ImplicitVRLittleEndian)
        ae.add_requested_context(MRImageStorage, ImplicitVRLittleEndian)
        ae.add_supported_context(ComputedRadiographyImageStorage, ImplicitVRLittleEndian)
        ae.add_requested_context(ComputedRadiographyImageStorage, ImplicitVRLittleEndian)
        
        return ae
    
    def verify_connection(self) -> bool:
        """
        Verify connection to PACS using C-ECHO.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            ae = self._create_ae()
            
            # Associate with PACS
            aet_title = str(self.aet).strip()
            if len(aet_title) > 16:
                aet_title = aet_title[:16]
            assoc = ae.associate(self.host, self.port, ae_title=aet_title)
            
            if assoc.is_established:
                # Send C-ECHO request
                status = assoc.send_c_echo()
                
                # Release association
                assoc.release()
                
                if status.Status == 0x0000:  # Success
                    self.logger.info("C-ECHO successful")
                    return True
                else:
                    self.logger.error(f"C-ECHO failed with status: {status.Status}")
                    return False
            else:
                self.logger.error("Failed to establish association")
                return False
                
        except Exception as e:
            self.logger.error(f"Connection verification failed: {e}")
            return False
    
    def send_study(self, study_data: Dict[str, Any]) -> bool:
        """
        Send a DICOM study to PACS using C-STORE.
        
        Args:
            study_data: Study data containing series and images
            
        Returns:
            True if all images sent successfully, False otherwise
        """
        try:
            ae = self._create_ae()
            
            # Associate with PACS
            aet_title = str(self.aet).strip()
            if len(aet_title) > 16:
                aet_title = aet_title[:16]
            assoc = ae.associate(self.host, self.port, ae_title=aet_title)
            
            if not assoc.is_established:
                self.logger.error("Failed to establish association")
                return False
            
            success_count = 0
            total_count = 0
            
            # Send all images in the study
            for series in study_data.get("series", []):
                for image in series.get("images", []):
                    total_count += 1
                    
                    # Send C-STORE request
                    status = assoc.send_c_store(image)
                    
                    if status.Status == 0x0000:  # Success
                        success_count += 1
                        self.logger.info(f"Sent image {image.SOPInstanceUID}")
                    else:
                        self.logger.error(f"Failed to send image {image.SOPInstanceUID}: {status.Status}")
            
            # Release association
            assoc.release()
            
            success = success_count == total_count
            if success:
                self.logger.info(f"Successfully sent {success_count}/{total_count} images")
            else:
                self.logger.error(f"Only sent {success_count}/{total_count} images")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to send study: {e}")
            return False
    
    def send_image(self, image_dataset: Dataset) -> bool:
        """
        Send a single DICOM image to PACS.
        
        Args:
            image_dataset: DICOM dataset to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            ae = self._create_ae()
            
            # Associate with PACS
            aet_title = str(self.aet).strip()
            if len(aet_title) > 16:
                aet_title = aet_title[:16]
            assoc = ae.associate(self.host, self.port, ae_title=aet_title)
            
            if not assoc.is_established:
                self.logger.error("Failed to establish association")
                return False
            
            # Send C-STORE request
            status = assoc.send_c_store(image_dataset)
            
            # Release association
            assoc.release()
            
            if status.Status == 0x0000:  # Success
                self.logger.info(f"Successfully sent image {image_dataset.SOPInstanceUID}")
                return True
            else:
                self.logger.error(f"Failed to send image: {status.Status}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to send image: {e}")
            return False
