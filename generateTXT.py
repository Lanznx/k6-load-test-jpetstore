import random
import string

def generate_random_string(length=100):
    letters = string.ascii_letters + string.digits + ' '
    return ''.join(random.choice(letters) for _ in range(length))

def create_large_text_file(file_path, target_size, line_length=100):
    with open(file_path, 'w', encoding='utf-8') as file:
        total_bytes = 0
        while total_bytes < target_size:
            line = generate_random_string(line_length)
            file.write(line + '\n')
            total_bytes += len(line.encode('utf-8')) + 1  # 加1是因为换行符

if __name__ == "__main__":
    create_large_text_file('32MB.txt', 32*1024*1024)
    create_large_text_file('128MB.txt', 128*1024*1024)
    create_large_text_file('512MB.txt', 512*1024*1024)
