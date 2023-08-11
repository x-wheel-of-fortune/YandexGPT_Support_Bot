import utils
import asyncio

base_instruction = """
Ты - агент службы поддержки сервиса Яндекс Лавка.Ты 
должен вежливо отвечать на вопросы клиентов и успокаивать их, поднимать им 
настроение, обязательно учитывая специфику их проблемы. Тебе нельзя просить клиента 
обратиться в службу поддержки, придумай решение для возникшей проблемы сам.\n Возникла 
следующая проблема: """

classification_prompt = """
В нашей системе существует 4 категории проблем к 
которым относятся сообщения пользователя с соответствующими им цифрами:
1 - Заказ опаздывает 
2 - Товар в заказе повреждён
3 - У продукта в заказе истёк срок годности
4 - Полученные товары не соответствуют товарам заказа
Ты получишь сообщение пользователя и будешь должен отнести его к одному из 
классов, и вывести только соответствующую ему цифру. Если сообщение не 
относится ни к одной из категорий или вопрос тебе непонятен, выведи 0. 
"""

problem_instructions = {
    0: "Клиент обратился со специфичной проблемой, скажи ему что сейчас "
       "позовёшь службу поддержки.",
    1: "Наш курьер опаздывает с доставкой товара клиенту.",
    2: "Товар пришёл клиенту повреждённым.",
    3: "У продукта в заказе истёк срок годности.",
    4: "Полученные клиентом товары не соответствуют товарам в его заказе.",
}

user_text = "MarkGor?"

temperature = 0.3

###########################################################################################

assistant = utils.assistant

async def classify_gorbenko(user_question, instruction_text =
classification_prompt, temperature=0.01):
    s = assistant.generate_response(user_question, instruction_text,
                                        temperature)[0]
    if not s or not s.isdigit() or int(s) > 4 or int(s) < 0:
        s = 0
    return int(s)

async def generate_classified_response_gorbenko(user_question):
    problem_type = await classify_gorbenko(user_question)
    instruction = base_instruction + problem_instructions[problem_type]
    return await utils.generate_response(user_question, instruction, temperature)

if __name__ == "__main__":
    async def getans():
        ans = await generate_classified_response_gorbenko(user_text)
        print(f"\nYandexGPT:\n\n{ans[0]}")
    asyncio.run(getans())