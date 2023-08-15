import re
import utils
import asyncio
from database_queries import get_by_id

with open('resources/instructions.yaml', encoding="utf8") as file:
    instructions = yaml.safe_load(file)

user_text = "Мой заказ пришел с червяками!"

###########################################################################################
assistant = utils.assistant


def extract_number_from_string(input_string):
    # Ищем все числа в строке, даже если они встречаются внутри слов
    numbers = re.findall(r'\d+', input_string)

    # Если найдены числа, возвращаем первое из них
    if numbers:
        return int(numbers[0])

    # Если числа не найдены, возвращаем 0
    return 0

async def classify_gorbenko(
        user_question: str,
        instruction_text: str = instructions["classification_prompt"],
        temperature: float = 0.01,
):
    s = assistant.generate_response(user_question, instruction_text, temperature)[0]
    s = extract_number_from_string(s)
    if s > 5 or s < 0:
        s = 0
    return s


async def generate_classified_response_gorbenko(user_question, user_id):
    problem_type = await classify_gorbenko(user_question)
    print("Категория вопроса:", problem_type)
    instruction = instructions["base"] + instructions["database"] + str(get_by_id(user_id)) + instructions["problem"][problem_type]["base"]
    res = None
    while not res or not res[0]:
        res = await utils.generate_response(user_question, instruction)
    return res


if __name__ == '__main__':
    async def getans():
        ans = await generate_classified_response_gorbenko(user_text, user_id=7)
        print(f"\nYandexGPT:\n\n{ans[0]}")
    asyncio.run(getans())
