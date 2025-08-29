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
    Определяет форму лица на основе 5 ключевых точек.

    :param all_lmks: Полный набор ключевых точек лица.
    :return: Словарь с 'shape_name' и 'description'.
             Если лицо не обнаружено или точек недостаточно, возвращает None.
    """
    if all_lmks is None or len(all_lmks) == 0:
        return None

    try:
        five_lmks = get_five_landmarks_from_net(all_lmks)
    except NotImplementedError:
        print(
            f"Warning: get_five_landmarks_from_net does not support {len(all_lmks)} landmarks for face shape calculation.")
        return None

    if len(five_lmks) < 5:
        return None

    le, re, nose, ml, mr = five_lmks[0], five_lmks[1], five_lmks[2], five_lmks[3], five_lmks[4]

    # Расчет ключевых размеров лица
    face_width_eyes = abs(re[0] - le[0])  # Ширина между глазами
    face_width_mouth = abs(mr[0] - ml[0])  # Ширина рта
    face_width_forehead = face_width_eyes * 1.5  # Предполагаемая ширина лба (сложно точно определить без отдельных точек лба)

    # Для простоты, берем ширину лица как расстояние между внешними точками глаз, умноженное на коэффициент
    # или используем x-координаты крайних боковых точек, если они доступны в all_lmks
    # Если all_lmks имеет 98 точек, можно взять 36 (левый висок) и 45 (правый висок) для ширины лица
    # или 0 (самая левая) и 16 (самая правая) если lmks - это 68-точек

    # Максимальная ширина лица (предположим, что она примерно в районе скул/висков)
    # Если у вас 98 точек:
    if len(all_lmks) == 98:
        # Приближенно используем точки 0 (левая граница лица) и 32 (правая граница лица) для ширины
        # или 33 (левая скула) и 39 (правая скула) для скул
        # Или берем минимальную и максимальную X-координаты из всех точек
        all_x_coords = all_lmks[:, 0]
        min_x = np.min(all_x_coords)
        max_x = np.max(all_x_coords)
        max_face_width = max_x - min_x

        # Высота лица от верхней части лба до нижней части подбородка
        min_y = np.min(all_lmks[:, 1])  # Верхняя точка (лоб)
        max_y = np.max(all_lmks[:, 1])  # Нижняя точка (подбородок)
        face_height = max_y - min_y

        # Ширина лба (приближенно)
        # Если есть брови, можно использовать их
        forehead_left = all_lmks[17] if len(all_lmks) >= 18 else le
        forehead_right = all_lmks[26] if len(all_lmks) >= 27 else re
        width_forehead = abs(forehead_right[0] - forehead_left[0])

        # Ширина челюсти (приближенно)
        # Если есть точки челюсти, можно использовать их (например, 48 и 54 для 68 точек)
        jaw_left = all_lmks[48] if len(all_lmks) >= 49 else ml
        jaw_right = all_lmks[54] if len(all_lmks) >= 55 else mr
        width_jaw = abs(jaw_right[0] - jaw_left[0])
        # Чтобы получить реальную ширину челюсти, можно взять точки 4 и 12 из 17-точечной линии челюсти

    else:  # Если у нас только 5 точек, то оценки будут очень приблизительными
        max_face_width = abs(re[0] - le[0]) * 2.0  # Оценка общей ширины лица
        face_height = abs(nose[1] - (le[1] + re[1]) / 2) * 2.5  # Оценка высоты лица
        width_forehead = face_width_eyes * 1.5  # Очень приблизительно
        width_jaw = face_width_mouth * 1.5  # Очень приблизительно

    # Соотношение сторон лица (Height to Width)
    aspect_ratio = face_height / max_face_width if max_face_width > 0 else 0

    # Пропорции для определения формы
    is_oval = False
    is_round = False
    is_square = False
    is_rectangle = False
    is_heart = False
    is_pear = False

    # Логика определения формы лица
    # Эти пороговые значения нужно будет настроить и откалибровать!

    # Овальное: Высота немного больше ширины, мягкие линии
    if 1.25 < aspect_ratio < 1.6 and width_forehead < max_face_width and width_jaw < max_face_width * 0.9:
        is_oval = True

    # Круглое: Ширина и длина примерно равны, мягкие линии
    elif 0.95 < aspect_ratio < 1.05 and max_face_width * 0.9 < width_forehead < max_face_width * 1.1 and max_face_width * 0.9 < width_jaw < max_face_width * 1.1:
        is_round = True

    # Квадратное: Ширина и длина примерно равны, выраженная челюсть и лоб
    elif 0.9 < aspect_ratio < 1.1 and width_forehead > max_face_width * 0.9 and width_jaw > max_face_width * 0.9 and abs(
            width_forehead - width_jaw) < max_face_width * 0.2:
        is_square = True

    # Прямоугольное (удлиненное): Длинное лицо
    elif aspect_ratio >= 1.6 and abs(width_forehead - width_jaw) < max_face_width * 0.2:
        is_rectangle = True

    # Треугольное (сердце): Широкий лоб, узкий подбородок
    elif width_forehead > width_jaw * 1.2 and aspect_ratio > 1.2:
        is_heart = True

    # Грушевидное: Узкий лоб, широкий подбородок
    elif width_jaw > width_forehead * 1.2 and aspect_ratio > 1.0:
        is_pear = True

    # Если ни одна форма не подошла идеально, можно выбрать "Близко к овальной" или "Неопределенная"

    # Приоритет форм (чтобы избежать дублирования, если условия пересекаются)
    if is_oval:
        shape_name = "Овальное лицо"
        description = "Ваше лицо чуть длиннее, чем ширина, с плавными линиями. Лоб немного шире подбородка, скулы заметны, линия подбородка мягкая. Это универсальная форма, к которой подходит большинство причесок и стилей."
    elif is_round:
        shape_name = "Круглое лицо"
        description = "У вас примерно одинаковые ширина и длина лица. Скулы и линия подбородка округлые, лицо кажется мягким и полным. Рекомендуется выбирать прически с объемом сверху и удлиненными линиями для визуального удлинения лица."
    elif is_square:
        shape_name = "Квадратное лицо"
        description = "У вас широкий лоб, выраженная линия челюсти и подбородка. Лицо кажется массивным и угловатым. Хорошо подходят прически с объемом сверху для смягчения углов и придания лицу более мягкого вида."
    elif is_rectangle:
        shape_name = "Прямоугольное (удлиненное) лицо"
        description = "Ваше лицо длиннее, чем ширина, с высокой линией лба и вытянутой формой. Можно использовать прически с объемом по бокам и челки для балансировки пропорций и визуального сокращения длины лица."
    elif is_heart:
        shape_name = "Треугольное лицо (сердце)"
        description = "У вас широкий лоб и скулы, сужающиеся к узкому подбородку, напоминающие форму сердца. Хороши прически с объемом по бокам для уравновешивания ширины лба и придания гармонии нижней части лица."
    elif is_pear:
        shape_name = "Грушевидное лицо"
        description = "У вас узкий лоб и широкая нижняя часть лица (подбородок). Можно выбрать прически с объемом в верхней части головы для балансировки пропорций и визуального расширения лба."
    else:
        shape_name = "Неопределенная форма лица"
        description = "Не удалось точно определить форму вашего лица на основе текущих данных. Форма лица может быть смешанной или требовать более детального анализа."

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