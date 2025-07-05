import re

# Path to your feature file
feature_file_path = 'test_scenarios.feature'
# Path to the output step definitions file
step_definitions_path = 'test_steps.py'

# Read feature file
with open(feature_file_path, 'r', encoding='utf-8') as file:
    feature_content = file.read()

# Regular expression to match Given, When, Then, And steps
step_pattern = re.compile(r'^\s*(Given|When|Then|And)\s+(.+)', re.MULTILINE)

# Track unique step texts to avoid duplicates
unique_steps = set()

# Prepare list to store step definitions
step_definitions = []

# Map step keywords to decorators
keyword_to_decorator = {
    'Given': '@given',
    'When': '@when',
    'Then': '@then',
    'And': '',  # Will inherit from previous step type
}

last_decorator = ''

# Process each matched step
for match in step_pattern.finditer(feature_content):
    keyword, step_text = match.groups()
    step_text_clean = step_text.strip()

    if step_text_clean not in unique_steps:
        unique_steps.add(step_text_clean)

        if keyword != 'And':
            last_decorator = keyword_to_decorator[keyword]

        # Use triple quotes if single quote detected in step text
        if "'" in step_text_clean:
            step_string = f'"""{step_text_clean}"""'
        else:
            step_string = f"'{step_text_clean}'"

        # Create step definition block
        step_definitions.append(f"{last_decorator}({step_string})\ndef step_impl(context):\n    pass\n")

# Write to step definitions file
with open(step_definitions_path, 'w', encoding='utf-8') as file:
    file.write('from behave import given, when, then\n\n')
    file.write('\n\n'.join(step_definitions))

print(f"✅ Step definitions generated in {step_definitions_path}")
