import cv2
import numpy as np
import io
from .utils_landmarks import set_circles_on_img, get_five_landmarks_from_net


def calculate_symmetry_index(all_lmks, img_width=1):
    """
    Рассчитывает улучшенный индекс симметрии лица на основе 5 ключевых точек.
    Использует отклонение симметричных точек от центральной оси.

    :param all_lmks: Полный набор ключевых точек, возвращаемых моделью (например, 98 точек).
    :param img_width: Ширина изображения для нормализации расстояний.
    :return: Процент симметрии (от 0 до 100).
    """
    if all_lmks is None or len(all_lmks) == 0:
        return 0.0

    try:
        five_lmks = get_five_landmarks_from_net(all_lmks)
    except NotImplementedError:
        print(
            f"Warning: get_five_landmarks_from_net does not support {len(all_lmks)} landmarks for symmetry calculation.")
        return 0.0

    if len(five_lmks) < 5:
        return 0.0

    le, re, nose, ml, mr = five_lmks[0], five_lmks[1], five_lmks[2], five_lmks[3], five_lmks[4]

    center_x = (le[0] + re[0]) / 2

    dist_le_x = abs(le[0] - center_x)
    dist_re_x = abs(re[0] - center_x)
    dist_ml_x = abs(ml[0] - center_x)
    dist_mr_x = abs(mr[0] - center_x)

    diff_eyes_x = abs(dist_le_x - dist_re_x)
    diff_mouth_x = abs(dist_ml_x - dist_mr_x)

    avg_x_deviation = (diff_eyes_x + diff_mouth_x) / 2

    y_diff_eyes = abs(le[1] - re[1])
    y_diff_mouth = abs(ml[1] - mr[1])

    avg_y_deviation = (y_diff_eyes + y_diff_mouth) / 2

    eye_distance = np.linalg.norm(le - re)
    if eye_distance == 0:
        return 0.0

    normalized_total_deviation = (avg_x_deviation + avg_y_deviation) / eye_distance

    max_deviation_threshold = 0.4

    symmetry_percentage = max(0, 100 - (normalized_total_deviation / max_deviation_threshold) * 100)

    return round(symmetry_percentage, 2)


def determine_face_shape(all_lmks):
    """
    Определяет форму лица на основе 98 ключевых точек WFLW с использованием
    улучшенной, более строгой и иерархической логики.

    :param all_lmks: Полный набор из 98 ключевых точек лица от модели WFLW.
    :return: Словарь с 'shape_name' и 'description'.
    """
    if all_lmks is None or len(all_lmks) != 98:
        return {
            "shape_name": "Неопределенная форма лица",
            "description": "Недостаточно данных для определения формы. Убедитесь, что модель обнаружила 98 ключевых точек."
        }

    # --- 1. ИЗВЛЕЧЕНИЕ КЛЮЧЕВЫХ ТОЧЕК (остается без изменений) ---
    face_height = abs(all_lmks[8][1] - all_lmks[54][1])
    cheekbone_width = abs(all_lmks[16][0] - all_lmks[0][0])
    forehead_width = abs(all_lmks[42][0] - all_lmks[33][0])
    jaw_width = abs(all_lmks[12][0] - all_lmks[4][0])

    if cheekbone_width == 0 or face_height == 0:
        return {
            "shape_name": "Неопределенная форма лица",
            "description": "Не удалось вычислить базовые пропорции лица."
        }

    # --- 2. ВЫЧИСЛЕНИЕ КЛЮЧЕВЫХ СООТНОШЕНИЙ ---
    # Соотношение высоты к ширине (для определения "длинных" и "коротких" лиц)
    aspect_ratio = face_height / cheekbone_width

    # Нормализованные ширины для сравнения (делим на самую широкую часть - скулы)
    forehead_norm = forehead_width / cheekbone_width
    jaw_norm = jaw_width / cheekbone_width

    # --- ДЛЯ ОТЛАДКИ: Раскомментируйте, чтобы видеть значения для каждой фотографии ---
    # print(f"H: {face_height:.1f}, CW: {cheekbone_width:.1f}, FW: {forehead_width:.1f}, JW: {jaw_width:.1f}")
    # print(f"Aspect Ratio: {aspect_ratio:.2f}")
    # print(f"Forehead Norm: {forehead_norm:.2f}, Jaw Norm: {jaw_norm:.2f}")
    # ---------------------------------------------------------------------------------

    shape_name = "Неопределенная форма лица"
    description = "Не удалось точно определить форму вашего лица. Форма может быть смешанной или требует более детального изучения."

    # --- 3. НОВЫЙ АЛГОРИТМ ПРИНЯТИЯ РЕШЕНИЙ (от самого редкого к самому общему) ---

    # 1. Грушевидное лицо: Челюсть заметно шире лба, скулы посередине.
    # Это редкая форма, поэтому проверяем ее первой.
    if jaw_width > forehead_width and jaw_width > cheekbone_width:
        shape_name = "Грушевидное лицо"
        description = "У вас узкий лоб и широкая нижняя часть лица (подбородок). Рекомендуются прически с объемом в верхней части головы для создания баланса."

    # 2. Треугольное лицо (Сердце): Лоб самый широкий, челюсть самая узкая и заостренная.
    # Условие стало гораздо строже: лоб должен быть шире скул, а челюсть - значительно уже.
    elif forehead_width > cheekbone_width and jaw_norm < 0.88:
        shape_name = "Треугольное лицо (сердце)"
        description = "У вас широкий лоб, который сужается к изящному, узкому подбородку. Хорошо подходят прически с объемом в нижней части лица, чтобы сбалансировать пропорции."

    # 3. Квадратное лицо: "Короткое" лицо, у которого все ширины почти равны.
    # aspect_ratio ~ 1 и очень широкая, "квадратная" челюсть.
    elif aspect_ratio < 1.15 and jaw_norm > 0.95 and forehead_norm > 0.95:
        shape_name = "Квадратное лицо"
        description = "У вас широкий лоб и выраженная, почти квадратная линия челюсти. Рекомендуются прически, смягчающие углы, с объемом сверху и мягкими волнами."

    # 4. Круглое лицо: "Короткое" лицо, но с сужающейся челюстью (в отличие от квадратного).
    # aspect_ratio ~ 1, но челюсть заметно уже скул.
    elif aspect_ratio < 1.15:
        shape_name = "Круглое лицо"
        description = "Длина и ширина вашего лица примерно одинаковы, с мягкими, округлыми линиями. Чтобы визуально удлинить лицо, выбирайте прически с объемом на макушке."

    # 5. Прямоугольное (Удлиненное) лицо: "Длинное" лицо с равными ширинами.
    # Похоже на квадратное, но вытянутое по вертикали.
    elif aspect_ratio > 1.25 and jaw_norm > 0.9 and forehead_norm > 0.9:
        shape_name = "Прямоугольное (удлиненное) лицо"
        description = "Ваше лицо заметно длиннее, чем шире, с примерно одинаковой шириной лба и челюсти. Объем по бокам и челка помогут сбалансировать пропорции."

    # 6. Овальное лицо: "Золотой стандарт". "Длинное" лицо, где скулы - самая широкая часть,
    # а лоб и челюсть плавно сужаются. Это самое "сбалансированное" лицо.
    # Мы проверяем его в конце, как наиболее вероятный вариант, если другие не подошли.
    elif aspect_ratio > 1.2 and forehead_norm < 1.0 and jaw_norm < 0.9:
        shape_name = "Овальное лицо"
        description = "Ваше лицо немного длиннее, чем его ширина, со сбалансированными пропорциями и плавной линией подбородка. Эта форма считается универсальной, и вам подходит большинство причесок."

    return {"shape_name": shape_name, "description": description}


def process_image_with_landmarks_and_symmetry(img, all_lmks, circle_size=3, color=(255, 0, 0), is_copy=True):
    """
    Plots landmarks, a central symmetry line, horizontal alignment lines,
    and deviation lines on the image.

    :param img: Source image (numpy array).
    :param all_lmks: All landmarks detected by the model.
    :param circle_size: Size of the landmark circles.
    :param color: Color of the landmark circles.
    :param is_copy: If True, plot on a copy of the image.
    :return: Bytes of the processed image in JPEG format.
    """
    processed_img = img.copy() if is_copy else img

    # --- ДИНАМИЧЕСКИЙ РАСЧЕТ ТОЛЩИНЫ ЛИНИЙ ---
    min_dim = min(processed_img.shape[0], processed_img.shape[1])

    # Увеличены коэффициенты для более заметных линий
    # base_thickness = max(1, min_dim // 300) # ИЗМЕНЕНИЕ: Сделаем 1px на каждые 300px
    # Landmark circle size: 1px for every 100-150px
    # Line thickness: 1px for every 200-300px

    # Можно использовать более агрессивные значения для заметности
    base_thickness_factor = 250  # 1px на каждые 250px минимального размера
    landmark_size_factor = 100  # 1px на каждые 100px минимального размера

    calculated_base_thickness = max(1, min_dim // base_thickness_factor)

    central_line_thickness = max(3, calculated_base_thickness * 2)  # Минимум 3px, масштабируется
    horizontal_line_thickness = max(2, calculated_base_thickness)  # Минимум 2px, масштабируется
    deviation_line_thickness = max(2, calculated_base_thickness)  # Минимум 2px, масштабируется
    landmark_circle_size = max(3, min_dim // landmark_size_factor)  # Минимум 3px, масштабируется

    # Рисуем ключевые точки (с динамическим размером)
    if all_lmks is not None and len(all_lmks) > 0:
        processed_img = set_circles_on_img(processed_img, all_lmks, circle_size=landmark_circle_size, color=color,
                                           is_copy=False)

        try:
            five_lmks = get_five_landmarks_from_net(all_lmks)
            if len(five_lmks) >= 5:
                le, re, nose, ml, mr = five_lmks[0], five_lmks[1], five_lmks[2], five_lmks[3], five_lmks[4]

                # --- 1. Центральная Вертикальная Линия (Желтая) ---
                center_x_axis = int((le[0] + re[0]) / 2)
                cv2.line(processed_img, (center_x_axis, 0), (center_x_axis, processed_img.shape[0]), (0, 255, 255),
                         central_line_thickness)

                # --- 2. Горизонтальные Линии для Сравнения Уровней (Оранжевые) ---
                avg_eye_y = int((le[1] + re[1]) / 2)
                cv2.line(processed_img, (int(le[0]), avg_eye_y), (int(re[0]), avg_eye_y), (0, 165, 255),
                         horizontal_line_thickness)

                avg_mouth_y = int((ml[1] + mr[1]) / 2)
                # ИЗМЕНЕНИЕ: avg_mouth[1] -> avg_mouth_y для консистентности
                cv2.line(processed_img, (int(ml[0]), avg_mouth_y), (int(mr[0]), avg_mouth_y), (0, 165, 255),
                         horizontal_line_thickness)

                # --- 3. Линии Отклонения от "Идеальной" Симметрии (Красные) ---
                deviation_color = (0, 0, 255)  # Красный цвет

                # Для левого глаза
                ideal_le_x = center_x_axis - (re[0] - center_x_axis)
                cv2.line(processed_img, (int(le[0]), int(le[1])), (int(ideal_le_x), int(le[1])), deviation_color,
                         deviation_line_thickness)
                cv2.line(processed_img, (int(le[0]), int(le[1])), (int(le[0]), int(re[1])), deviation_color,
                         deviation_line_thickness)

                # Для правого глаза
                ideal_re_x = center_x_axis + (center_x_axis - le[0])
                cv2.line(processed_img, (int(re[0]), int(re[1])), (int(ideal_re_x), int(re[1])), deviation_color,
                         deviation_line_thickness)
                cv2.line(processed_img, (int(re[0]), int(re[1])), (int(re[0]), int(le[1])), deviation_color,
                         deviation_line_thickness)

                # Для левого уголка рта
                ideal_ml_x = center_x_axis - (mr[0] - center_x_axis)
                cv2.line(processed_img, (int(ml[0]), int(ml[1])), (int(ideal_ml_x), int(ml[1])), deviation_color,
                         deviation_line_thickness)
                cv2.line(processed_img, (int(ml[0]), int(ml[1])), (int(ml[0]), int(mr[1])), deviation_color,
                         deviation_line_thickness)

                # Для правого уголка рта
                ideal_mr_x = center_x_axis + (center_x_axis - ml[0])
                cv2.line(processed_img, (int(mr[0]), int(mr[1])), (int(ideal_mr_x), int(mr[1])), deviation_color,
                         deviation_line_thickness)
                cv2.line(processed_img, (int(mr[0]), int(mr[1])), (int(mr[0]), int(ml[1])), deviation_color,
                         deviation_line_thickness)


        except NotImplementedError:
            print(
                f"Warning: Cannot draw symmetry lines for {len(all_lmks)} landmarks without `get_five_landmarks_from_net` support.")
        except IndexError:
            print("Warning: Not enough landmarks to draw symmetry lines (e.g., nose not detected).")
        except Exception as e:
            print(f"Error drawing symmetry lines: {e}")

    is_success, buffer = cv2.imencode(".jpg", processed_img)
    if not is_success:
        raise Exception("Could not encode image to JPEG.")

    return io.BytesIO(buffer)