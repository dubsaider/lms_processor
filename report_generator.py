import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

def get_groups_to_process(df: pd.DataFrame, group_column: str) -> list:
    """
    Запрашивает у пользователя, для каких групп нужно создать изображения-таблицы.
    Возвращает список очищенных названий групп.
    """
    unique_groups = df[group_column].unique()
    print(f"\nДоступные группы в файле: {', '.join(unique_groups)}")
    groups_input = input(f"Введите названия групп, для которых нужно создать изображения-таблицы (разделите запятой): ")
    requested_groups = [g.strip() for g in groups_input.split(',') if g.strip()]
    return requested_groups

def prepare_display_data(group_df: pd.DataFrame, display_columns: list, rating_column: str) -> pd.DataFrame:
    """
    Готовит DataFrame для отображения в виде таблицы-изображения.
    Заполняет NaN пустыми строками и форматирует числовые колонки.
    """
    display_df = group_df[display_columns].fillna('')
    columns_with_scores = list(group_df.columns[group_df.columns.isin(list(group_df.columns)) & 
                                                group_df.columns.isin(list(group_df.columns)) & 
                                                ~group_df.columns.str.contains(' - Статус') & 
                                                ~group_df.columns.str.contains('Допущен к оценке') &
                                                ~group_df.columns.str.contains('Финальная оценка') &
                                                (group_df.dtypes == float) | (group_df.dtypes == int)].tolist())
    
    if rating_column in display_df.columns and not pd.api.types.is_numeric_dtype(display_df[rating_column]):
        columns_with_scores.append(rating_column)

    for col in columns_with_scores:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(
                lambda x: f"{float(x):.1f}" if pd.notna(x) and isinstance(x, (int, float)) else str(x)
            )

    return display_df

def generate_table_image(display_df: pd.DataFrame, original_group_df: pd.DataFrame, group_name: str, config: dict):
    """
    Создает и сохраняет изображение-таблицу для одной группы.
    """
    OUTPUT_IMAGES_DIR = config['file_paths']['output_images_dir']
    os.makedirs(OUTPUT_IMAGES_DIR, exist_ok=True)

    CELL_HEIGHT = config['table_visuals']['cell_height']
    BASE_COLUMN_WIDTH = config['table_visuals']['base_column_width']
    FONT_SIZE_CELL = config['table_visuals']['font_size_cell']
    FONT_SIZE_HEADER = config['table_visuals']['font_size_header']
    HEADER_BG_COLOR = config['table_visuals']['header_bg_color']
    HEADER_TEXT_COLOR = config['table_visuals']['header_text_color']
    PASSED_CELL_COLOR = config['table_visuals']['passed_cell_color']
    FAILED_CELL_COLOR = config['table_visuals']['failed_cell_color']
    COLUMN_WIDTHS_RATIOS = config['table_visuals']['column_widths_ratios']
    
    THRESHOLDS = config['thresholds']
    COLUMNS_TO_ANALYZE_FOR_PASSING = list(THRESHOLDS.keys())
    FIO_COLUMN = config['column_names']['fio']
    GROUP_COLUMN = config['column_names']['group']

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
        col_widths_abs.append(COLUMN_WIDTHS_RATIOS.get(col_label, COLUMN_WIDTHS_RATIOS['default']))

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
                student_original_score = original_group_df.iloc[r_idx - 1][current_col_name]
                
                threshold = THRESHOLDS.get(current_col_name)

                if pd.notna(student_original_score) and isinstance(student_original_score, (int, float)) and student_original_score < threshold:
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


def print_grade_summary(group_df: pd.DataFrame, final_grade_column: str, grade_order: list, group_name: str):
    """
    Выводит текстовую сводку по финальным оценкам для группы.
    """
    print(f"\n--- Сводка по финальным оценкам для группы '{group_name}' ---")
    grade_counts = group_df[final_grade_column].value_counts(dropna=False)
    grade_counts = grade_counts.reindex(grade_order, fill_value=0)
    
    print(grade_counts.to_string())
    print(f"Всего студентов в группе: {len(group_df)}")
    print("--------------------------------------------------")
