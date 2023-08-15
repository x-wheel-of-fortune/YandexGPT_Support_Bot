import os
import yaml
import utils
import datetime
from aiogram import F, Router, types, Bot, Dispatcher, flags
from aiogram.filters import Command, Text, StateFilter
from aiogram.types import Message, FSInputFile
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
from states import Gen
from pathlib import Path
import keyboard


with open('resources/instructions.yaml', encoding="utf8") as file:
    instructions = yaml.safe_load(file)
with open('config.yaml', encoding="utf8") as file:
    cfg = yaml.safe_load(file)
with open('resources/const_answers.yaml', encoding="utf8") as file:
    const_answers = yaml.safe_load(file)

bot = Bot(token=cfg["BOT_TOKEN"], parse_mode=ParseMode.HTML)
router = Router()
SESSION_TIMEOUT = datetime.timedelta(minutes=30)

user_last_interaction = {}


@router.message(Command("start"))
@router.message(StateFilter(None))
async def start_handler(msg: Message, state: FSMContext):
    await msg.answer(const_answers["greet"].format(name=msg.from_user.full_name))
    user_id = 7 #msg.from_user.id
    await state.set_state(Gen.waiting_for_question)
    user_last_interaction[user_id] = datetime.datetime.now()


@router.callback_query(F.data == "text_response")
async def input_text_prompt(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.text_response)
    await clbck.message.answer(const_answers["gen_text"], reply_markup=keyboard.exit_kb)


@router.callback_query(F.data == "audio_response")
async def input_text_prompt(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.audio_response)
    await clbck.message.answer(const_answers["gen_text"], reply_markup=keyboard.exit_kb)


@router.message(Text(const_answers["case_completed"]))
async def input_text_prompt(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    await clbck.answer(const_answers["end_session_text"])


@router.message(Gen.waiting_for_question)
@flags.chat_action("typing")
async def response(msg: Message, state: FSMContext):
    user_id = 7 #msg.from_user.id
    if user_id not in user_last_interaction or (datetime.datetime.now() - user_last_interaction[user_id]) >= SESSION_TIMEOUT:
        print("previous session ran out")
        await start_handler(msg, state)
    else:
        if msg.content_type == types.ContentType.VOICE:
            file_id = msg.voice.file_id
            file = await bot.get_file(file_id)
            file_path = file.file_path
            file_on_disk = Path("", f"{file_id}.tmp")
            await bot.download_file(file_path, destination=file_on_disk)
            prompt = await utils.stt(file_on_disk)
            print(prompt)
            os.remove(file_on_disk)  # Удаление временного файла
        else:
            prompt = msg.text
        mesg = await msg.answer(const_answers["gen_wait"])
        print(await order_wrong_cut(msg, state))
        res, problem_type = await utils.generate_classified_response(prompt, user_id)
        if not res or not res[0]:
            return await mesg.edit_text(const_answers["gen_error"])
        if msg.content_type == types.ContentType.VOICE:
            out_filename = await utils.speech.text_to_speech(res[0])
            # Отправка голосового сообщения
            path = Path("", out_filename)
            voice = FSInputFile(path)
            await bot.send_voice(msg.from_user.id, voice)

            os.remove(out_filename)  # Удаление временного файла
            await state.set_state(Gen.order_problem[problem_type])
            user_id = msg.from_user.id
            user_last_interaction[user_id] = datetime.datetime.now()
        else:
            await mesg.edit_text(res[0], disable_web_page_preview=True)
            #await state.set_state(Gen.order_problem[problem_type])
            user_last_interaction[user_id] = datetime.datetime.now()


async def other_problems(msg: Message, state: FSMContext):
    instruction = instructions["problem"][0]["extend"]
    # тправляет вопрос пользователя в службу поддержки
    print(msg.text) #вопрос пользователя
    support_response = input()
    # Бот отправляет ответ службы поддержки пользователю


async def order_late(msg: Message, state: FSMContext):
    instruction = instructions["problem"][1]["extend"]
    print("Вы задерживаетесь с доставкой заказа. Вы привезете заказ?")
    delivery_response = input("Да/Нет")
    #     обработать ответ с помощью джпт и отправить клиенту ответ


async def order_damaged(msg: Message, state: FSMContext):
    instruction = instructions["problem"][2]["extend"]
    photo = msg.photo
    print("Данный товар считается поврежденным?")
    support_response = input("Да/Нет")
    #     обработать ответ с помощью джпт и отправить клиенту ответ
    # отправляет клиенту купон


async def order_wrong_cut(msg: Message, state: FSMContext):
    instruction = instructions["problem"][3]["extend"]
    user_question = msg.text + "Молоко 3 , Мёд 1"
    res = await utils.generate_response(user_question, instruction)
    return res