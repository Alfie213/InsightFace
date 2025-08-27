import os
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import cv2
import numpy as np
from pathlib import Path
import io
import torch  # Добавлено для проверки доступности CUDA, если необходимо

# --- Project Root Definition ---
current_file = Path(__file__).resolve()
# Assuming main.py is in src/server/, so PROJECT_ROOT is 2 levels up
PROJECT_ROOT = current_file.parent.parent.parent

# Import your utility functions
# Убедитесь, что папка utils является пакетом (содержит __init__.py)
from utils.utils_inference import get_lmks_by_img, get_model_by_name
from utils.utils_landmarks import show_landmarks_return_img  # Используем нашу новую функцию

app = Flask(__name__)
CORS(app)  # Включаем CORS для всех доменов

# Добавьте пустой __init__.py в папку src/server/utils/, если его там еще нет
# Это необходимо, чтобы Python рассматривал utils как пакет.
(current_file.parent / 'utils' / '__init__.py').touch(exist_ok=True)

# --- Global Model Loading (Оптимизация: загружаем модель один раз) ---
# Это поможет избежать повторной медленной загрузки модели при каждом запросе
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
            raise  # Перевыбрасываем исключение, так как без модели работать нельзя


# --- Flask Routes ---
@app.before_request
def before_first_request():
    # Загружаем модель при первом запросе (или при старте приложения, если нужно)
    # Для Gunicorn/WSGI серверов лучше загружать модель глобально при старте процесса
    # Но для app.run() в debug режиме это нормально.
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
            # Read the image file directly into OpenCV
            in_memory_file = io.BytesIO()
            file.save(in_memory_file)
            data = np.frombuffer(in_memory_file.getvalue(), dtype=np.uint8)
            img = cv2.imdecode(data, cv2.IMREAD_COLOR)

            if img is None:
                return jsonify({"error": "Could not decode image. Is it a valid image format?"}), 400

            # --- Image Processing Logic ---
            # Используем глобально загруженную модель
            if face_alignment_model is None:
                raise Exception("Face alignment model is not loaded. Server might have failed to initialize.")

            lmks = get_lmks_by_img(face_alignment_model, img)  # Передаем уже загруженную модель

            # Use the new function to get the processed image stream
            processed_image_stream = show_landmarks_return_img(img, lmks)

            # Send the processed image back
            processed_image_stream.seek(0)  # Сбрасываем указатель на начало потока
            return send_file(processed_image_stream, mimetype='image/jpeg')

        except Exception as e:
            app.logger.error(f"Error processing image: {e}")
            if app.debug:
                return jsonify({"error": f"An internal server error occurred: {str(e)}", "trace": str(e)}), 500
            else:
                return jsonify({"error": "An internal server error occurred. Please try again later."}), 500


if __name__ == '__main__':
    # Оптимизация: Загрузка модели при старте приложения, а не при первом запросе
    # Это важно, если используется Gunicorn или другой WSGI-сервер
    # Для разработки с app.run(debug=True) может быть достаточно before_first_request
    # Но для продакшена лучше загружать тут.
    load_face_model()
    app.run(debug=True, host='0.0.0.0', port=5000)