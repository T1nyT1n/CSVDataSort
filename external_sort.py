import csv
import sys
import math
import logger as log
from pathlib import Path
from collections.abc import Iterator
from contextlib import ExitStack
from utils import *

# 1024 ** 3 bytes in one gigabyte.
max_chunk_size = 0.01 * (1024 ** 3)

def convert_string_into_bool(value):
    value = value.lower()
    if value == 'true':
        return True
    else:
        return False

def detect_column_type(value):
    """
    Detect data types for one row.
    """
    # BOOL
    stripped_value = value.strip()
    low = stripped_value.lower()
    if low in {'true','false'}:
        log.log('Столбец содержит bool.')
        if low == 'true':
            return True
        else:
            return False
    log.log('Столбец не содержит bool.')
    
    # INT
    try:
        x = int(value)
        log.log('Столбец содержит int.')
        return x
    except ValueError:
        log.log('Столбец не содержит int.')
        pass

    # FLOAT
    try:
        x = float(value)
        if math.isfinite(x):
            log.log('Столбец содержит float.')
            return x
    except ValueError:
        log.log('Столбец не содержит float.')
        pass

    # STR
    return str(value)

def write_sorted_chunk(chunk, num, key):
    """
    Sort list and write it to the file.
    """
    chunk_path : Path = Path(f'temp/chunk{num}.csv')
    chunk = sorted(chunk, key=key)
    chunk_path.parent.mkdir(parents=True, exist_ok=True)
    with open_utf8(chunk_path, 'w+') as chunk_file:
        writer = csv.writer(chunk_file)
        writer.writerows(chunk)

def start(key: str, data_path: Path, sorted_data_path: Path) -> int:
    """
    Start external sorting.
    """
    # Step 0: get the sorting key.

    try:
        with open_utf8(data_path, 'r') as data_file:
            reader = csv.reader(data_file)
            
            # Write file header to sorted data file and truncate that
            # file.
            with open_utf8(sorted_data_path, 'w') as sorted_data_file:
                writer = csv.writer(sorted_data_file)
                header = next(reader)
                writer.writerow(header)
                log.log('Записан заголовок итогового файла.')

            row = next(reader)
            row_index = header.index(key)
            sample_value = detect_column_type(row[row_index])
            if isinstance(sample_value, bool):
                log.log('Выбран bool() для приведения типов.')
                type_func = lambda value: convert_string_into_bool(value)
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
    
    # Step 1: SPLIT data into chunks.
    with open_utf8(data_path, 'r') as data_file:
        reader = csv.reader(data_file)
        file_chunks_amount = 0
        chunk = []
        current_size = 0

        next(reader) # Skip header.

        log.log(f'Идёт создание чанков...')
        
        for row in reader:
            chunk.append(row)
            current_size += sys.getsizeof(row)
            if current_size >= max_chunk_size:
                write_sorted_chunk(chunk, file_chunks_amount, sorting_key)
                chunk = []
                current_size = 0
                file_chunks_amount += 1

        write_sorted_chunk(chunk, file_chunks_amount, sorting_key)
        file_chunks_amount += 1

        log.log(f'Чанков создано: {file_chunks_amount}')
    
    # Step 2: MERGE data from chunks to the final file.
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

        log.log(f'Файлов открыто: {len(chunks_file_readers)}')
        log.log(f'Идёт слияние чанков...')

        # Read first lines from every chunk
        first_lines = []
        for chunk in chunks_file_readers:
            try:
                cur_line = next(chunk)
            except StopIteration:
                chunks_file_readers.remove(chunk)
            else:
                first_lines.append( (chunk, cur_line) )
        
        # Write the first line and get a new one
        first_lines.sort(key=sorting_key)
        while chunks_file_readers:
            cur_reader, cur_line = first_lines.pop(0)
            out_writer.writerow(cur_line)
            try:
                first_lines.append((cur_reader, next(cur_reader)))
                first_lines.sort(key=sorting_key)
            except StopIteration:
                chunks_file_readers.remove(cur_reader)

    log.success('Сортировка завершена!')

    # Delete chunks because they're no longer needed
    for chunk_num in range(file_chunks_amount):
        chunk_path = Path(f'temp/chunk{chunk_num}.csv')
        chunk_path.unlink(missing_ok = True)
    
    log.log(f'Чанки удалены.')

    return 1

if __name__ == '__main__':
    print('\033[92mexternal_sort.py\033[0m') # lol idk
