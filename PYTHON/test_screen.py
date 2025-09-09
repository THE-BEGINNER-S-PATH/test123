<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Рисование с отслеживанием рук</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tensorflow/4.20.0/tf.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/handpose/0.0.7/handpose.min.js"></script>
    <style>
        body {
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
            color: white;
            padding: 20px;
            text-align: center;
        }
        
        .header h1 {
            margin: 0;
            font-size: 2em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .controls {
            padding: 20px;
            background: rgba(255, 255, 255, 0.8);
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            align-items: center;
            justify-content: center;
        }
        
        .control-group {
            display: flex;
            align-items: center;
            gap: 10px;
            background: white;
            padding: 10px 15px;
            border-radius: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .control-group label {
            font-weight: bold;
            color: #333;
        }
        
        .color-palette {
            display: flex;
            gap: 5px;
        }
        
        .color-btn {
            width: 40px;
            height: 40px;
            border: 3px solid transparent;
            border-radius: 50%;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .color-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        
        .color-btn.active {
            border-color: #333;
            transform: scale(1.2);
        }
        
        #brushSize {
            width: 150px;
            height: 8px;
            border-radius: 5px;
            background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
            outline: none;
            cursor: pointer;
        }
        
        .btn {
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        }
        
        .canvas-container {
            position: relative;
            display: flex;
            justify-content: center;
            background: #f8f9fa;
            padding: 20px;
        }
        
        #videoElement {
            position: absolute;
            top: 20px;
            right: 20px;
            width: 200px;
            height: 150px;
            border: 3px solid #4ECDC4;
            border-radius: 10px;
            transform: scaleX(-1);
            z-index: 10;
        }
        
        #drawingCanvas {
            border: 3px solid #FF6B6B;
            border-radius: 10px;
            background: white;
            cursor: crosshair;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .status {
            position: absolute;
            top: 180px;
            right: 20px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 10px 15px;
            border-radius: 20px;
            font-size: 14px;
            z-index: 10;
        }
        
        .instructions {
            background: rgba(255, 235, 59, 0.2);
            border-left: 4px solid #FFD700;
            padding: 15px;
            margin: 20px;
            border-radius: 5px;
        }
        
        .instructions h3 {
            margin-top: 0;
            color: #B8860B;
        }
        
        .instructions ul {
            margin: 0;
            padding-left: 20px;
        }
        
        .instructions li {
            margin: 5px 0;
        }

        .gesture-indicator {
            position: absolute;
            top: 220px;
            right: 20px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 10px 15px;
            border-radius: 20px;
            font-size: 12px;
            z-index: 10;
        }

        .drawing-cursor {
            position: absolute;
            width: 20px;
            height: 20px;
            background: rgba(255, 107, 107, 0.7);
            border: 2px solid #FF6B6B;
            border-radius: 50%;
            pointer-events: none;
            z-index: 15;
            transform: translate(-50%, -50%);
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 Рисование жестами рук</h1>
        </div>
        
        <div class="instructions">
            <h3>📖 Инструкция:</h3>
            <ul>
                <li><strong>Рисование:</strong> Поднимите указательный палец (остальные согнуты)</li>
                <li><strong>Остановка:</strong> Поднимите указательный и средний пальцы (знак "мир")</li>
                <li><strong>Настройки:</strong> Выберите цвет и размер кисти внизу</li>
                <li><strong>Очистка:</strong> Нажмите кнопку "Очистить холст"</li>
            </ul>
        </div>
        
        <div class="controls">
            <div class="control-group">
                <label>Цвет:</label>
                <div class="color-palette">
                    <div class="color-btn active" style="background-color: #FF6B6B;" data-color="#FF6B6B"></div>
                    <div class="color-btn" style="background-color: #4ECDC4;" data-color="#4ECDC4"></div>
                    <div class="color-btn" style="background-color: #45B7D1;" data-color="#45B7D1"></div>
                    <div class="color-btn" style="background-color: #96CEB4;" data-color="#96CEB4"></div>
                    <div class="color-btn" style="background-color: #FFEAA7;" data-color="#FFEAA7"></div>
                    <div class="color-btn" style="background-color: #DDA0DD;" data-color="#DDA0DD"></div>
                    <div class="color-btn" style="background-color: #98D8C8;" data-color="#98D8C8"></div>
                    <div class="color-btn" style="background-color: #F7DC6F;" data-color="#F7DC6F"></div>
                    <div class="color-btn" style="background-color: #BB8FCE;" data-color="#BB8FCE"></div>
                    <div class="color-btn" style="background-color: #333333;" data-color="#333333"></div>
                </div>
            </div>
            
            <div class="control-group">
                <label>Размер кисти:</label>
                <input type="range" id="brushSize" min="2" max="50" value="5">
                <span id="sizeValue">5px</span>
            </div>
            
            <button class="btn" onclick="clearCanvas()">Очистить холст</button>
            <button class="btn" onclick="toggleCamera()">Вкл/Выкл камеру</button>
            <button class="btn" onclick="saveDrawing()">Сохранить</button>
        </div>
        
        <div class="canvas-container">
            <video id="videoElement" autoplay muted playsinline></video>
            <canvas id="drawingCanvas" width="800" height="600"></canvas>
            <div class="status" id="status">Загрузка...</div>
            <div class="gesture-indicator" id="gesture">Жест: Нет</div>
            <div class="drawing-cursor" id="cursor"></div>
        </div>
    </div>

    <script>
        // Глобальные переменные
        let canvas, ctx;
        let currentColor = '#FF6B6B';
        let brushSize = 5;
        let isDrawing = false;
        let lastX = 0;
        let lastY = 0;
        let handposeModel = null;
        let video = null;
        let cameraActive = false;
        let animationId = null;
        
        // Инициализация
        window.addEventListener('load', init);
        
        async function init() {
            canvas = document.getElementById('drawingCanvas');
            ctx = canvas.getContext('2d');
            video = document.getElementById('videoElement');
            
            // Настройка контекста
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';
            
            setupControls();
            await loadModel();
            setupCamera();
        }
        
        async function loadModel() {
            const status = document.getElementById('status');
            try {
                status.textContent = 'Загрузка модели распознавания рук...';
                handposeModel = await handpose.load();
                status.textContent = 'Модель загружена! Запуск камеры...';
            } catch (error) {
                console.error('Ошибка загрузки модели:', error);
                status.textContent = 'Ошибка загрузки. Используйте мышь.';
                setupMouseDrawing();
            }
        }
        
        function setupControls() {
            // Цветовая палитра
            document.querySelectorAll('.color-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    document.querySelector('.color-btn.active').classList.remove('active');
                    btn.classList.add('active');
                    currentColor = btn.dataset.color;
                    updateCursorColor();
                });
            });
            
            // Размер кисти
            const brushSizeSlider = document.getElementById('brushSize');
            const sizeValue = document.getElementById('sizeValue');
            
            brushSizeSlider.addEventListener('input', (e) => {
                brushSize = parseInt(e.target.value);
                sizeValue.textContent = brushSize + 'px';
                updateCursorSize();
            });
        }
        
        function updateCursorColor() {
            const cursor = document.getElementById('cursor');
            cursor.style.background = currentColor + '70';
            cursor.style.borderColor = currentColor;
        }
        
        function updateCursorSize() {
            const cursor = document.getElementById('cursor');
            const size = Math.max(brushSize, 10);
            cursor.style.width = size + 'px';
            cursor.style.height = size + 'px';
        }
        
        async function setupCamera() {
            const status = document.getElementById('status');
            
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { 
                        width: 640, 
                        height: 480,
                        facingMode: 'user'
                    } 
                });
                
                video.srcObject = stream;
                cameraActive = true;
                
                video.addEventListener('loadeddata', () => {
                    status.textContent = 'Камера готова! Покажите руку.';
                    detectHands();
                });
                
            } catch (error) {
                console.error('Ошибка доступа к камере:', error);
                status.textContent = 'Нет доступа к камере. Используйте мышь.';
                setupMouseDrawing();
            }
        }
        
        async function detectHands() {
            if (!handposeModel || !cameraActive || video.videoWidth === 0) {
                animationId = requestAnimationFrame(detectHands);
                return;
            }
            
            try {
                const predictions = await handposeModel.estimateHands(video);
                
                if (predictions.length > 0) {
                    const hand = predictions[0];
                    const landmarks = hand.landmarks;
                    
                    // Получаем координаты ключевых точек
                    const indexTip = landmarks[8];      // Кончик указательного пальца
                    const indexPip = landmarks[6];      // Средний сустав указательного
                    const middleTip = landmarks[12];    // Кончик среднего пальца
                    const middlePip = landmarks[10];    // Средний сустав среднего
                    const ringTip = landmarks[16];      // Кончик безымянного
                    const pinkyTip = landmarks[20];     // Кончик мизинца
                    const thumbTip = landmarks[4];      // Кончик большого пальца
                    
                    // Определяем жест
                    const gesture = recognizeGesture(landmarks);
                    updateGestureDisplay(gesture);
                    
                    // Преобразуем координаты видео в координаты канваса
                    const canvasX = ((video.videoWidth - indexTip[0]) / video.videoWidth) * canvas.width;
                    const canvasY = (indexTip[1] / video.videoHeight) * canvas.height;
                    
                    updateCursor(canvasX, canvasY);
                    
                    if (gesture === 'drawing') {
                        if (!isDrawing) {
                            startDrawingAt(canvasX, canvasY);
                        } else {
                            drawTo(canvasX, canvasY);
                        }
                    } else {
                        stopDrawing();
                    }
                } else {
                    hideCursor();
                    updateGestureDisplay('none');
                    stopDrawing();
                }
                
            } catch (error) {
                console.error('Ошибка распознавания:', error);
            }
            
            animationId = requestAnimationFrame(detectHands);
        }
        
        function recognizeGesture(landmarks) {
            // Кончики пальцев
            const indexTip = landmarks[8];
            const middleTip = landmarks[12];
            const ringTip = landmarks[16];
            const pinkyTip = landmarks[20];
            const thumbTip = landmarks[4];
            
            // Суставы пальцев
            const indexPip = landmarks[6];
            const middlePip = landmarks[10];
            const ringPip = landmarks[14];
            const pinkyPip = landmarks[18];
            
            // Проверяем, какие пальцы подняты
            const indexUp = indexTip[1] < indexPip[1];
            const middleUp = middleTip[1] < middlePip[1];
            const ringUp = ringTip[1] < ringPip[1];
            const pinkyUp = pinkyTip[1] < pinkyPip[1];
            
            // Жест для рисования: только указательный палец поднят
            if (indexUp && !middleUp && !ringUp && !pinkyUp) {
                return 'drawing';
            }
            
            // Жест для остановки: указательный и средний пальцы подняты (знак "мир")
            if (indexUp && middleUp && !ringUp && !pinkyUp) {
                return 'stop';
            }
            
            return 'none';
        }
        
        function updateGestureDisplay(gesture) {
            const gestureElement = document.getElementById('gesture');
            const gestureNames = {
                'drawing': '✏️ Рисование',
                'stop': '✌️ Остановка',
                'none': '❌ Нет жеста'
            };
            
            gestureElement.textContent = 'Жест: ' + (gestureNames[gesture] || 'Неизвестный');
        }
        
        function updateCursor(x, y) {
            const cursor = document.getElementById('cursor');
            cursor.style.display = 'block';
            cursor.style.left = x + 'px';
            cursor.style.top = y + 'px';
        }
        
        function hideCursor() {
            const cursor = document.getElementById('cursor');
            cursor.style.display = 'none';
        }
        
        function startDrawingAt(x, y) {
            isDrawing = true;
            lastX = x;
            lastY = y;
        }
        
        function drawTo(x, y) {
            if (!isDrawing) return;
            
            ctx.globalCompositeOperation = 'source-over';
            ctx.strokeStyle = currentColor;
            ctx.lineWidth = brushSize;
            
            ctx.beginPath();
            ctx.moveTo(lastX, lastY);
            ctx.lineTo(x, y);
            ctx.stroke();
            
            lastX = x;
            lastY = y;
        }
        
        function stopDrawing() {
            isDrawing = false;
        }
        
        // Альтернативное рисование мышью
        function setupMouseDrawing() {
            canvas.addEventListener('mousedown', startDrawingMouse);
            canvas.addEventListener('mousemove', drawMouse);
            canvas.addEventListener('mouseup', stopDrawing);
            canvas.addEventListener('mouseout', stopDrawing);
            
            canvas.addEventListener('touchstart', handleTouch);
            canvas.addEventListener('touchmove', handleTouch);
            canvas.addEventListener('touchend', stopDrawing);
        }
        
        function startDrawingMouse(e) {
            const [x, y] = getMousePos(e);
            startDrawingAt(x, y);
        }
        
        function drawMouse(e) {
            if (!isDrawing) return;
            const [x, y] = getMousePos(e);
            drawTo(x, y);
        }
        
        function getMousePos(e) {
            const rect = canvas.getBoundingClientRect();
            return [
                (e.clientX - rect.left) * (canvas.width / rect.width),
                (e.clientY - rect.top) * (canvas.height / rect.height)
            ];
        }
        
        function handleTouch(e) {
            e.preventDefault();
            const touch = e.touches[0];
            const mouseEvent = new MouseEvent(e.type === 'touchstart' ? 'mousedown' : 
                                           e.type === 'touchmove' ? 'mousemove' : 'mouseup', {
                clientX: touch.clientX,
                clientY: touch.clientY
            });
            canvas.dispatchEvent(mouseEvent);
        }
        
        function clearCanvas() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
        
        function toggleCamera() {
            const status = document.getElementById('status');
            
            if (cameraActive && video.srcObject) {
                // Выключаем камеру
                video.srcObject.getTracks().forEach(track => track.stop());
                video.style.display = 'none';
                cameraActive = false;
                status.textContent = 'Камера выключена';
                if (animationId) {
                    cancelAnimationFrame(animationId);
                }
                hideCursor();
                setupMouseDrawing();
            } else {
                // Включаем камеру
                video.style.display = 'block';
                setupCamera();
            }
        }
        
        function saveDrawing() {
            const link = document.createElement('a');
            link.download = 'hand_drawing_' + Date.now() + '.png';
            link.href = canvas.toDataURL();
            link.click();
        }
        
        // Инициализируем мышиное управление как резервное
        setupMouseDrawing();
    </script>
</body>
</html>