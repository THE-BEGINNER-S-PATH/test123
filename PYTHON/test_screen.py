import cv2
import numpy as np
import mediapipe as mp

# Инициализация MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Инициализация вебкамеры
cap = cv2.VideoCapture(0)

# Переменные для рисования
canvas = None
prev_x, prev_y = None, None
color = (0, 0, 255)  # Красный по умолчанию
brush_size = 5
eraser_size = 20
mode = 'draw'  # Режим: 'draw' или 'erase'

# Список доступных цветов
colors = [
    (0, 0, 255),    # Красный
    (0, 255, 0),    # Зеленый
    (255, 0, 0),    # Синий
    (0, 255, 255),  # Желтый
    (255, 0, 255),  # Пурпурный
    (255, 255, 0),  # Голубой
    (0, 0, 0)       # Ластик (черный, но будет работать как ластик)
]

color_names = ['Красный', 'Зеленый', 'Синий', 'Желтый', 'Пурпурный', 'Голубой', 'Ластик']
current_color_index = 0

# Размеры кистей
brush_sizes = [3, 5, 8, 12, 15]
current_brush_index = 1

def draw_ui(img):
    """Рисует интерфейс выбора цвета и размера кисти"""
    # Панель цветов
    for i, col in enumerate(colors):
        cv2.rectangle(img, (10 + i*40, 10), (40 + i*40, 40), col, -1)
        if i == current_color_index:
            cv2.rectangle(img, (10 + i*40, 10), (40 + i*40, 40), (255, 255, 255), 2)
    
    # Панель размеров кисти
    for i, size in enumerate(brush_sizes):
        cv2.circle(img, (30 + i*40, 70), size, (255, 255, 255), -1)
        if i == current_brush_index:
            cv2.circle(img, (30 + i*40, 70), size+2, (0, 255, 0), 2)
    
    # Информация о текущем режиме
    mode_text = "Режим: Рисование" if mode == 'draw' else "Режим: Ластик"
    cv2.putText(img, mode_text, (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(img, "Два пальца - завершить/очистить", (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

while True:
    ret, frame = cap.read()
    if not ret:
        continue
    
    # Отражаем изображение для естественного отображения
    frame = cv2.flip(frame, 1)
    
    # Инициализируем холст, если он еще не создан
    if canvas is None:
        canvas = np.zeros_like(frame)
    
    # Конвертируем изображение в RGB для MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)
    
    # Рисуем интерфейс
    draw_ui(frame)
    
    # Если руки обнаружены
    if result.multi_hand_landmarks:
        hand_landmarks = result.multi_hand_landmarks[0]
        
        # Рисуем landmarks руки
        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        
        # Получаем координаты кончиков пальцев
        landmarks = []
        for lm in hand_landmarks.landmark:
            h, w, c = frame.shape
            landmarks.append((int(lm.x * w), int(lm.y * h)))
        
        # Кончик указательного пальца (для рисования)
        index_tip = landmarks[8]
        
        # Кончик большого пальца (для выбора цвета/размера)
        thumb_tip = landmarks[4]
        
        # Кончик среднего пальца (для определения жеста "два пальца")
        middle_tip = landmarks[12]
        
        # Проверяем, находится ли большой палец над панелью выбора цвета
        if 10 <= thumb_tip[1] <= 40:
            for i in range(len(colors)):
                if 10 + i*40 <= thumb_tip[0] <= 40 + i*40:
                    current_color_index = i
                    if i == len(colors) - 1:  # Последний элемент - ластик
                        mode = 'erase'
                    else:
                        mode = 'draw'
                        color = colors[i]
                    break
        
        # Проверяем, находится ли большой палец над панелью выбора размера
        if 50 <= thumb_tip[1] <= 90:
            for i in range(len(brush_sizes)):
                if 10 + i*40 <= thumb_tip[0] <= 50 + i*40:
                    current_brush_index = i
                    brush_size = brush_sizes[i]
                    break
        
        # Определяем, зажаты ли два пальца (указательный и средний)
        # Проверяем, находятся ли кончики пальцев близко друг к другу
        fingers_distance = np.sqrt((index_tip[0] - middle_tip[0])**2 + (index_tip[1] - middle_tip[1])**2)
        
        if fingers_distance < 30:  # Если пальцы близко - завершаем рисование
            prev_x, prev_y = None, None
            canvas = np.zeros_like(frame)  # Очищаем холст
        else:
            # Рисуем на холсте
            if prev_x is not None and prev_y is not None:
                if mode == 'draw':
                    cv2.line(canvas, (prev_x, prev_y), index_tip, color, brush_size)
                else:  # Режим ластика
                    cv2.line(canvas, (prev_x, prev_y), index_tip, (0, 0, 0), eraser_size)
            
            prev_x, prev_y = index_tip
    
    # Накладываем холст на frame
    frame = cv2.add(frame, canvas)
    
    # Показываем изображение
    cv2.imshow('Hand Tracking Drawing', frame)
    
    # Обработка клавиш
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('c'):
        canvas = np.zeros_like(frame)  # Очистить холст
    elif key == ord('e'):
        mode = 'erase'  # Переключить в режим ластика
    elif key == ord('d'):
        mode = 'draw'  # Переключить в режим рисования

# Освобождаем ресурсы
cap.release()
cv2.destroyAllWindows()