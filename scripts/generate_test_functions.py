import os
from pathlib import Path

def get_test_values(directory):
    files = sorted(Path(directory).glob("*.wav"))
    values = []
    for f in files:
        # Extract value from filename like "a_freq_0.0547.wav"
        parts = f.stem.split('_')
        value = parts[-1]
        values.append(value)
    return values

def generate_tests(param_name, test_class, values):
    tests = []
    for value in values:
        safe_value = value.replace('.', '_')
        test_code = f'''
#[test]
fn test_{param_name}_{safe_value}() {{
    let test = {test_class} {{
        name: "{param_name}_{value}",
        config_file: "{param_name}_{value}.ron",
        reference_file: "{param_name}_{value}.wav",
        duration: 7.24,
    }};
    test.run().expect("{param_name}={value} 测试失败");
}}'''
        tests.append(test_code)
    return '\n'.join(tests)

# Generate tests for a_freq
a_freq_values = get_test_values('temps/a_freq')
a_freq_tests = generate_tests('a_freq', 'AFreqTestCase', a_freq_values)

# Generate tests for b_form
b_form_values = get_test_values('temps/b_form')
b_form_tests = generate_tests('b_form', 'BFormTestCase', b_form_values)

# Generate tests for b_freq
b_freq_values = get_test_values('temps/b_freq')
b_freq_tests = generate_tests('b_freq', 'BFreqTestCase', b_freq_values)

# Write to file
with open('test_functions_to_add.txt', 'w') as f:
    f.write("// a_freq tests\n")
    f.write(a_freq_tests)
    f.write("\n\n// b_form tests\n")
    f.write(b_form_tests)
    f.write("\n\n// b_freq tests\n")
    f.write(b_freq_tests)

print(f"Generated {len(a_freq_values)} a_freq tests")
print(f"Generated {len(b_form_values)} b_form tests")
print(f"Generated {len(b_freq_values)} b_freq tests")
print("Total:", len(a_freq_values) + len(b_form_values) + len(b_freq_values))
