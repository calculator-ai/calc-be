import google.generativeai as genai
import json
import re
from PIL import Image
from constants import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

def analyze_image(img: Image, dict_of_vars: dict):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    dict_of_vars_str = json.dumps(dict_of_vars, ensure_ascii=False)

    # 🔥 **Updated Prompt to Force Proper JSON**
    prompt = (
        f"You are a math AI. Extract and solve mathematical expressions from the image. "
        f"Strictly return only valid JSON in the following format:\n"
        f'{{"expressions": [{{"expr": "2+2", "result": "4", "assign": false}}]}}\n'
        f"- Use **double quotes (`\"`) instead of single quotes (`'`)**.\n"
        f"- Ensure that **booleans are lowercase (`true`/`false`)**.\n"
        f"- Ensure **numbers are returned as strings (`\"5\"` instead of `5`)**.\n"
        f"- **Do not include text explanations or markdown formatting.**\n"
        f"Use {dict_of_vars_str} to resolve variable values."
    )

    try:
        response = model.generate_content([prompt, img])
        response_text = response.text.strip()

        # print("🔹 Gemini Raw Response:", response_text)

        # ✅ **Fix Gemini’s Response Formatting**
        response_text = response_text.replace("'", '"')  # Fix single to double quotes
        response_text = response_text.replace("True", "true").replace("False", "false")  # Fix boolean values

        # ✅ **Extract JSON using Regex to Handle Unexpected Output**
        match = re.search(r'\{.*\}', response_text, re.DOTALL)  # Find first valid JSON block
        if match:
            response_text = match.group(0)

        # ✅ **Validate JSON Structure**
        if not response_text.startswith('{') or not response_text.endswith('}'):
            print("❌ Error: Gemini response is not valid JSON")
            return [{'expr': 'Error', 'result': 'Invalid JSON from Gemini', 'assign': False}]

        # ✅ **Parse JSON Safely**
        response_data = json.loads(response_text)

        # ✅ **Ensure response contains correct structure**
        if "expressions" in response_data and isinstance(response_data["expressions"], list):
            answers = response_data["expressions"]
        else:
            print("❌ Error: 'expressions' key not found in Gemini response")
            return [{'expr': 'Error', 'result': 'Invalid JSON structure from Gemini', 'assign': False}]

        print('✅ Returned Answer:', answers)

        # ✅ **Ensure 'assign' key exists in all responses**
        for answer in answers:
            answer['assign'] = answer.get('assign', False)  # Ensure assign key exists

        return answers

    except json.JSONDecodeError:
        print("❌ Error: Gemini returned invalid JSON format")
        return [{'expr': 'Error', 'result': 'Invalid JSON from Gemini', 'assign': False}]
    except Exception as e:
        print(f"❌ Error in analyzing image: {e}")
        return [{'expr': 'Error', 'result': str(e), 'assign': False}]
