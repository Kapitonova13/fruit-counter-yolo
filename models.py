import os
import cv2
import numpy as np
from datetime import datetime
from collections import Counter
from ultralytics import YOLO
import base64

# Загрузка модели YOLOv8
print("⏳ Загружаю модель YOLO...")
model = YOLO('C:/Users/anyak/Desktop/fruit_project/fruit_env/fruit_counter/best.pt')

print("✅ Модель загружена!")

# Классы фруктов
FRUIT_CLASSES = {
    0: 'apple',
    1: 'banana',
    2: 'orange',
}

def process_image(image_data, is_base64=False, app=None):
    """Обработка изображения"""
    try:
        if is_base64:
            # Декодируем base64
            img_bytes = base64.b64decode(image_data.split(',')[1])
            img_array = np.frombuffer(img_bytes, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        else:
            # Загружаем файл
            img = cv2.imdecode(np.frombuffer(image_data.read(), np.uint8), cv2.IMREAD_COLOR)

        if img is None:
            return {"error": "Не удалось загрузить изображение"}

        h, w = img.shape[:2]

        # Сегментация
        results = model(img, iou=0.45, agnostic_nms=True, max_det=100)

        # Подсчет фруктов
        fruit_counts = Counter()
        processed_img = img.copy()
        details = []

        for result in results:
            if result.masks is not None:
                for i, mask in enumerate(result.masks.data):
                    class_id = int(result.boxes.cls[i])
                    confidence = float(result.boxes.conf[i])

                    if class_id in FRUIT_CLASSES and confidence > 0.40:
                        fruit_name = FRUIT_CLASSES[class_id]
                        fruit_counts[fruit_name] += 1

                        # Обработка маски
                        mask_np = mask.cpu().numpy()
                        mask_resized = cv2.resize(mask_np, (w, h))

                        # Цвет для маски
                        color = np.random.randint(50, 255, 3).tolist()

                        # Накладываем маску
                        processed_img[mask_resized > 0.5] = (
                            processed_img[mask_resized > 0.5] * 0.6 +
                            np.array(color) * 0.4
                        ).astype(np.uint8)

                        # Bounding box
                        x1, y1, x2, y2 = result.boxes.xyxy[i].cpu().numpy().astype(int)
                        cv2.rectangle(processed_img, (x1, y1), (x2, y2), color, 2)

                        # Подпись
                        label = f"{fruit_name} {confidence:.2f}"
                        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                        cv2.rectangle(processed_img, (x1, y1-th-10), (x1+tw, y1), color, -1)
                        cv2.putText(processed_img, label, (x1, y1-5),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)

                        details.append({
                            'fruit': fruit_name,
                            'confidence': confidence,
                            'bbox': [int(x1), int(y1), int(x2), int(y2)]
                        })

        # Сохраняем результат
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_filename = f"result_{timestamp}.jpg"
        result_path = os.path.join(app.config['RESULTS_FOLDER'], result_filename)
        cv2.imwrite(result_path, processed_img)

        # Подготавливаем результаты
        results_data = {
            'success': True,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'fruit_counts': dict(fruit_counts),
            'total_fruits': sum(fruit_counts.values()),
            'result_image': f'/results/{result_filename}',
            'details': details
        }

        return results_data

    except Exception as e:
        return {"error": str(e)}