# Скрипт для анализа данных LMS и генерации табличных отчетов

Этот Python-скрипт предназначен для обработки выгрузок из LMS (системы управления обучением), расчета статусов прохождения модулей и итоговых оценок на основе заданных порогов, а также для генерации наглядных табличных отчетов в виде изображений для каждой группы.

## Особенности

*   **Чтение данных из Excel:** Автоматически считывает данные из указанного Excel-файла LMS.
*   **Определение прохождения порогов:** Рассчитывает, прошел ли студент пороговое значение по каждому модулю и итоговому тестированию.
*   **Расчет финальной оценки:** Определяет итоговую оценку студента на основе набранных баллов и статуса прохождения всех ключевых порогов. Если порог не набран, оценка не выставляется.
*   **Генерация табличных изображений:** Для каждой указанной группы создается отдельное изображение (PNG), представляющее собой таблицу с ФИО студентов, их баллами по модулям/тестированию, рейтингом и финальной оценкой.
*   **Цветовая индикация:** Ячейки с баллами, которые не достигли порога, подсвечиваются для лучшей наглядности.
*   **Сохранение обработанных данных:** Новый Excel-файл с добавленными столбцами статусов и финальных оценок сохраняется для дальнейшего использования.
*   **Сводка по оценкам:** В консоль выводится текстовая сводка распределения финальных оценок для каждой группы.
*   **Гибкая конфигурация:** Все ключевые параметры (названия столбцов, пороги, пути вывода, визуальные настройки таблицы) вынесены в отдельный файл `config.json`, что позволяет легко адаптировать скрипт без изменения кода.

## Предварительные требования

Для запуска скрипта вам понадобится:

*   **Python 3.7+** (рекомендуется последняя версия).
*   **`pip`** (обычно поставляется вместе с Python).
*   **Необходимые библиотеки Python:** `pandas`, `matplotlib`, `openpyxl`.

## Установка

1.  **Скачайте файлы скрипта:**
    *   `lms_processor.py`
    *   `config.json`
2.  **Разместите их в одной директории** на вашем компьютере.
3.  **Установите необходимые библиотеки** с помощью `pip`. Откройте командную строку (или терминал) и выполните следующую команду:
    ```python
    pip install pandas matplotlib openpyxl
    ```

## Использование

1.  Поместите ваш Excel-файл с выгрузкой из LMS в любое удобное для вас место.
2.  Откройте командную строку (CMD на Windows) или терминал (macOS/Linux).
3.  Перейдите в директорию, где вы сохранили скрипт. Например, если скрипт находится на рабочем столе:

```bash
cd C:\Users\ВашеИмяПользователя\Desktop\
```

4.  Запустите скрипт:

    `python lms_processor.py`

5.  Следуйте инструкциям в консоли:
    -   Скрипт запросит полный путь к вашему Excel-файлу LMS. Введите его и нажмите Enter.
        -   Пример: `C:\Users\ВашеИмяПользователя\Documents\выгрузка_lms.xlsx`
    -   Затем скрипт покажет список уникальных групп, найденных в файле, и попросит ввести названия групп, для которых нужно создать отчеты. Вводите названия групп через запятую.
        -   Пример: `Группа А, Группа Б, Группа В`
6.  После завершения работы скрипт сообщит о сохранении файлов.

---

## Выходные данные

Скрипт создает две новые папки в той же директории, где находится `lms_processor.py`:

-   `output_table_images/`: Содержит PNG-изображения таблиц для каждой обработанной группы. Имена файлов формируются как `Группа_НазваниеГруппы_РезультатыТаблица.png`.
-   `output_data/`: Содержит новый Excel-файл `lms_data_processed.xlsx`. Этот файл включает все оригинальные данные, а также новые столбцы с рассчитанными статусами прохождения модулей (`Модуль X - Статус`), статусом допуска к оценке (`Допущен к оценке`) и финальной оценкой (`Финальная ОЦЕНКА`).
-   Консольный вывод: В терминале вы увидите сводки по финальным оценкам для каждой группы.

---

## Конфигурация (`config.json`)

Файл `config.json` позволяет настроить поведение скрипта без изменения его исходного кода. Это стандартный формат JSON (JavaScript Object Notation), который легко читается и редактируется.

**Важно**: После любых изменений в `config.json` обязательно сохраните файл!

Вот основные секции и параметры:

```json
{
  "file_paths": {
    "output_images_dir": "output_table_images",
    "output_data_dir": "output_data"
  },
  "column_names": {
    "group": "Название потока",
    "rating": "Рейтинг в 1С",
    "fio": "Фамилия и имя",
    "final_grade": "Финальная ОЦЕНКА",
    "eligibility": "Допущен к оценке"
  },
  "thresholds": {
    "Модуль 1": 13,
    "Модуль 2": 18,
    "Модуль 3": 15,
    "Итоговое тестирование": 15
  },
  "grade_boundaries": {
    "Отлично": 86,
    "Хорошо": 76,
    "Удовлетворительно": 61
  },
  "display_columns": [
    "Фамилия и имя",
    "Название потока",
    "Модуль 1",
    "Модуль 2",
    "Модуль 3",
    "Итоговое тестирование",
    "Рейтинг в 1С",
    "Финальная ОЦЕНКА"
  ],
  "table_visuals": {
    "cell_height": 0.5,
    "base_column_width": 2.0,
    "font_size_cell": 10,
    "font_size_header": 11,
    "header_bg_color": "#4CAF50",
    "header_text_color": "white",
    "passed_cell_color": "white",
    "failed_cell_color": "#FFDDDD",
    "column_widths_ratios": {
      "Фамилия и имя": 0.25,
      "Название потока": 0.15,
      "Финальная ОЦЕНКА": 0.25,
      "default": 0.1
    }
  },
  "grade_order_for_summary": [
    "Отлично",
    "Хорошо",
    "Удовлетворительно",
    "Неудовлетворительно",
    "Нет данных по рейтингу (допущен)",
    "Не допущен (не набран порог)",
    "Ошибка: Некорректный рейтинг"
  ]
}
```

### Подробное описание параметров:

-   **`file_paths`**:
    -   `"output_images_dir"`: Название папки для сохранения изображений-таблиц.
    -   `"output_data_dir"`: Название папки для сохранения обработанного Excel-файла.
-   **`column_names`**: Крайне важно, чтобы эти названия **ТОЧНО соответствовали** заголовкам столбцов в вашем Excel-файле!
    -   `"group"`: Название столбца, содержащего группы (потоки) студентов.
    -   `"rating"`: Название столбца с общим рейтингом студента (используется для финальной оценки).
    -   `"fio"`: Название столбца с фамилией и именем студента.
    -   `"final_grade"`: Название для нового столбца, который будет содержать рассчитанную финальную оценку.
    -   `"eligibility"`: Название для нового столбца, указывающего, допущен ли студент к оценке.
-   **`thresholds`**:
    -   Список модулей и их соответствующих пороговых значений (минимальный балл для прохождения). Ключи должны точно совпадать с названиями столбцов модулей в Excel.
    -   Пример: `"Модуль 1": 13` означает, что для прохождения "Модуля 1" требуется не менее 13 баллов.
-   **`grade_boundaries`**:
    -   Определяет границы баллов для выставления финальных оценок (`"Отлично"`, `"Хорошо"`, `"Удовлетворительно"`). Баллы ниже `"Удовлетворительно"` будут считаться `"Неудовлетворительно"`.
-   **`display_columns`**:
    -   Список столбцов, которые будут отображены в итоговом изображении-таблице. Порядок столбцов в этом списке определит порядок их отображения в таблице. Убедитесь, что здесь присутствуют все столбцы, которые вы хотите видеть.
-   **`table_visuals`**: Настройки внешнего вида сгенерированных таблиц.
    -   `"cell_height"`: Высота одной ячейки таблицы в дюймах. Влияет на общую высоту изображения.
    -   `"base_column_width"`: Базовая ширина столбца в дюймах. Используется для расчета общей ширины изображения.
    -   `"font_size_cell"`: Размер шрифта для данных в ячейках таблицы.
    -   `"font_size_header"`: Размер шрифта для заголовков столбцов.
    -   `"header_bg_color"`: Цвет фона ячеек заголовков (в формате `HEX-кода`).
    -   `"header_text_color"`: Цвет текста заголовков.
    -   `"passed_cell_color"`: Цвет фона ячеек для модулей, где порог пройден.
    -   `"failed_cell_color"`: Цвет фона ячеек для модулей, где порог не пройден.
    -   `"column_widths_ratios"`: Определяет относительную ширину для отдельных столбцов в таблице.
        -   Ключи — это названия столбцов, значения — их относительная ширина.
        -   `"default"`: Используется для всех столбцов, не перечисленных явно.
        -   Значения являются "весами"; скрипт автоматически нормализует их так, чтобы их сумма составляла `1.0`. Изменение этих значений позволит вам сделать одни столбцы шире, другие уже.
-   **`grade_order_for_summary`**:
    -   Определяет порядок отображения категорий оценок в текстовой сводке, которая выводится в консоль.
