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
    Определяет одну из 6 заданных форм лица на основе 98 ключевых точек WFLW.
    Логика откалибрована для строгого соответствия предоставленным категориям.
    Версия 4.0 (под 6 форм).

    :param all_lmks: Полный набор из 98 ключевых точек лица от модели WFLW.
    :return: Словарь с 'shape_name' и 'description' одной из 6 форм.
    """
    if all_lmks is None or len(all_lmks) != 98:
        return {
            "shape_name": "Неопределенная форма",
            "description": "Недостаточно данных для определения формы. Убедитесь, что модель обнаружила 98 ключевых точек."
        }

    # --- 1. ТОЧНЫЕ ИЗМЕРЕНИЯ ---
    # Используем полную высоту лица от верхушки лба (59) до подбородка (8)
    face_height = abs(all_lmks[8][1] - all_lmks[59][1])
    # Ширина скул (максимальная ширина лица)
    cheekbone_width = abs(all_lmks[16][0] - all_lmks[0][0])
    # Ширина лба
    forehead_width = abs(all_lmks[42][0] - all_lmks[33][0])
    # Ширина челюсти
    jaw_width = abs(all_lmks[12][0] - all_lmks[4][0])

    if cheekbone_width == 0 or face_height == 0:
        return {
            "shape_name": "Неопределенная форма",
            "description": "Не удалось вычислить базовые пропорции лица."
        }

    # --- 2. КЛЮЧЕВЫЕ СООТНОШЕНИЯ ДЛЯ КЛАССИФИКАЦИИ ---
    # Соотношение высоты к ширине
    aspect_ratio = face_height / cheekbone_width
    # Соотношение челюсти к скулам (ключевое для разделения Квадрата и Круга)
    jaw_to_cheek_ratio = jaw_width / cheekbone_width
    # Соотношение лба к скулам
    forehead_to_cheek_ratio = forehead_width / cheekbone_width

    # --- ДЛЯ ОТЛАДКИ ---
    # print(f"H:{face_height:.1f}, CW:{cheekbone_width:.1f}, FW:{forehead_width:.1f}, JW:{jaw_width:.1f}")
    # print(f"Aspect:{aspect_ratio:.2f}, Jaw/Cheek:{jaw_to_cheek_ratio:.2f}, Forehead/Cheek:{forehead_to_cheek_ratio:.2f}")
    # -------------------

    shape_name = "Неопределенная форма" # Исходное значение
    description = "Не удалось классифицировать лицо по заданным формам."

    # --- 3. СТРОГАЯ ИЕРАРХИЧЕСКАЯ ЛОГИКА ДЛЯ 6 ФОРМ ---

    # ПЕРВЫЙ УРОВЕНЬ: Уникальные формы, определяемые по самой широкой части

    # 1. Грушевидное лицо: Челюсть заметно шире скул и лба.
    if jaw_width > cheekbone_width and jaw_width > forehead_width:
        shape_name = "Грушевидное лицо"
        description = "Узкий лоб и широкая нижняя часть лица (подбородок). Лицо похоже на грушу. Можно выбрать прически с объемом в верхней части для балансировки."

    # 2. Треугольное лицо (сердце): Лоб заметно шире скул, которые, в свою очередь, шире челюсти.
    elif forehead_width > cheekbone_width and cheekbone_width > jaw_width:
        shape_name = "Треугольное лицо (сердце)"
        description = "Широкий лоб и скулы, узкий подбородок. Лицо напоминает форму сердца. Хороши прически с объемом по бокам для уравновешивания ширины лба."

    # ВТОРОЙ УРОВЕНЬ: Разделение оставшихся форм (Овал, Круг, Квадрат, Прямоугольник) по соотношению сторон
    else:
        # Категория A: "Короткие" лица (ширина и длина сопоставимы)
        if aspect_ratio < 1.3:
            # 3. Квадратное лицо: Широкая, "тяжелая" челюсть, почти равная по ширине скулам.
            if jaw_to_cheek_ratio > 0.92:
                shape_name = "Квадратное лицо"
                description = "Широкий лоб, выраженная линия челюсти и подбородка. Лицо кажется массивным и угловатым. Хорошо подходят прически с объемом сверху для смягчения углов."
            # 4. Круглое лицо: Мягкие линии, челюсть заметно уже скул.
            else:
                shape_name = "Круглое лицо"
                description = "Ширина и длина примерно одинаковые. Скулы и линия подбородка округлые, лицо кажется мягким и полным. Желательно выбирать прически с объемом сверху и удлиненными линиями."

        # Категория B: "Длинные" лица
        else:
            # 5. Прямоугольное лицо: Вытянутое, но при этом "угловатое", все ширины почти равны.
            if jaw_to_cheek_ratio > 0.9 and forehead_to_cheek_ratio > 0.9:
                shape_name = "Прямоугольное (или удлиненное) лицо"
                description = "Лицо длиннее, чем ширина, с высокой линией лба и вытянутой формой. Можно использовать прически с объемом по бокам для балансировки пропорций."
            # 6. Овальное лицо: Классическая "длинная" форма с плавным сужением от скул к челюсти и лбу.
            else:
                shape_name = "Овальное лицо"
                description = "Лицо чуть длиннее, чем ширина, с плавными линиями. Лоб немного шире подбородка, скулы заметны, линия подбородка мягкая. Универсальная форма, подходит большинство причесок и стилей."

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