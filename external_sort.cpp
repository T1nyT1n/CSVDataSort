#include <iostream>
#include <fstream>
#include <ostream>
#include <sstream>
#include <string>
#if defined (_WIN32)
    #include <windows.h> // Russian language for console output on Windows.
#endif

#define DEFAULT_MAX_CHUNK_SIZE 10737419

/// LOGGING FUNCTIONS

void log(std::string text) {
    std::cout << ("\033[96m[LOG]\033[0m " + text) << std::endl;
    return;
}

void debug(std::string text) {
    std::cout << ("\033[90m[DEBUG]\033[0m " + text) << std::endl;
    return;
}

void success(std::string text) {
    std::cout << ("\033[92m[SUCCESS]\033[0m " + text) << std::endl;
    return;
}

void error(std::string text) {
    std::cerr << ("\033[91m[ERROR]\033[0m " + text) << std::endl;
    return;
}

/// ACTUAL PROGRAM (finally)

int get_sorting_key_num(std::string header_line, std::string key_str) {
    unsigned char num = 0;
    std::stringstream header(header_line);
    std::string token;
    while (std::getline(header, token, ',')) { // Split the string by a delimiter ",".
        if (token == key_str) {
            return num;
        }
        num += 1;
    }
    throw "Столбец для сортировки не найден. Проверьте, что вы правильно написали название столбца.";
}

extern "C" int start( // We have to use const char* and it's size to correctly pass arguments from Python.
    const char* char_key,
    size_t key_len,
    const char* char_data_file_path,
    size_t data_file_path_len,
    const char* char_sorted_file_path,
    size_t sorted_file_path_len
    // Yep, it takes this much text to pass THREE STRINGS. That's ridiculous.
) {
    #if defined (_WIN32)
        SetConsoleOutputCP(CP_UTF8); // Russian language for console output on Windows.
    #endif

    // Oh yeah, we also have to turn them into the actual C++ strings now.
    std::string key(char_key, key_len);
    std::string data_file_path(char_data_file_path, data_file_path_len);
    std::string sorted_file_path(char_sorted_file_path, sorted_file_path_len);

    std::string line; // Current line of the file.
    
    // Create file objects.
    std::ifstream data_file(data_file_path);
    std::ofstream sorted_data_file(sorted_file_path, std::fstream::trunc);
    
    // Check if file is opened correctly.
    if (!data_file.is_open()) {
        error("Файл для сортировки не найден. Используйте \033[92mcsv_generator\033[0m.");
        return 1;
    }

    // Get header and write it to sorted file.
    std::getline(data_file, line);
    sorted_data_file << line << std::endl;
    log("Заголовок CSV файла записан в итоговый файл.");

    // Step 0: get the sorting key.
    int key_num;
    try {
        key_num = get_sorting_key_num(line, key);
        log("Получен индекс столбца таблицы.");
    } catch(std::string error_message) {
        error(error_message);
        return 1;
    }
    std::getline(data_file, line);
    log("Прочитана первая строка данных.");
    std::stringstream example_row_str(line);
    std::string token;
    for (int i = 0; i <= key_num; i++) {
        std::getline(example_row_str, token, ',');
    }
    try {
        std::stoi(token);
    } catch(...) {
        error("Это не int.");
    }
    try {
        std::stof(token);
    } catch(...) {
        error("Это не float.");
    }
    try {
        std::stod(token);
    } catch(...) {
        error("Это не double.");
    }

    // Close the files.
    data_file.close();
    sorted_data_file.close();
    
    return 0; // Everything's good. Everything's okay. No need to worry.
}
