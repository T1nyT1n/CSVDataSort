#include <iostream>
#include <fstream>
#include <ostream>
#include <string>
#include <windows.h>

#define DEFAULT_MAX_CHUNK_SIZE 10737419

extern "C" int start(
    const char* char_key,
    size_t key_len,
    const char* char_data_file_path,
    size_t data_file_path_len,
    const char* char_sorted_file_path,
    size_t sorted_file_path_len
) {
    SetConsoleOutputCP(CP_UTF8);
    
    std::string key(char_key, key_len);
    std::string data_file_path(char_data_file_path, data_file_path_len);
    std::string sorted_file_path(char_sorted_file_path, sorted_file_path_len);

    std::string line; // Current line of the file.
    
    // Create file objects.
    std::ifstream data_file(data_file_path);
    std::ofstream sorted_data_file(sorted_file_path);
    
    // Check if file is opened correctly.
    if (!data_file.is_open()) {
        std::cerr << "Файл для сортировки не найден. Используйте \033[92mcsv_generator\033[0m." << std::endl;
        return 1;
    }

    // Get header and write it to sorted file.
    std::getline(data_file, line);
    sorted_data_file << line << std::endl;

    data_file.close();
    sorted_data_file.close();
    
    return 0; // Everything's good. Everything's okay. No need to worry.
}
