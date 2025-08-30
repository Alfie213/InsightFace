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
# ИЗМЕНЕНИЕ: Импортируем две НОВЫЕ функции отрисовки
from utils.image_processing_utils import calculate_symmetry_index, determine_face_shape, \
    draw_symmetry_analysis_image, draw_face_shape_analysis_image
from utils.utils_landmarks import get_five_landmarks_from_net

app = Flask(__name__)
CORS(app)

(current_file.parent / 'utils' / '__init__.py').touch(exist_ok=True)
(current_file.parent.parent / '__init__.py').touch(exist_ok=True)
(current_file.parent / '__init__.py').touch(exist_ok=True)

# --- Global Model Loading ---
face_alignment_model = None
face_cascade = None
HAARCASCADE_PATH = PROJECT_ROOT / 'src' / 'server' / 'utils' / 'haarcascade_frontalface_default.xml'
MODEL_DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
print(MODEL_DEVICE)


def load_face_model():
    global face_alignment_model, face_cascade, MODEL_DEVICE
    if face_alignment_model is None:
        try:
            app.logger.info(f"Loading face alignment model on device: {MODEL_DEVICE}")
            face_alignment_model = get_model_by_name('WFLW', device=MODEL_DEVICE)
            app.logger.info("Face alignment model loaded successfully.")
        except Exception as e:
            app.logger.error(f"Failed to load face alignment model: {e}")
            raise

    if face_cascade is None:
        if not HAARCASCADE_PATH.exists():
            app.logger.error(f"Haar Cascade XML file not found at: {HAARCASCADE_PATH}")
            raise FileNotFoundError(f"Haar Cascade XML file not found at: {HAARCASCADE_PATH}")
        face_cascade = cv2.CascadeClassifier(str(HAARCASCADE_PATH))
        if face_cascade.empty():
            app.logger.error("Failed to load Haar Cascade classifier.")
            raise RuntimeError("Failed to load Haar Cascade classifier.")
        app.logger.info("Haar Cascade classifier loaded successfully.")


@app.before_request
def before_first_request():
    if face_alignment_model is None or face_cascade is None:
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

    # --- СЕРВЕРНАЯ ВАЛИДАЦИЯ: ТИП И РАЗМЕР ФАЙЛА ---
    allowed_types = ['image/jpeg', 'image/png', 'image/gif']
    max_size_mb = 5
    max_size_bytes = max_size_mb * 1024 * 1024

    if file.content_type not in allowed_types:
        return jsonify({"error": f"Неподдерживаемый тип файла. Допустимы: {', '.join(allowed_types)}"}), 400

    if request.content_length is not None and request.content_length > max_size_bytes:
        return jsonify({"error": f"Файл слишком большой. Максимальный размер файла: {max_size_mb} MB."}), 400

    try:
        in_memory_file = io.BytesIO()
        file.save(in_memory_file)
        data = np.frombuffer(in_memory_file.getvalue(), dtype=np.uint8)
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)

        if img is None:
            is_success, buffer = cv2.imencode(".jpg", img)
            if not is_success:
                raise Exception("Could not encode original image to JPEG for error response.")
            encoded_original_image = base64.b64encode(buffer).decode('utf-8')

            return jsonify({
                "error": "Не удалось декодировать изображение. Возможно, файл поврежден или не является корректным изображением.",
                "original_image": encoded_original_image,
                "symmetry_image": encoded_original_image,
                "face_shape_image": encoded_original_image,
                "symmetry_data": {"index": 0.0, "description": "Анализ не выполнен."},
                "face_shape": {"name": "Неопределенная форма", "description": "Анализ не выполнен."}
            }), 400

        if face_alignment_model is None or face_cascade is None:
            raise Exception("Models are not loaded. Server might have failed to initialize.")

        # --- ОБНАРУЖЕНИЕ ЛИЦА С ПОМОЩЬЮ HAAR CASCADE ---
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) == 0:
            is_success, buffer = cv2.imencode(".jpg", img)
            if not is_success:
                raise Exception("Could not encode original image to JPEG for error response.")
            encoded_original_image = base64.b64encode(buffer).decode('utf-8')

            return jsonify({
                "error": "Лицо не обнаружено на изображении. Пожалуйста, попробуйте другую фотографию (убедитесь, что лицо хорошо видно).",
                "original_image": encoded_original_image,
                "symmetry_image": encoded_original_image,
                "face_shape_image": encoded_original_image,
                "symmetry_data": {"index": 0.0, "description": "Лицо не обнаружено для анализа симметрии."},
                "face_shape": {"name": "Неопределенная форма", "description": "Лицо не обнаружено для анализа формы."}
            }), 422

        # Получаем все ключевые точки от WFLW модели
        all_lmks = get_lmks_by_img(face_alignment_model, img, device=MODEL_DEVICE)

        if all_lmks is None or len(all_lmks) == 0:
            is_success, buffer = cv2.imencode(".jpg", img)
            if not is_success:
                raise Exception("Could not encode original image to JPEG for error response.")
            encoded_original_image = base64.b64encode(buffer).decode('utf-8')

            return jsonify({
                "error": "Лицо обнаружено, но модель для ключевых точек не смогла его обработать. Пожалуйста, попробуйте другую фотографию.",
                "original_image": encoded_original_image,
                "symmetry_image": encoded_original_image,
                "face_shape_image": encoded_original_image,
                "symmetry_data": {"index": 0.0, "description": "Модель ключевых точек не смогла обработать лицо."},
                "face_shape": {"name": "Неопределенная форма",
                               "description": "Модель ключевых точек не смогла обработать лицо."}
            }), 422

        # --- АНАЛИЗ СИММЕТРИИ ---
        symmetry_index = calculate_symmetry_index(all_lmks, img_width=img.shape[1])
        # ИЗМЕНЕНИЕ: Вызов новой функции для отрисовки симметрии
        symmetry_image_stream = draw_symmetry_analysis_image(img, all_lmks)
        symmetry_image_stream.seek(0)
        encoded_symmetry_image = base64.b64encode(symmetry_image_stream.getvalue()).decode('utf-8')

        symmetry_data_response = {
            "index": symmetry_index,
            "description": f"Индекс симметрии вашего лица: {symmetry_index}%. " +
                           ("Великолепная симметрия! Ваше лицо очень гармонично." if symmetry_index > 90 else
                            "Высокая симметрия. У вас очень сбалансированные черты лица." if symmetry_index > 75 else
                            "Хорошая симметрия. Черты лица достаточно гармоничны." if symmetry_index > 50 else
                            "Есть заметные отклонения в симметрии. Возможно, стоит обратить внимание на некоторые детали.")
        }

        # --- АНАЛИЗ ФОРМЫ ЛИЦА ---
        face_shape_data = determine_face_shape(all_lmks)
        # ИЗМЕНЕНИЕ: Вызов новой функции для отрисовки формы
        face_shape_image_stream = draw_face_shape_analysis_image(
            img,
            all_lmks,
            shape_measurement_points=face_shape_data.get('measurement_points')
        )
        face_shape_image_stream.seek(0)
        encoded_face_shape_image = base64.b64encode(face_shape_image_stream.getvalue()).decode('utf-8')

        face_shape_response = {
            "name": face_shape_data.get("shape_name"),
            "description": face_shape_data.get("description")
        }

        # --- ФИНАЛЬНЫЙ ОТВЕТ ---
        return jsonify({
            "original_image": base64.b64encode(in_memory_file.getvalue()).decode('utf-8'),
            "symmetry_image": encoded_symmetry_image,
            "face_shape_image": encoded_face_shape_image,
            "symmetry_data": symmetry_data_response,
            "face_shape": face_shape_response
        })

    except Exception as e:
        app.logger.error(f"Error processing image: {e}")
        encoded_original_image = ""
        if 'img' in locals() and img is not None:
            is_success, buffer = cv2.imencode(".jpg", img)
            if is_success:
                encoded_original_image = base64.b64encode(buffer).decode('utf-8')

        if app.debug:
            return jsonify({
                "error": f"Произошла внутренняя ошибка сервера: {str(e)}",
                "trace": str(e),
                "original_image": encoded_original_image,
                "symmetry_image": encoded_original_image,
                "face_shape_image": encoded_original_image
            }), 500
        else:
            return jsonify({
                "error": "Произошла внутренняя ошибка сервера. Пожалуйста, попробуйте еще раз.",
                "original_image": encoded_original_image,
                "symmetry_image": encoded_original_image,
                "face_shape_image": encoded_original_image
            }), 500


if __name__ == '__main__':
    load_face_model()
    app.run(debug=True, host='0.0.0.0', port=5000)