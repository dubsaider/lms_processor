import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import json

def load_config(config_file="config.json"):
    """Загружает конфигурацию из JSON файла."""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"Конфигурация успешно загружена из '{config_file}'.")
        return config
    except FileNotFoundError:
        print(f"Ошибка: Файл конфигурации '{config_file}' не найден. Убедитесь, что он находится в той же папке, что и скрипт.")
        exit()
    except json.JSONDecodeError as e:
        print(f"Ошибка: Некорректный формат JSON в файле '{config_file}'. Проверьте синтаксис: {e}")
        exit()
    except Exception as e:
        print(f"Произошла непредвиденная ошибка при загрузке конфигурации: {e}")
        exit()

def process_lms_data_to_table_images():
    """
    Основная функция для обработки данных LMS, определения порогов,
    расчета финальных оценок и генерации изображений-таблиц для указанных групп.
    """

    # --- 1. Загрузка конфигурации ---
    config = load_config()

    # --- 2. Извлечение настроек из конфигурации ---
    THRESHOLDS = config['thresholds']
    COLUMNS_TO_ANALYZE_FOR_PASSING = list(THRESHOLDS.keys())

    GROUP_COLUMN = config['column_names']['group']
    RATING_COLUMN = config['column_names']['rating']
    FIO_COLUMN = config['column_names']['fio']
    FINAL_GRADE_COLUMN = config['column_names']['final_grade']
    ELIGIBILITY_COLUMN = config['column_names']['eligibility']

    GRADE_THRESHOLDS = config['grade_boundaries']
    DISPLAY_COLUMNS = config['display_columns']

    OUTPUT_IMAGES_DIR = config['file_paths']['output_images_dir']
    OUTPUT_DATA_DIR = config['file_paths']['output_data_dir']
    os.makedirs(OUTPUT_IMAGES_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DATA_DIR, exist_ok=True)

    CELL_HEIGHT = config['table_visuals']['cell_height']
    BASE_COLUMN_WIDTH = config['table_visuals']['base_column_width']
    FONT_SIZE_CELL = config['table_visuals']['font_size_cell']
    FONT_SIZE_HEADER = config['table_visuals']['font_size_header']
    HEADER_BG_COLOR = config['table_visuals']['header_bg_color']
    HEADER_TEXT_COLOR = config['table_visuals']['header_text_color']
    PASSED_CELL_COLOR = config['table_visuals']['passed_cell_color']
    FAILED_CELL_COLOR = config['table_visuals']['failed_cell_color']
    COLUMN_WIDTHS_RATIOS = config['table_visuals']['column_widths_ratios']
    
    GRADE_ORDER_FOR_SUMMARY = config['grade_order_for_summary']

    # --- 3. Запрос файла Excel у пользователя ---
    excel_file_path = input("Пожалуйста, введите полный путь к вашему Excel файлу LMS (например, C:\\Users\\User\\Desktop\\lms_data.xlsx): ")

    try:
        df = pd.read_excel(excel_file_path)
        print(f"Файл '{excel_file_path}' успешно загружен.")
    except FileNotFoundError:
        print(f"Ошибка: Файл не найден по пути '{excel_file_path}'. Пожалуйста, проверьте путь.")
        return
    except Exception as e:
        print(f"Произошла ошибка при чтении файла Excel: {e}")
        return

    required_columns_for_processing = [GROUP_COLUMN, RATING_COLUMN, FIO_COLUMN] + COLUMNS_TO_ANALYZE_FOR_PASSING
    missing_columns = [col for col in required_columns_for_processing if col not in df.columns]
    if missing_columns:
        print(f"Ошибка: В Excel файле отсутствуют следующие необходимые столбцы для обработки: {', '.join(missing_columns)}")
        print(f"Доступные столбцы: {', '.join(df.columns)}")
        return

    # --- 4. Определение статуса "Пройден" / "Не пройден" для каждого модуля/теста ---
    for col_name, threshold in THRESHOLDS.items():
        status_col_name = f"{col_name} - Статус"
        df[status_col_name] = df[col_name].apply(lambda x: "Пройден" if pd.notna(x) and x >= threshold else "Не пройден")
        print(f"Статус для '{col_name}' определен (порог: {threshold}).")

    # --- 5. Определение статуса "Допущен к оценке" ---
    df[ELIGIBILITY_COLUMN] = True
    for col_name in COLUMNS_TO_ANALYZE_FOR_PASSING:
        status_col_name = f"{col_name} - Статус"
        df[ELIGIBILITY_COLUMN] = df[ELIGIBILITY_COLUMN] & (df[status_col_name] == "Пройден")
    print(f"Статус '{ELIGIBILITY_COLUMN}' определен.")

    # --- 6. Расчет финальной оценки ---
    def calculate_final_grade(row):
        if not row[ELIGIBILITY_COLUMN]:
            return "Не допущен (не набран порог)"

        rating = row[RATING_COLUMN]
        if pd.isna(rating):
            return "Нет данных по рейтингу (допущен)"
        
        try:
            rating = float(rating)
        except ValueError:
            return "Ошибка: Некорректный рейтинг"

        if rating >= GRADE_THRESHOLDS['Отлично']:
            return "Отлично"
        elif rating >= GRADE_THRESHOLDS['Хорошо']:
            return "Хорошо"
        elif rating >= GRADE_THRESHOLDS['Удовлетворительно']:
            return "Удовлетворительно"
        else:
            return "Неудовлетворительно"

    df[FINAL_GRADE_COLUMN] = df.apply(calculate_final_grade, axis=1)
    print(f"Столбец '{FINAL_GRADE_COLUMN}' рассчитан.")

    output_excel_path = os.path.join(OUTPUT_DATA_DIR, "lms_data_processed.xlsx")
    df.to_excel(output_excel_path, index=False)
    print(f"\nОбновленные данные с колонками статусов и финальной оценки сохранены в: '{output_excel_path}'")


    # --- 7. Запрос групп у пользователя ---
    unique_groups = df[GROUP_COLUMN].unique()
    print(f"\nДоступные группы в файле: {', '.join(unique_groups)}")
    groups_input = input(f"Введите названия групп, для которых нужно создать изображения-таблицы (разделите запятой): ")
    requested_groups = [g.strip() for g in groups_input.split(',') if g.strip()]

    if not requested_groups:
        print("Не указаны группы для обработки. Завершение работы.")
        return

    # --- 8. Обработка каждой группы и генерация изображений-таблиц ---
    for group_name in requested_groups:
        print(f"\nОбработка группы: '{group_name}'...")

        group_df = df[df[GROUP_COLUMN] == group_name].copy()

        if group_df.empty:
            print(f"Внимание: В файле не найдено данных для группы '{group_name}'. Пропускаем.")
            continue

        display_df = group_df[DISPLAY_COLUMNS].fillna('')

        for col in ['Модуль 1', 'Модуль 2', 'Модуль 3', 'Итоговое тестирование', RATING_COLUMN]:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{float(x):.1f}" if pd.notna(x) and isinstance(x, (int, float)) else str(x))

        cell_text = display_df.values.tolist()
        col_labels = display_df.columns.tolist()

        num_rows = len(cell_text)
        num_cols = len(col_labels)
        
        fig_width = max(12, num_cols * BASE_COLUMN_WIDTH)
        fig_height = (num_rows + 1) * CELL_HEIGHT + 1

        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        ax.axis('off')
        ax.set_frame_on(False)

        col_widths_abs = []
        for col_label in col_labels:
            if col_label in COLUMN_WIDTHS_RATIOS:
                col_widths_abs.append(COLUMN_WIDTHS_RATIOS[col_label])
            else:
                col_widths_abs.append(COLUMN_WIDTHS_RATIOS['default'])

        total_relative_width = sum(col_widths_abs)
        if total_relative_width == 0:
            normalized_col_widths = [1.0 / num_cols] * num_cols
        else:
            normalized_col_widths = [w / total_relative_width for w in col_widths_abs]

        table = ax.table(cellText=cell_text,
                         colLabels=col_labels,
                         colWidths=normalized_col_widths,
                         loc='center',
                         bbox=[0, 0, 1, 1])

        table.auto_set_font_size(False)
        table.set_fontsize(FONT_SIZE_CELL)
        
        for (r_idx, c_idx), cell in table._cells.items():
            cell.set_edgecolor('black')
            if r_idx == 0:
                cell.set_facecolor(HEADER_BG_COLOR)
                cell.set_text_props(weight='bold', color=HEADER_TEXT_COLOR)
                cell.set_fontsize(FONT_SIZE_HEADER)
            else:
                cell.set_facecolor(PASSED_CELL_COLOR)
                cell.set_fontsize(FONT_SIZE_CELL)

                current_col_name = col_labels[c_idx]

                if current_col_name in COLUMNS_TO_ANALYZE_FOR_PASSING:
                    student_original_score = group_df.iloc[r_idx - 1][current_col_name]
                    
                    threshold = THRESHOLDS[current_col_name]

                    if pd.notna(student_original_score) and student_original_score < threshold:
                        cell.set_facecolor(FAILED_CELL_COLOR)
                
                if current_col_name in [FIO_COLUMN, GROUP_COLUMN]:
                    cell.set_text_props(ha='left', va='center')
                else:
                    cell.set_text_props(ha='center', va='center')
                
        plt.tight_layout()

        sanitized_group_name = group_name.replace("/", "_").replace("\\", "_")
        output_filename_table = os.path.join(OUTPUT_IMAGES_DIR, f'Группа_{sanitized_group_name}_РезультатыТаблица.png')
        plt.savefig(output_filename_table, dpi=300)
        plt.close(fig)
        print(f"Таблица результатов для группы '{group_name}' сохранена как '{output_filename_table}'")

        # --- Вывод сводки по финальным оценкам (текстовая сводка, как раньше) ---
        print(f"\n--- Сводка по финальным оценкам для группы '{group_name}' ---")
        grade_counts = group_df[FINAL_GRADE_COLUMN].value_counts(dropna=False)

        grade_counts = grade_counts.reindex(GRADE_ORDER_FOR_SUMMARY, fill_value=0)
        
        print(grade_counts.to_string())
        print(f"Всего студентов в группе: {len(group_df)}")
        print("--------------------------------------------------")

    print("\nОбработка завершена. Все изображения-таблицы сохранены в папке 'output_table_images', а обновленный Excel-файл - в 'output_data'.")

if __name__ == "__main__":
    process_lms_data_to_table_images()
