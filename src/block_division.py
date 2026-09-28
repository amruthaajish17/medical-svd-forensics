import numpy as np

def divide_into_blocks(image, block_size=16):
    """Splits a 2D image into non-overlapping blocks."""
    h, w = image.shape
    blocks = []
    positions = []
    for y in range(0, h - block_size + 1, block_size):
        for x in range(0, w - block_size + 1, block_size):
            blocks.append(image[y:y+block_size, x:x+block_size])
            positions.append((x, y))
    return blocks, positions

def blocks_to_image(block_values, positions, image_shape, block_size=16):
    """Maps feature values back to their block coordinates for heatmap visualization."""
    heatmap = np.zeros(image_shape, dtype=np.float64)
    for val, (x, y) in zip(block_values, positions):
        heatmap[y:y+block_size, x:x+block_size] = val
    return heatmap

if __name__ == "__main__":
    test_img = np.zeros((256, 256))
    blocks, pos = divide_into_blocks(test_img, 16)
    print(f"Number of blocks: {len(blocks)}, Block size: {blocks[0].shape}")
    print(f"First block position: {pos[0]}")