import pandas as pd
import os

def get_excel_file_path() -> str:
    """Запрашивает у пользователя полный путь к Excel файлу LMS."""
    return input("Пожалуйста, введите полный путь к вашему Excel файлу LMS (например, C:\\Users\\User\\Desktop\\lms_data.xlsx): ")

def load_excel_data(file_path: str) -> pd.DataFrame:
    """Загружает данные из Excel-файла."""
    try:
        df = pd.read_excel(file_path)
        print(f"Файл '{file_path}' успешно загружен.")
        return df
    except FileNotFoundError:
        print(f"Ошибка: Файл не найден по пути '{file_path}'. Пожалуйста, проверьте путь.")
        return None
    except pd.errors.EmptyDataError:
        print(f"Ошибка: Файл '{file_path}' пуст.")
        return None
    except Exception as e:
        print(f"Произошла ошибка при чтении файла Excel: {e}")
        return None

def validate_dataframe_columns(df: pd.DataFrame, required_columns: list) -> bool:
    """
    Проверяет наличие всех необходимых столбцов в загруженном DataFrame.
    Выводит сообщение об ошибке, если столбцы отсутствуют.
    """
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Ошибка: В Excel файле отсутствуют следующие необходимые столбцы для обработки: {', '.join(missing_columns)}")
        print(f"Доступные столбцы: {', '.join(df.columns)}")
        return False
    return True

def save_processed_excel(df: pd.DataFrame, output_dir: str, columns_to_save: list, filename: str = "lms_data_processed.xlsx"):
    """
    Сохраняет обработанный DataFrame в Excel-файл, включая только указанные колонки.
    Создает директорию, если она не существует.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    try:
        existing_columns = [col for col in columns_to_save if col in df.columns]
        if len(existing_columns) != len(columns_to_save):
            missing_cols_for_save = set(columns_to_save) - set(existing_columns)
            print(f"Предупреждение: Некоторые колонки, указанные для сохранения, отсутствуют в DataFrame и будут пропущены: {', '.join(missing_cols_for_save)}")

        df[existing_columns].to_excel(output_path, index=False)
        print(f"\nОбновленные данные (только важные колонки для отображения) сохранены в: '{output_path}'")
    except KeyError as e:
        print(f"Ошибка: Не удалось сохранить Excel-файл. Один из столбцов для сохранения отсутствует в DataFrame: {e}")
        print(f"Убедитесь, что все столбцы, указанные в 'display_columns' в config.json, существуют после обработки.")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка при сохранении Excel-файла: {e}")
