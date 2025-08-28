import cv2
import numpy as np
import io
from .utils_landmarks import set_circles_on_img, \
    get_five_landmarks_from_net  # Импортируем нужные функции из оригинального файла


def calculate_symmetry_index(all_lmks):
    """
    Рассчитывает простой индекс симметрии лица на основе 5 ключевых точек.

    :param all_lmks: Полный набор ключевых точек, возвращаемых моделью (например, 98 точек).
    :return: Процент симметрии (от 0 до 100).
    """
    if all_lmks is None or len(all_lmks) == 0:
        return 0.0  # Невозможно рассчитать без точек

    # Извлекаем 5 основных точек для симметрии
    try:
        five_lmks = get_five_landmarks_from_net(all_lmks)
    except NotImplementedError:
        # Если get_five_landmarks_from_net не поддерживает текущее количество точек,
        # можно попробовать взять первые 5 или реализовать специфичную логику.
        # Для демонстрации, если не удается, вернем 0.
        print(
            f"Warning: get_five_landmarks_from_net does not support {len(all_lmks)} landmarks for symmetry calculation.")
        return 0.0

    if len(five_lmks) < 5:
        return 0.0  # Недостаточно точек для расчета

    # five_lmks: [левый глаз, правый глаз, нос, левый уголок рта, правый уголок рта]

    # 1. Определение центральной вертикальной оси
    # Возьмем среднее по X для всех 5 точек или X носа
    center_x = five_lmks[2][0]  # X-координата носа как центральная ось

    # 2. Отклонения X-координат от центральной оси
    # Отклонение по горизонтали: (левый глаз - центр) vs (центр - правый глаз)
    dev_le_x = abs(five_lmks[0][0] - center_x)
    dev_re_x = abs(five_lmks[1][0] - center_x)
    dev_lm_x = abs(five_lmks[3][0] - center_x)
    dev_rm_x = abs(five_lmks[4][0] - center_x)

    # Разница в отклонениях
    diff_eyes_x = abs(dev_le_x - dev_re_x)
    diff_mouth_x = abs(dev_lm_x - dev_rm_x)

    # 3. Отклонения Y-координат (вертикальное выравнивание симметричных точек)
    # Разница Y-координат между левым и правым глазом
    diff_eyes_y = abs(five_lmks[0][1] - five_lmks[1][1])
    # Разница Y-координат между левым и правым уголком рта
    diff_mouth_y = abs(five_lmks[3][1] - five_lmks[4][1])

    # 4. Нормализация отклонений
    # Используем расстояние между глазами для нормализации, так как это хороший масштаб для лица
    eye_distance = np.linalg.norm(five_lmks[0] - five_lmks[1])
    if eye_distance == 0:
        return 0.0  # Избегаем деления на ноль

    normalized_x_deviation = (diff_eyes_x + diff_mouth_x) / (2 * eye_distance)
    normalized_y_deviation = (diff_eyes_y + diff_mouth_y) / (2 * eye_distance)  # Разница Y между симметричными точками

    total_deviation_score = normalized_x_deviation + normalized_y_deviation

    # 5. Преобразование в процент симметрии
    # Чем меньше total_deviation_score, тем выше симметрия.
    # Простая линейная шкала: 0 отклонение = 100% симметрии. Макс. отклонение = 0% симметрии.
    # Нужно откалибровать max_permissible_deviation для вашей модели
    max_permissible_deviation = 0.5  # Это примерное значение, возможно, потребуется калибровка

    symmetry_percentage = max(0, 100 - (total_deviation_score / max_permissible_deviation) * 100)

    return round(symmetry_percentage, 2)


def process_image_with_landmarks_and_symmetry(img, all_lmks, circle_size=3, color=(255, 0, 0), is_copy=True):
    """
    Plots landmarks and a central symmetry line on the image, then returns
    the modified image as a JPEG byte stream.

    :param img: Source image (numpy array).
    :param all_lmks: All landmarks detected by the model.
    :param circle_size: Size of the landmark circles.
    :param color: Color of the landmark circles.
    :param is_copy: If True, plot on a copy of the image.
    :return: Bytes of the processed image in JPEG format.
    """
    processed_img = set_circles_on_img(img, all_lmks, circle_size=circle_size, color=color, is_copy=is_copy)

    if all_lmks is not None and len(all_lmks) > 0:
        try:
            five_lmks = get_five_landmarks_from_net(all_lmks)
            if len(five_lmks) >= 3:  # Убедимся, что есть хотя бы нос
                nose_x = int(five_lmks[2][0])  # X-координата носа
                # Рисуем вертикальную центральную линию симметрии
                cv2.line(processed_img, (nose_x, 0), (nose_x, processed_img.shape[0]), (0, 255, 255), 2)  # Желтая линия
        except NotImplementedError:
            print(
                f"Warning: Cannot draw symmetry line for {len(all_lmks)} landmarks without `get_five_landmarks_from_net` support.")
        except IndexError:
            print("Warning: Not enough landmarks to draw symmetry line (e.g., nose not detected).")

    # Encode the image to JPEG format in memory
    is_success, buffer = cv2.imencode(".jpg", processed_img)
    if not is_success:
        raise Exception("Could not encode image to JPEG.")

    return io.BytesIO(buffer)