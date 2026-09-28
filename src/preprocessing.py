import numpy as np
import pydicom

def load_dicom(file_path):
    """Loads a DICOM file and returns the 2D pixel array."""
    dicom_data = pydicom.dcmread(file_path)
    return dicom_data.pixel_array.astype(np.float64)

def normalize_image(img):
    """Normalizes image pixels to a 0-1 range."""
    img_min = img.min()
    img_max = img.max()
    if img_max - img_min == 0:
        return img
    return (img - img_min) / (img_max - img_min)

if __name__ == "__main__":
    print("preprocessing.py module ready.")