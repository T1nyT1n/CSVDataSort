import sys
import config as c
import external_sort as ext_sort
import logger as log
import argparse as arg
import ctypes as ct
from pathlib import Path

def main() -> None:
    if sys.platform == "win32":
        lib_path = "./external_sort.dll"
    else:
        lib_path = "./external_sort.so"
    
    # Command line arguments
    parser = arg.ArgumentParser(
            description=('Implementation of external sorting in Python and C++'
                         ' with Tkinter GUI.'),
    )
    parser.add_argument(
            '-v',
            '--version',
            action='version',
            version='CSV Data Sort 0.1',
    )
    parser.add_argument(
            '-c',
            '--cli',
            action='store_true',
    )
    parser.add_argument(
            '-m',
            '--module',
            default='py',
            choices=['py', 'cpp'],
    )
    parser.add_argument(
            '-k',
            '--key',
            type=str,
    )
    parser.add_argument(
            '-f',
            '--file',
            type=str,
            default='data.csv',
    )
    parser.add_argument(
            '-o',
            '--output',
            type=str,
            default='sorted_data.csv',
    )
    args_list = parser.parse_args()

    if args_list.cli:
        
        print("""\033[91m
        ┳━┓┓ ┃┏┓┓┳━┓┳━┓┏┓┓┳━┓┳    ┓━┓┏━┓┳━┓┏┓┓
        ┣━ ┏╋┛ ┃ ┣━ ┃┳┛┃┃┃┃━┫┃    ┗━┓┃ ┃┃┳┛ ┃
        ┻━┛┇ ┗ ┇ ┻━┛┇┗┛┇┗┛┛ ┇┇━┛  ━━┛┛━┛┇┗┛ ┇
              \033[0m""")
        print(('Посетите страницу с репозиторием на GitHub, чтобы узнать'
            ' больше: \033[93mhttps://github.com/T1nyT1n/CSVDataSort/\033[0m'))
        
        if args_list.key:
            if args_list.module == 'cpp':
                lib = ct.CDLL(lib_path)
                lib.start.argtypes = [ 
                    ct.c_char_p, ct.c_size_t,
                    ct.c_char_p, ct.c_size_t,
                    ct.c_char_p, ct.c_size_t,
                ]
                lib.start.restype = ct.c_int
                key_bytes = args_list.key.encode('utf-8')
                file_bytes = args_list.file.encode('utf-8')
                output_bytes = args_list.output.encode('utf-8')
                lib.start(
                    key_bytes, len(key_bytes),
                    file_bytes, len(file_bytes),
                    output_bytes, len(output_bytes),
                )
            elif args_list.module == 'py':
                data_path = Path(args_list.file)
                sorted_path = Path(args_list.output)
                ext_sort.start(args_list.key, data_path, sorted_path)
            else:
                log.error((f'Используемый модуль для сортировки не указан.'
                          'Используйте --module.'))
        else:
            log.error((f'Ключ для сортировки не передан. Используйте --key,'
                        ' чтобы передать ключ для сортировки.'))
        
    else:
        log.error(f'Режима интерфейса ещё не реализован. Используйте --cli.')
    
if __name__ == '__main__':
    main()
