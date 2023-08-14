import json
import requests
import time
from speechkit import Session, SpeechSynthesis, ShortAudioRecognition
import logging
from db import get_by_id
import config
import text


class GPTAssistant:
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
            prev_messages: [{str:str}] = [],
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


assistant = GPTAssistant(config.GPT_API_KEY, config.FOLDER_ID)


async def classify(
        user_question,
        instruction_text=text.classification_prompt,
        temperature=0.01,
):
    s = assistant.generate_response(
        user_question,
        instruction_text,
        temperature,
    )[0]

    if not s or not s.isdigit() or int(s) > 5 or int(s) < 0:
        s = 0

    return int(s)


async def generate_response(
        user_question,
        instruction_text=text.base_instruction,
        temperature=0.1,
):

    return assistant.generate_response(
        user_question, instruction_text, temperature)


async def generate_classified_response(user_question,user_id):
    problem_type = await classify(user_question)
    print("Категория вопроса:", problem_type)
    instruction = text.base_instruction + text.database_instruction + str(
        get_by_id(user_id)) + text.problem_instructions[problem_type]
    res = None
    while not res or not res[0]:
        res = await generate_response(user_question, instruction)
        if not res or not res[0]:
            time.sleep(1)
    return res, problem_type


class CSpeechKit:

    __APIKey = "AQVN1a6-ru21pyEZiU67SKUNbaxvuhaudG5IdOCT"
    __api_key_session = Session

    def __init__(self):
        self.__api_key_session = Session.from_api_key(
            self.__APIKey,
            x_client_request_id_header=True,
            x_data_logging_enabled=True,
        )

    def synthesize_audio(self, path, message_text, person_voice='oksana', file_format='oggopus', rate='16000'):
        synthesize_audio = SpeechSynthesis(self.__api_key_session)
        synthesize_audio.synthesize(path,
                                    text=message_text,
                                    voice=person_voice,
                                    format=file_format,
                                    sampleRateHertz=rate)

    def recognize_audio(self, file_path, file_format='oggopus', rate='16000'):
        recognize_short_audio = ShortAudioRecognition(self.__api_key_session)
        with open(file_path, "rb") as f:
            data = f.read()
        text = recognize_short_audio.recognize(data, format=file_format, sampleRateHertz=rate)
        return text


speech = CSpeechKit()


async def stt(audio_path):
    return speech.recognize_audio(audio_path)


async def tts(text):
    audio_path = "audio.ogg"
    speech.synthesize_audio(audio_path, text)
    return audio_path

# import asyncio
# if __name__ == "__main__":
#     async def getans():
#         ans = await generate_classified_response("Мне до сих пор не доаставили заказ!")
#         print(ans)
#     asyncio.run(getans())
