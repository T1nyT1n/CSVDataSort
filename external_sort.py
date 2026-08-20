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
        log.success('Столбец содержит bool.')
        return bool(value)
    log.error('Столбец не содержит bool.')
    
    # FLOAT
    try:
        x = float(value)
        if math.isfinite(x):
            log.success('Столбец содержит float.')
            return x
    except ValueError:
        log.error('Столбец не содержит float.')
        pass

    # INT
    try:
        x = int(value)
        log.success('Столбец содержит int.')
        return x
    except ValueError:
        log.error('Столбец не содержит int.')
        pass

    # STR
    return str(value)

def write_sorted_chunk(chunk, num, key):
    """
    Sort list and write it to the file.
    """
    chunk_path : Path = Path(f'temp/chunk{num}.csv')
    chunk = sorted(chunk, key=key)
    # Убедиться, что папка существует.
    chunk_path.parent.mkdir(parents=True, exist_ok=True)
    with open_utf8(chunk_path, 'w+') as chunk_file:
        writer = csv.writer(chunk_file)
        writer.writerows(chunk)

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
                log.success('Записан заголовок итогового файла.')

            row = next(reader)
            row_index = header.index(key)
            sample_value = detect_column_type(row[row_index])
            if isinstance(sample_value, bool):
                log.log('Выбран bool() для приведения типов.')
                type_func = lambda value: bool(value)
            elif isinstance(sample_value, int):
                log.log('Выбран int() для приведения типов.')
                type_func = lambda value: int(value)
            elif isinstance(sample_value, float):
                log.log('Выбран float() для приведения типов.')
                type_func = lambda value: float(value)
            else:
                log.log('Выбран str() для приведения типов.')
                type_func = lambda value: str(value)
            
            sorting_key = lambda row: type_func(row[header.index(key)])
            
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

        next(reader) # Skip header.
        
        for row in reader:
            chunk.append(row)
            current_size += sys.getsizeof(row)
            if current_size >= max_chunk_size:
                write_sorted_chunk(chunk, file_chunks_amount, sorting_key)
                chunk = []
                current_size = 0
                file_chunks_amount += 1
                log.log(f'Создан чанк: {file_chunks_amount}.')

        write_sorted_chunk(chunk, file_chunks_amount, sorting_key)
        file_chunks_amount += 1
        log.log(f'Создан чанк: {file_chunks_amount}.')
    
    # Шаг 2: СЛИЯНИЕ. Открываем несколько чанков за раз и записываем
    # первый хороший вариант.
    with ExitStack() as stack:

        # Create new sorting key
        sorting_key = lambda item_tuple: type_func(item_tuple[1][row_index])
        
        # Open sorted file
        out_file = stack.enter_context(open_utf8(sorted_data_path, 'a'))
        out_writer = csv.writer(out_file)

        # Open chunk files
        chunks_file_readers = []
        for chunk_num in range(file_chunks_amount):
            file_path = Path(f'temp/chunk{chunk_num}.csv')
            file = stack.enter_context(open_utf8(file_path, 'r'))
            chunks_file_readers.append(csv.reader(file))
            log.log(f'Открыт файл {str(file_path)}.')

        first_lines = []
        for chunk in chunks_file_readers:
            try:
                cur_line = next(chunk)
            except StopIteration:
                chunks_file_readers.remove(chunk)
                log.log('Один из файлов закрыт.')
            else:
                first_lines.append( (chunk, cur_line) )

        first_lines = sorted(first_lines, key=sorting_key)
        out_writer.writerow(first_lines[0][1])
        while chunks_file_readers != []:
            cur_reader = first_lines[0][0]
            try:
                first_lines.append((cur_reader, next(cur_reader)))
            except StopIteration:
                chunks_file_readers.remove(cur_reader)
                first_lines.pop(0)
                log.log('Один из файлов закрыт.')
            else:
                first_lines.pop(0)
                first_lines = sorted(first_lines, key=sorting_key)
                out_writer.writerow(first_lines[0][1])

    log.success('Сортировка завершена!')

    # Удаляем чанки так как они больше не нужны.
    for chunk_num in range(file_chunks_amount):
        chunk_path = Path(f'temp/chunk{chunk_num}.csv')
        chunk_path.unlink(missing_ok = True)
        log.log(f'Удалён файл {str(chunk_path)}.')

    return 1

if __name__ == '__main__':
    print('\033[92mexternal_sort.py\033[0m') # lol idk
