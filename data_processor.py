import pandas as pd
import numpy as np

def apply_module_statuses(df: pd.DataFrame, thresholds: dict) -> pd.DataFrame:
    """
    Определяет статус "Пройден" / "Не пройден" для каждого модуля/теста
    на основе заданных порогов.
    """
    df_copy = df.copy()
    for col_name, threshold in thresholds.items():
        if col_name in df_copy.columns:
            status_col_name = f"{col_name} - Статус"
            df_copy[status_col_name] = df_copy[col_name].apply(
                lambda x: "Пройден" if pd.notna(x) and x >= threshold else "Не пройден"
            )
            print(f"Статус для '{col_name}' определен (порог: {threshold}).")
        else:
            print(f"Предупреждение: Колонка '{col_name}' для определения статуса не найдена в данных. Пропускаем.")
    return df_copy

def determine_eligibility(df: pd.DataFrame, columns_to_analyze: list, eligibility_column_name: str) -> pd.DataFrame:
    """
    Определяет статус "Допущен к оценке" на основе прохождения всех необходимых модулей.
    """
    df_copy = df.copy()
    df_copy[eligibility_column_name] = True
    
    status_columns_exist = True
    for col_name in columns_to_analyze:
        status_col = f"{col_name} - Статус"
        if status_col not in df_copy.columns:
            print(f"Ошибка: Колонка статуса '{status_col}' не найдена. Не могу определить допуск корректно.")
            status_columns_exist = False
            break
    
    if status_columns_exist:
        for col_name in columns_to_analyze:
            status_col = f"{col_name} - Статус"
            df_copy[eligibility_column_name] = df_copy[eligibility_column_name] & (df_copy[status_col] == "Пройден")
        print(f"Статус '{eligibility_column_name}' определен.")
    else:
        print(f"Статус '{eligibility_column_name}' не был полностью определен из-за отсутствующих колонок статусов.")
    return df_copy

def calculate_final_grades(df: pd.DataFrame, eligibility_column: str, rating_column: str, final_grade_column: str, grade_thresholds: dict) -> pd.DataFrame:
    """
    Рассчитывает финальную оценку для каждого студента.
    """
    df_copy = df.copy()

    def _calculate_grade(row):
        if not row[eligibility_column]:
            return "Не допущен (не набран порог)"

        rating = row[rating_column]
        if pd.isna(rating):
            return "Нет данных по рейтингу (допущен)"
        
        try:
            rating = float(rating)
        except ValueError:
            return "Ошибка: Некорректный рейтинг"

        if rating >= grade_thresholds['Отлично']:
            return "Отлично"
        elif rating >= grade_thresholds['Хорошо']:
            return "Хорошо"
        elif rating >= grade_thresholds['Удовлетворительно']:
            return "Удовлетворительно"
        else:
            return "Неудовлетворительно"

    df_copy[final_grade_column] = df_copy.apply(_calculate_grade, axis=1)
    print(f"Столбец '{final_grade_column}' рассчитан.")
    return df_copy

def process_all_lms_data(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Оркестрирует весь процесс обработки данных LMS.
    """
    THRESHOLDS = config['thresholds']

    COLUMNS_TO_ANALYZE_FOR_PASSING = list(THRESHOLDS.keys())
    RATING_COLUMN = config['column_names']['rating']
    FINAL_GRADE_COLUMN = config['column_names']['final_grade']
    ELIGIBILITY_COLUMN = config['column_names']['eligibility']
    GRADE_THRESHOLDS = config['grade_boundaries']

    df = apply_module_statuses(df, THRESHOLDS)

    df = determine_eligibility(df, COLUMNS_TO_ANALYZE_FOR_PASSING, ELIGIBILITY_COLUMN)

    df = calculate_final_grades(df, ELIGIBILITY_COLUMN, RATING_COLUMN, FINAL_GRADE_COLUMN, GRADE_THRESHOLDS)

    return df
