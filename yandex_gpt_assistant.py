import requests


class YandexGPTAssistant:
    def __init__(self, api_key, folder_id):
        self.api_key = api_key
        self.folder_id = folder_id
        self.instruct_url = "https://llm.api.cloud.yandex.net/llm/v1alpha/instruct"
        self.chat_url = "https://llm.api.cloud.yandex.net/llm/v1alpha/chat"
        self.headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "x-folder-id": self.folder_id,
            "Content-Type": "application/json"
        }

    def generate_response(
            self,
            user_question: str,
            instruction_text: str,
            temperature: float = 0.3,
    ):
        prompt_data = {
            "model": "general",
            "generationOptions": {
                "partialResults": False,
                "temperature": temperature,
                "maxTokens": "2000"
            },
            "instructionText": instruction_text,
            "requestText": user_question
        }
        print(f"Sending request to YandexGPT: {prompt_data}")
        response = requests.post(self.instruct_url, headers=self.headers, json=prompt_data)

        if response.status_code == 200:
            result = response.json()["result"]["alternatives"][0]["text"]
            num_tokens = response.json()["result"]["alternatives"][0]["num_tokens"]
            return result, num_tokens
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(response.text)
            return None, None

    def generate_response_with_memory(
            self,
            user_question: str,
            instruction_text: str,
            temperature: float = 0.3,
            prev_messages: [{str: str}] = [],
    ):
        prompt_data = {
            "model": "general",
            "generationOptions": {
                "partialResults": False,
                "temperature": temperature,
                "maxTokens": "500"
            },
            "messages": prev_messages,
            "instructionText": instruction_text,
        }
        print(f"Sending request to YandexGPT: {prompt_data}")
        response = requests.post(self.chat_url, headers=self.headers,
                                 json=prompt_data)

        if response.status_code == 200:
            result = response.json()["result"]["alternatives"][0]["text"]
            num_tokens = response.json()["result"]["alternatives"][0][
                "num_tokens"]
            return result, num_tokens
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(response.text)
            return None, None
