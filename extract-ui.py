import json
import ollama

def generate_input_type_and_example(input_info):
    prompt = f"""
You will receive a list of form input fields, each with properties like placeholder, type, tag name, and role.

For each input field, provide a single numbered line with this format:

[number].[Input Description]: [Logical dummy example data]

- Use the placeholder, role, tag, or type to describe the input.
- Provide logical dummy data matching the input type.
- Do not add explanations, just give one line per input.
- Ignore buttons and links; only focus on inputs with roles like textbox, search, combobox, spinbutton, and similar.

Example:

1.Username: johndoe  
2.Password: Password123!

Here is the list of inputs:
{input_info}

"""

    response = ollama.generate(
        model="llama3.1",
        prompt=prompt,
        options={"temperature": 0}
    )
    print("OLLAMA full response:", response)  # debug
    return response.response.strip()

import json

def main():
    with open("ui-extracted.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # If data is a list, use the last element
    if isinstance(data, list):
        if len(data) == 0:
            print("No data found in ui-extracted.json")
            return
        data = data[-1]

    url = data.get("url", "unknown url")

    with open("filled_inputs.txt", "w", encoding="utf-8") as outfile:
        outfile.write(f"URL: {url}\n{'-'*40}\n")


        guess = generate_input_type_and_example(data)
        outfile.write(guess + "\n")

    print("✅ Results saved to filled_inputs.txt")

if __name__ == "__main__":
    main()

