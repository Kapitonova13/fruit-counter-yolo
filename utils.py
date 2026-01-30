import os
import json
from datetime import datetime
import pandas as pd
from fpdf import FPDF
import numpy as np

def load_history(file_path='history.json'):
    """Загрузка истории из JSON"""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history, file_path='history.json'):
    """Сохранение истории в JSON"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def generate_excel(history_file, reports_folder):
    """Генерация Excel отчета"""
    history = load_history(history_file)

    if not history:
        return None

    # Создаем DataFrame
    data = []
    for entry in history[-20:]:  # Последние 10 записей
        row = {'Дата': entry['timestamp'], 'Всего фруктов': entry['total_fruits']}
        for fruit, count in entry['fruit_counts'].items():
            row[fruit] = count
        data.append(row)

    df = pd.DataFrame(data)

    # Сохраняем
    excel_filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    excel_path = os.path.join(reports_folder, excel_filename)
    df.to_excel(excel_path, index=False)

    return excel_filename