import toml
from io import StringIO
import sys


def toml_to_custom(input_data, output_file):
    try:
        data = toml.loads(input_data)
        output_lines = []
        constants = {}

        def process_item(key, value, indent=0):
            indent_space = '    ' * indent
            key = key.lower()
            if isinstance(value, dict):
                output_lines.append(f"{indent_space}const {key} = {{")
                for k, v in value.items():
                    output_lines.append(f"{indent_space}    {k.lower()} : {process_value(v)},")
                output_lines.append(f"{indent_space}}};")
            else:
                output_lines.append(f"{indent_space}const {key} = {process_value(value)};")

        def process_value(value):
            if isinstance(value, str):
                if value.startswith('.') and value.endswith('.'):
                    expression = value[1:-1].strip()
                    try:
                        for const_key, const_value in constants.items():
                            expression = expression.replace(const_key, str(const_value))
                        allowed_names = {"abs": abs}
                        result = eval(expression, {"__builtins__": None}, allowed_names)
                        return result
                    except Exception as e:
                        raise ValueError(f"Invalid expression: {value}. Error: {e}")  # Исключение выбрасывается здесь
                return f"'{value}'"
            elif isinstance(value, (int, float)):
                return value
            else:
                raise ValueError(f"Unsupported value type: {type(value)}")

        for key, value in data.items():
            if isinstance(value, (int, float, str)):
                constants[key.lower()] = value

        for key, value in data.items():
            if isinstance(value, dict):
                process_item(key, value)
            else:
                process_item(key, value)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(map(str, output_lines)))
        print(f"Conversion complete. Output saved to {output_file}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 config_converter.py <output_file>")
        sys.exit(1)  # Завершаем выполнение
    else:
        output_file = sys.argv[1]
        input_data = sys.stdin.read()
        toml_to_custom(input_data, output_file)
