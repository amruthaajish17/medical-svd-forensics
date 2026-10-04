'''
src/tampering.py
--------------------------------------------------------------------------------
Controlled Tampering Generator for CT Image Forensics (Person A - Day 2/3)

Supports controlled local modifications:
- N-pixel random noise/intensity shift (1, 5, 10, 25, 100 pixels)
- Square block region modification / copy-move / splicing stub
--------------------------------------------------------------------------------
'''

import numpy as np

def apply_pixel_tampering(image, num_pixels=1, intensity_delta=0.5, seed=42):
    """
    Modifies num_pixels in the central region of the image by adding intensity_delta.
    Returns:
        tampered_image: Image with modified pixel values (clipped to [0, 1])
        ground_truth_mask: Binary mask of modified pixels (1 at modified pixels, 0 elsewhere)
    """
    np.random.seed(seed)
    h, w = image.shape
    tampered_img = image.copy()
    mask = np.zeros((h, w), dtype=np.uint8)

    # Constrain modification within central region [25% to 75%] to mimic lesion insertion
    margin_y = h // 4
    margin_x = w // 4
    
    rand_y = np.random.randint(margin_y, h - margin_y, size=num_pixels)
    rand_x = np.random.randint(margin_x, w - margin_x, size=num_pixels)

    for y, x in zip(rand_y, rand_x):
        # Apply intensity modification
        tampered_img[y, x] = np.clip(tampered_img[y, x] + intensity_delta, 0.0, 1.0)
        mask[y, x] = 1

    return tampered_img, mask

def apply_region_tampering(image, region_size=(16, 16), start_pos=None, intensity_delta=0.3):
    """
    Modifies a contiguous block region of size region_size.
    Returns:
        tampered_image: Image with modified region
        ground_truth_mask: Binary mask of modified block (1 at region, 0 elsewhere)
    """
    h, w = image.shape
    rh, rw = region_size
    tampered_img = image.copy()
    mask = np.zeros((h, w), dtype=np.uint8)

    if start_pos is None:
        start_y = h // 2 - rh // 2
        start_x = w // 2 - rw // 2
    else:
        start_y, start_x = start_pos

    end_y = min(start_y + rh, h)
    end_x = min(start_x + rw, w)

    tampered_img[start_y:end_y, start_x:end_x] = np.clip(
        tampered_img[start_y:end_y, start_x:end_x] + intensity_delta, 0.0, 1.0
    )
    mask[start_y:end_y, start_x:end_x] = 1

    return tampered_img, mask

if __name__ == "__main__":
    test_img = np.zeros((128, 128))
    t_img, mask = apply_pixel_tampering(test_img, num_pixels=10)
    print(f"Tampering module ready. Modified pixels: {np.sum(mask)}")
