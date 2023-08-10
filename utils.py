import json
import requests

import logging
import config
import text

# Замените на ваши реальные значения
api_key = "AQVN31V_Z6wpxVSRe16YXfPitbS-XWB3VZv2pp8I"
folder_id = "b1g8hv628o86piqpqm02"

url = f"https://llm.api.cloud.yandex.net/llm/v1alpha/instruct"
headers = {
"Authorization": f"Api-Key {api_key}",
"x-folder-id": folder_id,
"Content-Type": "application/json"
}

async def generate_response(user_question):

        instruction_text = text.instruction
        request_text = user_question
        temperature = 0.3
        prompt_data = {
          "model": "general",
          "generationOptions": {
                "partialResults": False,
                "temperature": temperature,
                "maxTokens": "5000"
          },
          "instructionText": instruction_text,
          "requestText": request_text
        }
        response = requests.post(url, headers=headers, json=prompt_data)

        if response.status_code == 200:
            result = response.json()["result"]["alternatives"][0]["text"]
            num_tokens = response.json()["result"]["alternatives"][0]["num_tokens"]
            return result, num_tokens
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(response.text)

if __name__ == "__main__":
    print(generate_response("Мне до сих пор не доаставили заказ!"))