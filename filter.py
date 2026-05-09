def filter_proxies(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        filtered_proxies = []
        
        for line in lines:
            clean_line = line.strip()
            if not clean_line:
                continue
            
            lower_line = clean_line.lower()
            
            if 'socks' not in lower_line:
                filtered_proxies.append(clean_line)

        with open(output_file, 'w', encoding='utf-8') as f:
            for proxy in filtered_proxies:
                f.write(f"{proxy}\n")

        print(f"Фильтрация завершена, сохранено: {len(filtered_proxies)} -> {output_file}")

    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    filter_proxies('raw_proxies.txt', 'proxies.txt')