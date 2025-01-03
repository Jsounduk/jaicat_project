# utils/file_handling.py

import os

def read_file(file_path):
    """Reads the content of a text file and returns it as a string."""
    if not os.path.isfile(file_path):
        return "File does not exist."
    
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_to_file(file_path, content):
    """Writes content to a text file. If the file exists, it overwrites it."""
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    return "Content written successfully."

def file_exists(file_path):
    """Checks if a file exists."""
    return os.path.isfile(file_path)

def get_file_extension(file_path):
    """Returns the file extension for a given file path."""
    return os.path.splitext(file_path)[1]

def list_files_in_directory(directory_path):
    """Returns a list of files in the specified directory."""
    if not os.path.isdir(directory_path):
        return "Directory does not exist."
    
    return os.listdir(directory_path)
