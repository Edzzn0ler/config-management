import toml
import sys


def toml_to_custom(input_data, output_file):
    try:
        # Парсинг TOML
        data = toml.loads(input_data)
        output_lines = []
        constants = {}

        # Преобразование в учебный конфигурационный язык
        def process_item(key, value, indent=0):
            indent_space = '    ' * indent
            key = key.lower()  # Приведение ключа к нижнему регистру
            if isinstance(value, dict):
                output_lines.append(f"{indent_space}{{")
                for k, v in value.items():
                    output_lines.append(f"{indent_space}    {k.lower()} : {process_value(v)},")
                output_lines.append(f"{indent_space}}}")
            else:
                output_lines.append(f"{indent_space}const {key} = {process_value(value)};")

        def process_value(value):
            if isinstance(value, str):
                # Обработка выражений
                if value.startswith('.') and value.endswith('.'):
                    expression = value[1:-1].strip()  # Убираем точки
                    try:
                        # Замена переменных из constants в выражении
                        for const_key, const_value in constants.items():
                            expression = expression.replace(const_key, str(const_value))
                        # Разрешённые функции и операции
                        allowed_names = {"abs": abs}
                        result = eval(expression, {"__builtins__": None}, allowed_names)
                        return result  # Возвращается число
                    except Exception as e:
                        raise ValueError(f"Invalid expression: {value}. Error: {e}")
                # Если это обычная строка, вернуть как 'строка'
                return f"'{value}'"
            elif isinstance(value, (int, float)):
                # Числовое значение возвращается как есть
                return value
            else:
                raise ValueError(f"Unsupported value type: {type(value)}")

        # Сохраняем константы для использования в выражениях
        for key, value in data.items():
            if isinstance(value, (int, float, str)):
                constants[key.lower()] = value

        # Преобразуем TOML в целевой формат
        for key, value in data.items():
            if isinstance(value, dict):
                process_item(key, value)
            else:
                process_item(key, value)

        # Запись в выходной файл
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(map(str, output_lines)))
        print(f"Conversion complete. Output saved to {output_file}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 config_converter.py <output_file>")
    else:
        output_file = sys.argv[1]
        input_data = sys.stdin.read()
        toml_to_custom(input_data, output_file)
