import os
import pandas as pd
from config_manager import load_config
from data_loader import get_excel_file_path, load_excel_data, validate_dataframe_columns, save_processed_excel
from data_processor import process_all_lms_data
from report_generator import get_groups_to_process, prepare_display_data, generate_table_image, print_grade_summary

def main():
    """
    Главная функция, оркестрирующая весь процесс обработки данных LMS.
    """
    config = load_config()
    if not config:
        return

    THRESHOLDS = config['thresholds']
    COLUMNS_TO_ANALYZE_FOR_PASSING = list(THRESHOLDS.keys())
    GROUP_COLUMN = config['column_names']['group']
    RATING_COLUMN = config['column_names']['rating']
    FIO_COLUMN = config['column_names']['fio']
    FINAL_GRADE_COLUMN = config['column_names']['final_grade']
    ELIGIBILITY_COLUMN = config['column_names']['eligibility']
    DISPLAY_COLUMNS = config['display_columns']
    OUTPUT_DATA_DIR = config['file_paths']['output_data_dir']
    GRADE_ORDER_FOR_SUMMARY = config['grade_order_for_summary']

    excel_file_path = get_excel_file_path()
    df = load_excel_data(excel_file_path)
    if df is None:
        return

    required_columns_for_processing = [GROUP_COLUMN, RATING_COLUMN, FIO_COLUMN] + COLUMNS_TO_ANALYZE_FOR_PASSING
    if not validate_dataframe_columns(df, required_columns_for_processing):
        return

    df_processed = process_all_lms_data(df, config)

    save_processed_excel(df_processed, OUTPUT_DATA_DIR, DISPLAY_COLUMNS)

    requested_groups = get_groups_to_process(df_processed, GROUP_COLUMN)
    if not requested_groups:
        print("Не указаны группы для обработки изображений. Завершение работы.")
        return

    for group_name in requested_groups:
        print(f"\nОбработка группы: '{group_name}'...")

        group_df = df_processed[df_processed[GROUP_COLUMN] == group_name].copy()
        
        if group_df.empty:
            print(f"Внимание: В файле не найдено данных для группы '{group_name}'. Пропускаем.")
            continue
        
        group_df.sort_values(by=FIO_COLUMN, inplace=True)

        display_df = prepare_display_data(group_df, DISPLAY_COLUMNS, RATING_COLUMN)

        generate_table_image(display_df, group_df, group_name, config)

        print_grade_summary(group_df, FINAL_GRADE_COLUMN, GRADE_ORDER_FOR_SUMMARY, group_name)

    print("\nПолная обработка завершена. Все отчеты и обновленный Excel-файл готовы.")

if __name__ == "__main__":
    main()
