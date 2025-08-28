import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
from pathlib import Path
import io
import base64
import torch

# --- Project Root Definition ---
current_file = Path(__file__).resolve()
PROJECT_ROOT = current_file.parent.parent.parent

# Import your original utility functions
from utils.utils_inference import get_lmks_by_img, get_model_by_name
# Import new utility functions
from utils.image_processing_utils import calculate_symmetry_index, process_image_with_landmarks_and_symmetry
from utils.utils_landmarks import \
    get_five_landmarks_from_net  # Возможно, понадобится для calculate_symmetry_index напрямую

app = Flask(__name__)
CORS(app)

# Убедитесь, что папка utils является пакетом (содержит __init__.py)
(current_file.parent / 'utils' / '__init__.py').touch(exist_ok=True)

# --- Global Model Loading ---
face_alignment_model = None


def load_face_model():
    global face_alignment_model
    if face_alignment_model is None:
        try:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            app.logger.info(f"Loading face alignment model on device: {device}")
            face_alignment_model = get_model_by_name('WFLW', device=device)
            app.logger.info("Face alignment model loaded successfully.")
        except Exception as e:
            app.logger.error(f"Failed to load face alignment model: {e}")
            raise


@app.before_request
def before_first_request():
    if face_alignment_model is None:
        load_face_model()


@app.route('/')
def health_check():
    return jsonify({"status": "Server is running!", "project_root": str(PROJECT_ROOT)})


@app.route('/process-image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        try:
            in_memory_file = io.BytesIO()
            file.save(in_memory_file)
            data = np.frombuffer(in_memory_file.getvalue(), dtype=np.uint8)
            img = cv2.imdecode(data, cv2.IMREAD_COLOR)

            if img is None:
                return jsonify({"error": "Could not decode image. Is it a valid image format?"}), 400

            if face_alignment_model is None:
                raise Exception("Face alignment model is not loaded. Server might have failed to initialize.")

            # Получаем все ключевые точки
            all_lmks = get_lmks_by_img(face_alignment_model, img)

            # Рассчитываем индекс симметрии, используя полный набор точек
            symmetry_index = calculate_symmetry_index(all_lmks)

            # Получаем обработанное изображение с точками и линиями симметрии
            processed_image_stream = process_image_with_landmarks_and_symmetry(img, all_lmks)
            processed_image_stream.seek(0)

            # Кодируем изображение в base64 для передачи в JSON
            encoded_image = base64.b64encode(processed_image_stream.getvalue()).decode('utf-8')

            # Возвращаем JSON-ответ
            return jsonify({
                "processed_image": encoded_image,
                "symmetry_index": symmetry_index,
                "symmetry_description": f"Индекс симметрии вашего лица: {symmetry_index}%. " +
                                        ("Великолепная симметрия!" if symmetry_index > 90 else
                                         "Высокая симметрия." if symmetry_index > 75 else
                                         "Хорошая симметрия." if symmetry_index > 50 else
                                         "Есть заметные отклонения в симметрии.")
            })

        except Exception as e:
            app.logger.error(f"Error processing image: {e}")
            if app.debug:
                return jsonify({"error": f"An internal server error occurred: {str(e)}", "trace": str(e)}), 500
            else:
                return jsonify({"error": "An internal server error occurred. Please try again later."}), 500


if __name__ == '__main__':
    load_face_model()
    app.run(debug=True, host='0.0.0.0', port=5000)