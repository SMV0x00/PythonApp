from flask import Flask, request, jsonify

# Создаем Flask-приложение
app = Flask(__name__)

# Определяем функцию для расчета площади материала
# и выбора подходящей ширины рулона

def Material_Roll_Area(width, height, count, setup_length, roll_widths):
    roll_length = 1000000  # 1000 метров, длина рулона
    best_area = float('inf')  # Минимальная площадь материала (инициализируем бесконечностью)
    best_roll_width = None  # Оптимальная ширина рулона
    error_message = ""  # Сообщение об ошибке

    # Перебираем все доступные ширины рулонов
    for roll_width in roll_widths:
        # Проверяем, помещается ли макет горизонтально или вертикально в рулон
        can_fit_horizontally = width <= roll_width
        fits_vertically = height <= roll_width

        # Если макет не помещается ни в одном из положений, пропускаем рулон
        if not (can_fit_horizontally or fits_vertically):
            continue

        # Расчет для горизонтального размещения макетов
        if can_fit_horizontally:
            layouts_per_row = max(1, roll_width // width)  # Сколько макетов помещается в ряд
            rows_per_length = roll_length // height  # Сколько рядов помещается по длине рулона
            total_horizontal_length = ((count + layouts_per_row - 1) // layouts_per_row) * height + setup_length
            horizontal_area = total_horizontal_length * roll_width
        else:
            horizontal_area = float('inf')  # Если горизонтально не помещается

        # Расчет для вертикального размещения макетов
        if fits_vertically:
            layouts_per_row_vert = max(1, roll_width // height)  # Сколько макетов помещается в ряд вертикально
            rows_per_length_vert = roll_length // width  # Сколько рядов помещается по длине рулона
            total_vertical_length = ((count + layouts_per_row_vert - 1) // layouts_per_row_vert) * width + setup_length
            vertical_area = total_vertical_length * roll_width
        else:
            vertical_area = float('inf')  # Если вертикально не помещается

        # Сравниваем текущие площади с лучшим найденным вариантом
        if horizontal_area < best_area:
            best_area = horizontal_area
            best_roll_width = roll_width

        if vertical_area < best_area:
            best_area = vertical_area
            best_roll_width = roll_width

    # Если ни один рулон не подошел, возвращаем сообщение об ошибке
    if best_roll_width is None:
        error_message = "Макет не помещается ни в один из доступных рулонов."
        return 0, None, error_message

    # Переводим площадь из квадратных миллиметров в квадратные метры
    best_area_m2 = best_area / 1_000_000
    return best_area_m2, best_roll_width, error_message

# Определяем маршрут API для обработки данных
@app.route('/process', methods=['POST'])
def process_data():
    try:
        # Получаем данные из JSON-запроса
        data = request.json
        width = data.get('width')
        height = data.get('height')
        count = data.get('count')
        setup_length = data.get('setup_length')
        roll_widths = data.get('roll_widths')

        # Вызываем функцию расчета с переданными параметрами
        result_area, roll_width, error = Material_Roll_Area(width, height, count, setup_length, roll_widths)
        return jsonify({
            "area": result_area,  # Площадь используемого материала
            "roll_width": roll_width,  # Оптимальная ширина рулона
            "error": error  # Сообщение об ошибке, если есть
        })
    except Exception as e:
        # Обрабатываем исключения и возвращаем ошибку
        return jsonify({"error": str(e)}), 400

# Запуск Flask-приложения на указанном хосте и порте
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)