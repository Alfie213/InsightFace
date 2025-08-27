import cv2
from src.server.utils.utils_inference import get_lmks_by_img, get_model_by_name
from src.server.utils.utils_landmarks import show_landmarks

model = get_model_by_name('WFLW', device='cuda')

img = cv2.imread('./images/image.jpg')
lmks = get_lmks_by_img(model, img)
show_landmarks(img, lmks)
