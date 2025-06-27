import json

def load_config(config_file: str = "config.json") -> dict:
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
