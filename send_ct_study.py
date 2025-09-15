#!/usr/bin/env python3
"""
Direct script to send CT study to PACS
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pynetdicom import AE
from pynetdicom.sop_class import Verification, CTImageStorage
from pydicom.uid import ImplicitVRLittleEndian
from dicom_maker.study_manager import StudyManager

def send_ct_study():
    """Send the CT study to PACS."""
    study_uid = "1.2.826.0.1.3680043.8.498.87498894445841946927383241589332382278"
    
    print(f"Loading CT study {study_uid}...")
    study_manager = StudyManager("studies")
    study = study_manager.load_study(study_uid)
    
    if not study:
        print(f"Study {study_uid} not found!")
        return False
    
    print(f"Study loaded: {len(study.get('series', []))} series")
    
    # Count total images
    total_images = 0
    for series in study.get('series', []):
        total_images += len(series.get('images', []))
    print(f"Total images to send: {total_images}")
    
    # Create AE
    print("Creating AE...")
    ae = AE(ae_title='DICOM_MANAGER')
    ae.add_supported_context(Verification, ImplicitVRLittleEndian)
    ae.add_requested_context(Verification, ImplicitVRLittleEndian)
    ae.add_supported_context(CTImageStorage, ImplicitVRLittleEndian)
    ae.add_requested_context(CTImageStorage, ImplicitVRLittleEndian)
    
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
    
    print("C-ECHO successful! Sending CT study...")
    
    # Send all images in the study
    success_count = 0
    total_count = 0
    
    for series_idx, series in enumerate(study.get('series', []), 1):
        print(f"Sending series {series_idx} ({len(series.get('images', []))} images)...")
        
        for image_idx, image in enumerate(series.get('images', []), 1):
            total_count += 1
            print(f"  Sending image {image_idx}/{len(series.get('images', []))} (Instance {image.InstanceNumber})...")
            
            try:
                status = assoc.send_c_store(image)
                if status.Status == 0x0000:
                    success_count += 1
                    print(f"    ✓ Image {total_count} sent successfully")
                else:
                    print(f"    ✗ Image {total_count} failed with status: {status.Status}")
            except Exception as e:
                print(f"    ✗ Error sending image {total_count}: {e}")
    
    print(f"\nSent {success_count}/{total_count} images successfully")
    
    # Release association
    assoc.release()
    
    return success_count == total_count

if __name__ == "__main__":
    success = send_ct_study()
    if success:
        print("🎉 CT study sent successfully!")
    else:
        print("❌ Failed to send CT study")
        sys.exit(1)
