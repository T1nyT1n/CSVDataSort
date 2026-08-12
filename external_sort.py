import csv
import sys
import config
import logger as log
from pathlib import Path
from collections.abc import Iterator
from contextlib import ExitStack

# Максимальный размер чанка.
# 1024 ** 3 байт в гигабайте.
if config.auto_detect_ram == True:
    # TODO: автоматизировать вычисление максимального размера чанка на
    # основе количества доступной ОЗУ.
    pass
else:
    max_chunk_size = 0.01 * (1024 ** 3)

def open_utf8(path: Path, mode: str):
    return open(path, mode, newline='', encoding='utf-8')

def start() -> int:
    # Шаг 1: РАЗДЕЛЕНИЕ. Разделяем внешние данные на чанки и сортируем каждый в
    # отдельности.
    try:
        with open_utf8(config.data_path, 'r') \
                as data_file:
            reader = csv.reader(data_file)
            file_chunks_amount = 0
            chunk = []
            current_size = 0
            
            # Записать заголовок CSV файла, а за одним ещё и
            # truncate-нуть его за счёт режима 'w'.
            with open_utf8(config.sorted_data_path, 'w') as sorted_data_file:
                writer = csv.writer(sorted_data_file)
                writer.writerow(next(reader))
                
            for row in reader:
                chunk.append(row)
                current_size += sys.getsizeof(row)
                if current_size >= max_chunk_size:
                    chunk_path : Path = Path((f'temp/chunk{file_chunks_amount}'
                                               '.csv'))
                    chunk = sorted(chunk, key=lambda row: row[1], reverse=True)
                    # Убедиться, что папка существует.
                    chunk_path.parent.mkdir(parents=True, exist_ok=True)
                    with open_utf8(chunk_path, 'w+') \
                            as chunk_file:
                        writer = csv.writer(chunk_file)
                        writer.writerows(chunk)
                    chunk = []
                    current_size = 0
                    file_chunks_amount += 1
                    log.log(f'Создан чанк: {file_chunks_amount}.')
    except FileNotFoundError:
        log.error(('Файл для сортировки не найден. Используйте '
                   '\033[92mcsv_generator\033[0m.'))
        return 2
        
    # Шаг 2: СЛИЯНИЕ. Открываем несколько чанков за раз и записываем первый
    # хороший вариант.
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
                cur_line = chunk.readline()
                if cur_line == '':
                    # Убираем объекты из списка, когда они заканчиваются
                    chunks_file_objects.remove(chunk)
                else:
                    first_lines.append(cur_line)
            first_lines = sorted(first_lines, key=lambda row: row[1])
            if first_lines != []:
                open_utf8(config.sorted_data_path, 'a').write(first_lines[0])

    # Удаляем чанки так как они больше не нужны.
    for chunk_num in range(file_chunks_amount):
        chunk_path = Path(f'temp/chunk{chunk_num}.csv')
        chunk_path.unlink(missing_ok = True)
        log.log(f'Удалён файл {str(chunk_path)}.')

    return 1

if __name__ == '__main__':
    print('\033[92mexternal_sort.py\033[0m')
