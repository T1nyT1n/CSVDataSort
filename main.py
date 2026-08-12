import external_sort as ext_sort

def main() -> None:
    
    print("""\033[91m
            ┳━┓┓ ┃┏┓┓┳━┓┳━┓┏┓┓┳━┓┳    ┓━┓┏━┓┳━┓┏┓┓
            ┣━ ┏╋┛ ┃ ┣━ ┃┳┛┃┃┃┃━┫┃    ┗━┓┃ ┃┃┳┛ ┃
            ┻━┛┇ ┗ ┇ ┻━┛┇┗┛┇┗┛┛ ┇┇━┛  ━━┛┛━┛┇┗┛ ┇
          \033[0m""")
    print('Посетите страницу с репозиторием на GitHub, чтобы узнать больше: ' \
        '\033[93mhttps://github.com/T1nyT1n/CSVDataSort/\033[0m')
    
    ext_sort.start()
    
if __name__ == '__main__':
    main()
