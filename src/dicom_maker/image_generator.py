"""
Realistic DICOM Image Generator
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Optional, Dict, Any
import random
import math


class DICOMImageGenerator:
    """Generates realistic DICOM images using dicom-fabricator style."""
    
    def __init__(self):
        """Initialize the image generator."""
        self.anatomical_regions = {
            "chest": self._generate_chest_image,
            "abdomen": self._generate_abdomen_image,
            "pelvis": self._generate_pelvis_image,
            "head": self._generate_head_image,
            "spine": self._generate_spine_image,
            "limb": self._generate_limb_image,
        }
    
    def generate_image(self, width: int = 512, height: int = 512, 
                      modality: str = "CR", anatomical_region: str = "chest",
                      **kwargs) -> np.ndarray:
        """
        Generate a realistic DICOM image.
        
        Args:
            width: Image width in pixels
            height: Image height in pixels
            modality: DICOM modality (CR, CT, MR, US, etc.)
            anatomical_region: Anatomical region to simulate
            **kwargs: Additional parameters for image generation
            
        Returns:
            Generated image as numpy array
        """
        if anatomical_region in self.anatomical_regions:
            return self.anatomical_regions[anatomical_region](width, height, modality, **kwargs)
        else:
            return self._generate_generic_image(width, height, modality, **kwargs)
    
    def _generate_chest_image(self, width: int, height: int, modality: str, **kwargs) -> np.ndarray:
        """Generate a chest X-ray like image."""
        image = np.zeros((height, width), dtype=np.uint16)
        
        # Add background noise
        image += np.random.normal(1000, 50, (height, width)).astype(np.uint16)
        
        # Add rib structures
        for i in range(5):
            y = height // 6 + i * height // 6
            self._add_rib_structure(image, y, width, height)
        
        # Add heart shadow
        heart_center_x = width // 2 + random.randint(-20, 20)
        heart_center_y = height // 2 + random.randint(-10, 10)
        heart_radius = random.randint(30, 50)
        self._add_heart_shadow(image, heart_center_x, heart_center_y, heart_radius)
        
        # Add lung fields
        self._add_lung_fields(image, width, height)
        
        # Add clavicles
        self._add_clavicles(image, width, height)
        
        return self._apply_modality_characteristics(image, modality)
    
    def _generate_abdomen_image(self, width: int, height: int, modality: str, **kwargs) -> np.ndarray:
        """Generate an abdominal image."""
        image = np.zeros((height, width), dtype=np.uint16)
        
        # Add background
        image += np.random.normal(800, 30, (height, width)).astype(np.uint16)
        
        # Add spine
        spine_x = width // 2
        spine_width = random.randint(15, 25)
        image[:, spine_x-spine_width//2:spine_x+spine_width//2] += 200
        
        # Add soft tissue structures
        for i in range(3):
            y = height // 4 + i * height // 4
            self._add_soft_tissue_structure(image, y, width, height)
        
        # Add bowel gas patterns
        self._add_bowel_gas(image, width, height)
        
        return self._apply_modality_characteristics(image, modality)
    
    def _generate_pelvis_image(self, width: int, height: int, modality: str, **kwargs) -> np.ndarray:
        """Generate a pelvic image."""
        image = np.zeros((height, width), dtype=np.uint16)
        
        # Add background
        image += np.random.normal(900, 40, (height, width)).astype(np.uint16)
        
        # Add pelvic bones
        self._add_pelvic_bones(image, width, height)
        
        # Add soft tissue
        self._add_pelvic_soft_tissue(image, width, height)
        
        return self._apply_modality_characteristics(image, modality)
    
    def _generate_head_image(self, width: int, height: int, modality: str, **kwargs) -> np.ndarray:
        """Generate a head/CT image."""
        image = np.zeros((height, width), dtype=np.uint16)
        
        # Add background
        image += np.random.normal(100, 20, (height, width)).astype(np.uint16)
        
        # Add skull
        center_x, center_y = width // 2, height // 2
        skull_radius = min(width, height) // 3
        self._add_skull(image, center_x, center_y, skull_radius)
        
        # Add brain structures
        self._add_brain_structures(image, center_x, center_y, skull_radius)
        
        return self._apply_modality_characteristics(image, modality)
    
    def _generate_spine_image(self, width: int, height: int, modality: str, **kwargs) -> np.ndarray:
        """Generate a spine image."""
        image = np.zeros((height, width), dtype=np.uint16)
        
        # Add background
        image += np.random.normal(1000, 50, (height, width)).astype(np.uint16)
        
        # Add vertebral column
        spine_x = width // 2
        for i in range(7):  # 7 cervical vertebrae
            y = height // 8 + i * height // 8
            self._add_vertebra(image, spine_x, y, width // 8)
        
        # Add soft tissue
        self._add_spinal_soft_tissue(image, width, height)
        
        return self._apply_modality_characteristics(image, modality)
    
    def _generate_limb_image(self, width: int, height: int, modality: str, **kwargs) -> np.ndarray:
        """Generate a limb image."""
        image = np.zeros((height, width), dtype=np.uint16)
        
        # Add background
        image += np.random.normal(1200, 60, (height, width)).astype(np.uint16)
        
        # Add bone structure
        bone_center_x = width // 2
        bone_width = random.randint(20, 40)
        image[:, bone_center_x-bone_width//2:bone_center_x+bone_width//2] += 300
        
        # Add soft tissue
        self._add_limb_soft_tissue(image, width, height)
        
        return self._apply_modality_characteristics(image, modality)
    
    def _generate_generic_image(self, width: int, height: int, modality: str, **kwargs) -> np.ndarray:
        """Generate a generic medical image."""
        image = np.zeros((height, width), dtype=np.uint16)
        
        # Add background noise
        image += np.random.normal(1000, 100, (height, width)).astype(np.uint16)
        
        # Add some random structures
        for _ in range(random.randint(3, 8)):
            x = random.randint(0, width)
            y = random.randint(0, height)
            radius = random.randint(10, 30)
            intensity = random.randint(100, 300)
            self._add_circular_structure(image, x, y, radius, intensity)
        
        return self._apply_modality_characteristics(image, modality)
    
    def _add_rib_structure(self, image: np.ndarray, y: int, width: int, height: int):
        """Add rib-like structures to the image."""
        for i in range(3):
            x = width // 4 + i * width // 4
            radius = random.randint(15, 25)
            intensity = random.randint(50, 100)
            self._add_circular_structure(image, x, y, radius, intensity)
    
    def _add_heart_shadow(self, image: np.ndarray, center_x: int, center_y: int, radius: int):
        """Add heart shadow to the image."""
        y, x = np.ogrid[:image.shape[0], :image.shape[1]]
        mask = (x - center_x)**2 + (y - center_y)**2 <= radius**2
        image[mask] += random.randint(80, 120)
    
    def _add_lung_fields(self, image: np.ndarray, width: int, height: int):
        """Add lung field structures."""
        # Left lung
        left_lung_x = width // 4
        left_lung_y = height // 2
        left_lung_radius = width // 6
        self._add_circular_structure(image, left_lung_x, left_lung_y, left_lung_radius, -50)
        
        # Right lung
        right_lung_x = 3 * width // 4
        right_lung_y = height // 2
        right_lung_radius = width // 6
        self._add_circular_structure(image, right_lung_x, right_lung_y, right_lung_radius, -50)
    
    def _add_clavicles(self, image: np.ndarray, width: int, height: int):
        """Add clavicle structures."""
        clavicle_y = height // 8
        # Left clavicle
        for x in range(width // 4, 3 * width // 4):
            if random.random() < 0.3:
                image[clavicle_y:clavicle_y+3, x] += 100
    
    def _add_soft_tissue_structure(self, image: np.ndarray, y: int, width: int, height: int):
        """Add soft tissue structures."""
        for x in range(0, width, 20):
            if random.random() < 0.4:
                radius = random.randint(5, 15)
                intensity = random.randint(30, 80)
                self._add_circular_structure(image, x, y, radius, intensity)
    
    def _add_bowel_gas(self, image: np.ndarray, width: int, height: int):
        """Add bowel gas patterns."""
        for _ in range(random.randint(5, 15)):
            x = random.randint(0, width)
            y = random.randint(height // 4, 3 * height // 4)
            radius = random.randint(8, 20)
            intensity = -random.randint(50, 100)
            self._add_circular_structure(image, x, y, radius, intensity)
    
    def _add_pelvic_bones(self, image: np.ndarray, width: int, height: int):
        """Add pelvic bone structures."""
        # Left ilium
        left_ilium_x = width // 4
        left_ilium_y = height // 2
        self._add_circular_structure(image, left_ilium_x, left_ilium_y, width // 8, 200)
        
        # Right ilium
        right_ilium_x = 3 * width // 4
        right_ilium_y = height // 2
        self._add_circular_structure(image, right_ilium_x, right_ilium_y, width // 8, 200)
        
        # Sacrum
        sacrum_x = width // 2
        sacrum_y = height // 2
        image[sacrum_y-20:sacrum_y+20, sacrum_x-10:sacrum_x+10] += 150
    
    def _add_pelvic_soft_tissue(self, image: np.ndarray, width: int, height: int):
        """Add pelvic soft tissue."""
        for _ in range(random.randint(8, 20)):
            x = random.randint(0, width)
            y = random.randint(height // 4, 3 * height // 4)
            radius = random.randint(10, 25)
            intensity = random.randint(20, 60)
            self._add_circular_structure(image, x, y, radius, intensity)
    
    def _add_skull(self, image: np.ndarray, center_x: int, center_y: int, radius: int):
        """Add skull structure."""
        y, x = np.ogrid[:image.shape[0], :image.shape[1]]
        mask = (x - center_x)**2 + (y - center_y)**2 <= radius**2
        image[mask] += 200
        
        # Add inner skull
        inner_radius = radius - 20
        inner_mask = (x - center_x)**2 + (y - center_y)**2 <= inner_radius**2
        image[inner_mask] -= 100
    
    def _add_brain_structures(self, image: np.ndarray, center_x: int, center_y: int, radius: int):
        """Add brain structures."""
        # Add ventricles
        ventricle_y = center_y
        ventricle_x = center_x
        ventricle_radius = radius // 4
        y, x = np.ogrid[:image.shape[0], :image.shape[1]]
        ventricle_mask = (x - ventricle_x)**2 + (y - ventricle_y)**2 <= ventricle_radius**2
        image[ventricle_mask] -= 50
    
    def _add_vertebra(self, image: np.ndarray, center_x: int, center_y: int, width: int):
        """Add a vertebra structure."""
        vertebra_height = 20
        image[center_y-vertebra_height//2:center_y+vertebra_height//2, 
              center_x-width//2:center_x+width//2] += 150
    
    def _add_spinal_soft_tissue(self, image: np.ndarray, width: int, height: int):
        """Add spinal soft tissue."""
        for _ in range(random.randint(10, 25)):
            x = random.randint(0, width)
            y = random.randint(0, height)
            radius = random.randint(8, 20)
            intensity = random.randint(30, 70)
            self._add_circular_structure(image, x, y, radius, intensity)
    
    def _add_limb_soft_tissue(self, image: np.ndarray, width: int, height: int):
        """Add limb soft tissue."""
        for _ in range(random.randint(15, 30)):
            x = random.randint(0, width)
            y = random.randint(0, height)
            radius = random.randint(5, 15)
            intensity = random.randint(20, 50)
            self._add_circular_structure(image, x, y, radius, intensity)
    
    def _add_circular_structure(self, image: np.ndarray, center_x: int, center_y: int, 
                               radius: int, intensity: int):
        """Add a circular structure to the image."""
        y, x = np.ogrid[:image.shape[0], :image.shape[1]]
        mask = (x - center_x)**2 + (y - center_y)**2 <= radius**2
        image[mask] += intensity
    
    def _apply_modality_characteristics(self, image: np.ndarray, modality: str) -> np.ndarray:
        """Apply modality-specific characteristics to the image."""
        if modality == "CT":
            # CT images typically have higher contrast and different intensity ranges
            image = np.clip(image, 0, 4095)  # 12-bit CT
            image = (image / 4095 * 65535).astype(np.uint16)
        elif modality == "MR":
            # MR images have different intensity characteristics
            image = np.clip(image, 0, 4095)
            image = (image / 4095 * 65535).astype(np.uint16)
        elif modality == "US":
            # Ultrasound images have different characteristics
            image = np.clip(image, 0, 255)
            image = (image * 257).astype(np.uint16)  # Scale to 16-bit
        else:
            # Default for CR, DX, etc.
            image = np.clip(image, 0, 65535)
        
        return image.astype(np.uint16)
