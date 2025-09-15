#!/usr/bin/env python3
"""
Direct script to send mammography study to PACS
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pynetdicom import AE
from pynetdicom.sop_class import Verification, StorageServiceClass
from pydicom.uid import ImplicitVRLittleEndian
from dicom_maker.study_manager import StudyManager

def send_mammography_study():
    """Send the mammography study to PACS."""
    study_uid = "1.2.826.0.1.3680043.8.498.90408860879755762624080752483201339195"
    
    print(f"Loading study {study_uid}...")
    study_manager = StudyManager("studies")
    study = study_manager.load_study(study_uid)
    
    if not study:
        print(f"Study {study_uid} not found!")
        return False
    
    print(f"Study loaded: {len(study.get('series', []))} series")
    
    # Create AE
    print("Creating AE...")
    ae = AE(ae_title='DICOM_MANAGER')
    ae.add_supported_context(Verification, ImplicitVRLittleEndian)
    ae.add_requested_context(Verification, ImplicitVRLittleEndian)
    # Add storage service classes for different image types
    from pynetdicom.sop_class import CTImageStorage, DigitalMammographyXRayImageStorageForPresentation
    ae.add_supported_context(CTImageStorage, ImplicitVRLittleEndian)
    ae.add_requested_context(CTImageStorage, ImplicitVRLittleEndian)
    ae.add_supported_context(DigitalMammographyXRayImageStorageForPresentation, ImplicitVRLittleEndian)
    ae.add_requested_context(DigitalMammographyXRayImageStorageForPresentation, ImplicitVRLittleEndian)
    
    print("Associating with PACS1...")
    assoc = ae.associate('localhost', 4242, ae_title='PACS1')
    
    if not assoc.is_established:
        print("Association failed!")
        return False
    
    print("Association established! Sending C-ECHO...")
    status = assoc.send_c_echo()
    print(f"C-ECHO status: {status.Status}")
    
    if status.Status != 0x0000:
        print("C-ECHO failed!")
        assoc.release()
        return False
    
    print("C-ECHO successful! Sending study...")
    
    # Send all images in the study
    success_count = 0
    total_count = 0
    
    for series in study.get('series', []):
        for image in series.get('images', []):
            total_count += 1
            print(f"Sending image {image.SOPInstanceUID}...")
            
            try:
                status = assoc.send_c_store(image)
                if status.Status == 0x0000:
                    success_count += 1
                    print(f"✓ Image {total_count} sent successfully")
                else:
                    print(f"✗ Image {total_count} failed with status: {status.Status}")
            except Exception as e:
                print(f"✗ Error sending image {total_count}: {e}")
    
    print(f"Sent {success_count}/{total_count} images successfully")
    
    # Release association
    assoc.release()
    
    return success_count == total_count

if __name__ == "__main__":
    success = send_mammography_study()
    if success:
        print("🎉 Mammography study sent successfully!")
    else:
        print("❌ Failed to send mammography study")
        sys.exit(1)
