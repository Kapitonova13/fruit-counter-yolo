import os
import base64
from flask import Flask, render_template, request, jsonify, send_from_directory
from models import process_image
from utils import (
    load_history, save_history, generate_excel
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fruit-counter-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULTS_FOLDER'] = 'results'
app.config['REPORTS_FOLDER'] = 'reports'

# Создаем необходимые папки
for folder in [app.config['UPLOAD_FOLDER'],
               app.config['RESULTS_FOLDER'],
               app.config['REPORTS_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

HISTORY_FILE = 'history.json'

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/process_file', methods=['POST'])
def process_file_route():
    """Обработка загруженного файла"""
    if 'file' not in request.files:
        return jsonify({'error': 'Файл не выбран'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400

    results = process_image(file, is_base64=False, app=app)

    # для сохранения истории
    if 'success' in results and results['success']:
        history = load_history(HISTORY_FILE)
        history.append({
            'timestamp': results.get('timestamp', ''),
            'fruit_counts': results.get('fruit_counts', {}),
            'total_fruits': results.get('total_fruits', 0),
            'result_image': results.get('result_image', '')
        })
        save_history(history, HISTORY_FILE)
    
    return jsonify(results)

@app.route('/process_camera', methods=['POST'])
def process_camera_route():
    """Обработка фото с камеры"""
    if 'image' not in request.form:
        return jsonify({'error': 'Изображение не получено'}), 400

    image_data = request.form['image']
    results = process_image(image_data, is_base64=True, app=app)


    # для сохранения истории
    if 'success' in results and results['success']:
        history = load_history(HISTORY_FILE)
        history.append({
            'timestamp': results.get('timestamp', ''),
            'fruit_counts': results.get('fruit_counts', {}),
            'total_fruits': results.get('total_fruits', 0),
            'result_image': results.get('result_image', '')
        })
        save_history(history, HISTORY_FILE)
        
    return jsonify(results)

@app.route('/results/<filename>')
def get_result_image(filename):
    """Получение обработанного изображения"""
    return send_from_directory(app.config['RESULTS_FOLDER'], filename)

@app.route('/reports/<filename>')
def get_report(filename):
    """Получение отчета"""
    return send_from_directory(app.config['REPORTS_FOLDER'], filename)

@app.route('/generate_excel')
def generate_excel_route():
    """Генерация Excel"""
    excel_filename = generate_excel(HISTORY_FILE, app.config['REPORTS_FOLDER'])
    if not excel_filename:
        return jsonify({'error': 'Нет данных для отчета'})

    return jsonify({'filename': excel_filename})

@app.route('/get_history')
def get_history_route():
    """Получение истории"""
    history = load_history(HISTORY_FILE)
    return jsonify(history)

@app.route('/clear_history')
def clear_history_route():
    """Очистка истории"""
    save_history([], HISTORY_FILE)
    return jsonify({'success': True})

if __name__ == '__main__':
    print("🚀 Запускаю веб-приложение...")
    print(f"📱 Откройте в браузере: http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)