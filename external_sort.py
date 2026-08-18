import csv
import sys
import math
import logger as log
from pathlib import Path
from collections.abc import Iterator
from contextlib import ExitStack
from utils import *

# 1024 ** 3 байт в гигабайте.
# TODO: автоматизировать вычисление максимального размера чанка на
# основе количества доступной ОЗУ.
max_chunk_size = 0.01 * (1024 ** 3)

def detect_column_type(value):
    """
    Detect data types for one row.
    """
    # BOOL
    stripped_value = value.strip()
    low = stripped_value.lower()
    if low in {'true','false'}:
        return bool(value)
    
    # FLOAT
    try:
        x = float(value)
        if math.isfinite(x):
            return x
    except ValueError:
        pass

    # INT
    try:
        x = int(value)
        return x
    except ValueError:
        pass

    # STR
    return str(value)

def start(key: str, data_path: Path, sorted_data_path: Path) -> int:
    """
    Start external sorting.
    """
    # Шаг 0: ПОЛУЧИТЬ КЛЮЧ СОРТИРОВКИ. Для того, чтобы сортировать по
    # столбцу нужно знать, какой тип данных лежит в этом столбце.

    try:
        with open_utf8(data_path, 'r') as data_file:
            reader = csv.reader(data_file)
            
            # Записать заголовок CSV файла, а за одним ещё и
            # truncate-нуть его за счёт режима 'w'.
            with open_utf8(sorted_data_path, 'w') as sorted_data_file:
                writer = csv.writer(sorted_data_file)
                header = next(reader)
                writer.writerow(header)

            row = next(reader)
            column_type = detect_column_type(row[header.index(key)])
            if column_type is int:
                type_func = lambda value: int(value)
            elif column_type is float:
                type_func = lambda value: float(value)
            elif column_type is bool:
                type_func = lambda value: bool(value)
            else:
                type_func = lambda value: str(value)
            
    except FileNotFoundError:
        log.error(('Файл для сортировки не найден. Используйте '
                   '\033[92mcsv_generator\033[0m.'))
        return 2
    
    # Шаг 1: РАЗДЕЛЕНИЕ. Разделяем внешние данные на чанки и сортируем
    # каждый в отдельности.
    with open_utf8(data_path, 'r') as data_file:
        reader = csv.reader(data_file)
        file_chunks_amount = 0
        chunk = []
        current_size = 0
        
        for row in reader:
            chunk.append(row)
            current_size += sys.getsizeof(row)
            if current_size >= max_chunk_size:
                chunk_path : Path = Path((f'temp/chunk{file_chunks_amount}'
                                           '.csv'))
                sorting_key = lambda row: type_func(row[header.index(key)])
                chunk = sorted(chunk, key=sorting_key)
                # Убедиться, что папка существует.
                chunk_path.parent.mkdir(parents=True, exist_ok=True)
                with open_utf8(chunk_path, 'w+') as chunk_file:
                    writer = csv.writer(chunk_file)
                    writer.writerows(chunk)
                chunk = []
                current_size = 0
                file_chunks_amount += 1
                log.log(f'Создан чанк: {file_chunks_amount}.')
    
    # Шаг 2: СЛИЯНИЕ. Открываем несколько чанков за раз и записываем
    # первый хороший вариант.
    with ExitStack() as stack:
        chunks_file_objects = []
        for chunk_num in range(file_chunks_amount):
            file_path = Path(f'temp/chunk{chunk_num}.csv')
            file = stack.enter_context(open_utf8(file_path, 'r'))
            chunks_file_objects.append(file)
            log.log(f'Открыт файл {str(file_path)}.')

        while chunks_file_objects != []:
            first_lines = []
            for chunk in chunks_file_objects:
                chunk_reader = csv.reader(chunk)
                try:
                    cur_line = next(chunk_reader)
                except StopIteration:
                    chunks_file_objects.remove(chunk)
                else:
                    first_lines.append(cur_line)
            first_lines = sorted(first_lines, key=sorting_key)
            if first_lines != []:
                open_utf8(sorted_data_path, 'a').write(
                        ','.join(first_lines[0]) + '\n')

    # Удаляем чанки так как они больше не нужны.
    for chunk_num in range(file_chunks_amount):
        chunk_path = Path(f'temp/chunk{chunk_num}.csv')
        chunk_path.unlink(missing_ok = True)
        log.log(f'Удалён файл {str(chunk_path)}.')

    return 1

if __name__ == '__main__':
    print('\033[92mexternal_sort.py\033[0m')
