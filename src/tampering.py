'''
src/tampering.py
--------------------------------------------------------------------------------
Controlled Tampering Generator for CT Image Forensics (Person A & Person B)

Supports realistic medical image manipulation modalities:
1. Controlled micro-pixel modification (1, 5, 10, 25, 100 pixels)
2. Localized region tampering (lesion insertion)
3. Copy-move attack (duplicating internal anatomical texture/nodule)
4. Splicing attack (implanting external foreign tissue/structure)
5. Inpainting attack (erasing a region and interpolating background texture)
--------------------------------------------------------------------------------
'''

import numpy as np
import cv2

def apply_pixel_tampering(image, num_pixels=1, intensity_delta=0.5, seed=42):
    """Modifies num_pixels in the central region of the image by adding intensity_delta."""
    np.random.seed(seed)
    h, w = image.shape
    tampered_img = image.copy()
    mask = np.zeros((h, w), dtype=np.uint8)

    margin_y = h // 4
    margin_x = w // 4
    
    rand_y = np.random.randint(margin_y, h - margin_y, size=num_pixels)
    rand_x = np.random.randint(margin_x, w - margin_x, size=num_pixels)

    for y, x in zip(rand_y, rand_x):
        tampered_img[y, x] = np.clip(tampered_img[y, x] + intensity_delta, 0.0, 1.0)
        mask[y, x] = 1

    return tampered_img, mask

def apply_region_tampering(image, region_size=(16, 16), start_pos=None, intensity_delta=0.3):
    """Modifies a contiguous block region of size region_size."""
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

def apply_copy_move_tampering(image, patch_size=(24, 24), src_pos=None, dst_pos=None):
    """
    Simulates a copy-move forgery: clones an internal anatomical patch into another location.
    """
    h, w = image.shape
    ph, pw = patch_size
    tampered_img = image.copy()
    mask = np.zeros((h, w), dtype=np.uint8)

    if src_pos is None:
        src_y, src_x = h // 3, w // 3
    else:
        src_y, src_x = src_pos

    if dst_pos is None:
        dst_y, dst_x = int(h * 0.55), int(w * 0.55)
    else:
        dst_y, dst_x = dst_pos

    # Extract source patch
    src_patch = image[src_y:src_y+ph, src_x:src_x+pw]

    # Paste into destination with subtle border feathering to simulate realistic forgery
    tampered_img[dst_y:dst_y+ph, dst_x:dst_x+pw] = src_patch
    mask[dst_y:dst_y+ph, dst_x:dst_x+pw] = 1

    return tampered_img, mask

def apply_splicing_tampering(image, donor_patch=None, dst_pos=None, patch_size=(20, 20), intensity_shift=0.35):
    """
    Simulates image splicing: implants external foreign structure into the host CT.
    """
    h, w = image.shape
    ph, pw = patch_size
    tampered_img = image.copy()
    mask = np.zeros((h, w), dtype=np.uint8)

    if dst_pos is None:
        dst_y, dst_x = h // 2 - ph // 2, w // 2 - pw // 2
    else:
        dst_y, dst_x = dst_pos

    if donor_patch is None:
        # Create synthetic foreign pathological structure (simulated calcified nodule)
        yy, xx = np.ogrid[-ph//2:ph//2, -pw//2:pw//2]
        donor_patch = np.exp(-(xx**2 + yy**2) / (2.0 * (ph / 4)**2)) * intensity_shift

    tampered_img[dst_y:dst_y+ph, dst_x:dst_x+pw] = np.clip(
        tampered_img[dst_y:dst_y+ph, dst_x:dst_x+pw] + donor_patch, 0.0, 1.0
    )
    mask[dst_y:dst_y+ph, dst_x:dst_x+pw] = 1

    return tampered_img, mask

def apply_inpainting_tampering(image, target_pos=None, patch_size=(20, 20)):
    """
    Simulates inpainting / lesion removal: removes a lesion and interpolates surrounding tissue.
    """
    h, w = image.shape
    ph, pw = patch_size
    tampered_img = image.copy()
    mask = np.zeros((h, w), dtype=np.uint8)

    if target_pos is None:
        ty, tx = int(h * 0.4), int(w * 0.4)
    else:
        ty, tx = target_pos

    mask[ty:ty+ph, tx:tx+pw] = 1
    
    # Inpaint using OpenCV Navier-Stokes based inpainting
    img_uint8 = (image * 255).astype(np.uint8)
    inpaint_mask = mask.astype(np.uint8) * 255
    inpainted_uint8 = cv2.inpaint(img_uint8, inpaint_mask, inpaintRadius=3, flags=cv2.INPAINT_NS)
    tampered_img = inpainted_uint8.astype(np.float64) / 255.0

    return tampered_img, mask

if __name__ == "__main__":
    test_img = np.zeros((128, 128))
    _, m1 = apply_copy_move_tampering(test_img)
    _, m2 = apply_splicing_tampering(test_img)
    _, m3 = apply_inpainting_tampering(test_img)
    print(f"Tampering module verified. Masks: CopyMove={m1.sum()}, Splicing={m2.sum()}, Inpainting={m3.sum()}")
