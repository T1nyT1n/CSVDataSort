import csv
import sys # Для аргументов командной строки
import pathlib # Для выбора пути
import re
import random
import time
from itertools import cycle

# КОНФИГ

FILE_SIZE = 0.1 * (1024 ** 3)
TEXT_UPDATE_INTERVAL = 0.5 # секунд
SPINNER = cycle([ "-", "\\", "|", "/"])

PLACES_FILE = "gen/places.csv"
CONDITIONS_FILE = "gen/conditions.csv"
MIN_TEMP = -45.0
MAX_TEMP = 40.0
MIN_HUMIDITY = 0.0
MAX_HUMIDITY = 1.0
MIN_FIRE_RISK_TEMP = 27.0
MIN_TIMESTAMP = 0
MAX_TIMESTAMP = 31104000

def exit_on_wrong_usage():
    print("""Использование: python3 csv_generator.py <аргумент>
Аргументы:
    --path "путь/к/файлу.csv" — путь к создаваемому файлу. 
    """)
    sys.exit(1)

def path_from_args():
    if len(sys.argv) < 2: # Если нет аргументов командной строки — ничего не
        exit_on_wrong_usage() # заработает.
    x = re.search("--path", sys.argv[1])
    if x:
        file_path = pathlib.Path(sys.argv[2])
    else:
        exit_on_wrong_usage()
    return file_path

def main(file_path):
    with open(PLACES_FILE, 'r', newline='', encoding='utf-8') as val_file:
        reader = csv.reader(val_file)
        places = [row[0] for row in reader]
        
    with open(CONDITIONS_FILE, 'r', newline='', encoding='utf-8') as cond_file:
        reader = csv.DictReader(cond_file)
        conditions = []
        for row in reader:
            conditions.append({
                'condition': row['Condition'],
                'min_temp': int(row['MinTemp']),
                'max_temp': int(row['MaxTemp'])
            })
    
    with open(file_path, "w", newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([
            "Places",
            "Temperature",
            "Humidity",
            "FireRisk",
            "Condition",
            "Timestamp"
        ])
        last_update = time.monotonic()
        prev_len = 0
        while csv_file.tell() < FILE_SIZE:
            # Температура
            temp = round(random.uniform(MIN_TEMP, MAX_TEMP), 2)
            # Риск огня
            if temp >= MIN_FIRE_RISK_TEMP:
                fire_risk = bool(random.getrandbits(1))
            else:
                fire_risk = False
            # Состояние
            candidates = []
            for cond in conditions:
                if int(cond['min_temp']) <= temp <= int(cond['max_temp']):
                    candidates.append(cond['condition'])
            # Записать в файл.
            writer.writerow([
                random.choice(places), # Место
                temp,
                # Влажность
                round(random.uniform(MIN_HUMIDITY, MAX_HUMIDITY), 2),
                fire_risk,
                random.choice(candidates), # Состояние
                random.randint(MIN_TIMESTAMP, MAX_TIMESTAMP) # Timestamp
            ])
            
            now = time.monotonic()
            if __name__ == '__main__' and now - \
                last_update >= TEXT_UPDATE_INTERVAL:
                text = next(SPINNER) + " " + str(round(csv_file.tell() / \
                    (1024 ** 2), 1)) + " МБ"
                print(f'\r{text:<{prev_len}}', end='', flush=True)
                last_update = now
            
    print()

if __name__ == "__main__":    
    main(path_from_args())