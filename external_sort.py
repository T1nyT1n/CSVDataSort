import csv
import sys

MAX_CHUNK_SIZE = 0.01 * (1024 ** 3)

def start():
    with open('data.csv', 'r', newline='', encoding='utf-8') as data_file:
        reader = csv.reader(data_file)
        file_chunks_amount = 0
        chunk = []
        current_size = 0
        for row in reader:
            chunk.append(row)
            current_size += sys.getsizeof(row)
            if current_size >= MAX_CHUNK_SIZE:
                with open(f'temp/chunk{file_chunks_amount}.csv', 'w', \
                    newline='', encoding='utf-8') as chunk_file:
                    writer = csv.writer(chunk_file)
                    writer.writerows(chunk)
                chunk = []
                current_size = 0
                file_chunks_amount += 1

if __name__ == '__main__':
    print('Заметьте, \033[33mэтот модуль не предназначен для самостоятельного' \
        ' запуска\033[0m. Используйте main.py для запуска программы. Запускаю' \
        ' main.py автоматически и завершаю работу...\n')
    import runpy
    runpy.run_module('main', run_name='__main__')