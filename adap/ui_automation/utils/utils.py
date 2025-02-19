import os
import random
import string


def convert_to_snake_case(text):
    # Convert to lowercase
    text = text.lower()
    # Replace spaces with underscores
    text = text.replace(" ", "_")
    return text


def generate_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def delete_csv_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"CSV file '{file_path}' has been deleted.")
    else:
        print(f"CSV file '{file_path}' does not exist.")
