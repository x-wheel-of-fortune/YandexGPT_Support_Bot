import time
import database_queries

from resources.yaml_resource import load_yaml_resource
from yandex_gpt_assistant import YandexGPTAssistant
from yandex_speech_kit import YandexSpeechKit


instructions = load_yaml_resource('resources/instructions.yaml')
cfg = load_yaml_resource('resources/config.yaml')


assistant = YandexGPTAssistant(cfg["GPT_API_KEY"], cfg["FOLDER_ID"])
speech = YandexSpeechKit(cfg['SPEECH_KIT_API_KEY'])


async def classify(
        user_question,
        instruction_text=instructions["classification_prompt"],
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
        instruction_text=instructions["base"],
        temperature=0.1,
):
    return assistant.generate_response(
        user_question, instruction_text, temperature)


async def generate_classified_response(user_question, user_id):
    problem_type = await classify(user_question)
    print("Категория вопроса:", problem_type)
    instruction = instructions["base"] + instructions["database"] + str(
        database_queries.get_by_id(user_id)) + instructions["problem"][problem_type]["base"]
    res = None
    while not res or not res[0]:
        res = await generate_response(user_question, instruction)
        if not res or not res[0]:
            time.sleep(1)
    return res, problem_type
