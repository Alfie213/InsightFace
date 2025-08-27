import cv2
from pathlib import Path

# --- Project Root Definition ---
current_file = Path(__file__).resolve()
PROJECT_ROOT = current_file.parent.parent.parent # Move up 3 levels from main.py to project root

images_dir = PROJECT_ROOT / 'images'
image_path = images_dir / 'image.png'

from utils.utils_inference import get_lmks_by_img, get_model_by_name
from utils.utils_landmarks import show_landmarks

# --- Main Logic ---
try:
    img = cv2.imread(str(image_path))
    if img is None:
        print(f"Error: Could not load image from path: {image_path}")
    else:
        model = get_model_by_name('WFLW', device='cuda')
        lmks = get_lmks_by_img(model, img)
        show_landmarks(img, lmks)

except FileNotFoundError:
    print(f"Error: Image file not found at path: {image_path}")
except Exception as e:
    print(f"An error occurred: {e}")