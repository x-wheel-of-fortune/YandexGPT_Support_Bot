import datetime
import os
from pathlib import Path

from aiogram import Router, types, Bot, flags
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command, Text, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile
from aiogram.types.callback_query import CallbackQuery

import keyboard
import utils
from database_queries import get_by_id
from resources.yaml_resource import load_yaml_resource
from states import Gen

# Load resources and configuration
cfg = load_yaml_resource('resources/config.yaml')
instructions = load_yaml_resource('resources/instructions.yaml')
const_answers = load_yaml_resource('resources/const_answers.yaml')

bot = Bot(token=cfg["BOT_TOKEN"], parse_mode=ParseMode.HTML)
router = Router()
SESSION_TIMEOUT = datetime.timedelta(minutes=30)

user_last_interaction = {}


@router.message(Command("start"))
@router.message(StateFilter(None))
async def start_handler(msg: Message, state: FSMContext):
    await send_message(msg,
        const_answers["greet"].format(name=msg.from_user.full_name))
    user_id = 7  # msg.from_user.id
    await state.set_state(Gen.waiting_for_question)
    user_last_interaction[user_id] = datetime.datetime.now()


@router.message(Text(const_answers["case_completed"]))
async def input_text_prompt(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    await clbck.answer(const_answers["end_session_text"])


@router.message(Gen.waiting_for_question)
@flags.chat_action("typing")
async def response(msg: Message, state: FSMContext):
    user_id = 7  # msg.from_user.id
    if user_id not in user_last_interaction or (
            datetime.datetime.now() - user_last_interaction[
        user_id]) >= SESSION_TIMEOUT:
        print("previous session ran out")
        await start_handler(msg, state)
        return
    prompt = await receive_message(msg)
    await msg.answer(const_answers["gen_wait"])
    problem_type = await utils.classify(prompt)
    await SCENARIOS[problem_type](msg, state)


async def receive_message(message: Message):
    if message.content_type == types.ContentType.TEXT:  
        return message.text
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = f"{file_id}.tmp"
    await bot.download_file(file_path, destination=file_on_disk)
    prompt = await utils.speech.speech_to_text(file_on_disk)
    os.remove(file_on_disk)  # Удаление временного файла
    return prompt


async def send_message(msg: Message, res):
    user_id = msg.from_user.id
    if msg.content_type == types.ContentType.TEXT:
        await msg.answer(res, disable_web_page_preview=True)
    else:
        # голосовое сообщение
        await utils.speech.text_to_speech(res)
        out_filename = "audio.ogg"
        path = out_filename
        voice = FSInputFile(path)
        await bot.send_voice(msg.from_user.id, voice)
        os.remove(out_filename) 
    user_last_interaction[user_id] = datetime.datetime.now()


# Common function to handle responses
async def handle_response(msg: Message, state: FSMContext, instruction_key, next_state=None):
    instruction = instruction_key
    res = await utils.generate_response(await receive_message(msg), instruction)
    await send_message(msg,res[0])
    if next_state:
        await state.set_state(next_state)


async def other_problems(msg: Message, state: FSMContext):
    type = await utils.generate_response(await receive_message(msg), instructions["base"] + instructions["problem"][0][
        "classify"])
    if not type[0] or not type[0].isdigit() or int(type[0]) < 0 or int(
            type[0]) > 1:
        await handle_response(msg, state,
                              instructions["base"] + instructions["problem"][0]["not_support"],
                              Gen.waiting_for_question)
    else:
        await handle_response(msg, state,
                              instructions["base"] + instructions["problem"][0]["support"])


async def order_late(msg: Message, state: FSMContext):
    instruction_yes = instructions["base"] + instructions["problem"][1]["delivery_goes"] + \
                       instructions["database"] + str(get_by_id(USER_ID))
    instruction_no = instructions["base"] + instructions["problem"][1]["delivery_failed"] + \
                     instructions["database"] + str(get_by_id(USER_ID))
    print("Вы задерживаетесь с доставкой. Вы привезете заказ?")
    #delivery_response = input("Да/Нет ")
    delivery_response = utils.generate_support_answer()
    if delivery_response == "Да":
        await handle_response(msg, state, instruction_yes,
                              Gen.waiting_for_question)
        await send_message(msg,
            "\nВаш промокод на следующий заказ " + utils.generate_ticket())

    else:
        await handle_response(msg, state, instruction_no,
                              Gen.waiting_for_refund_method_damaged)
        await send_message(msg,"",
                         reply_markup=keyboard.choice_of_answer_order_damaged)


async def order_damaged(msg: Message, state: FSMContext):
    instruction = instructions["base"] + instructions["problem"][2]["base"] + \
                   instructions["database"] + str(get_by_id(USER_ID))
    await handle_response(msg, state, instruction,
                          Gen.waiting_for_damaged_photo)


@router.message(Gen.waiting_for_damaged_photo)
async def order_damaged_photo(msg: Message, state: FSMContext):
    await send_message(msg,const_answers["gen_wait"])
    photo = msg.photo
    # print("Данный товар считается поврежденным?")
    #support_response = input("Да/Нет ")
    support_response = utils.generate_support_answer()
    if support_response == "Да":
        instruction = instructions["base"] + instructions["problem"][2][
            "damaged"] + instructions["database"] + str(get_by_id(USER_ID))
        res = await utils.generate_response("", instruction_text=instruction)
        #    Вставить кнопки в клавиатуру пользователя при нажатии на
        #    которые отправится сообщение
        kb = keyboard.choice_of_answer_order_damaged
        await send_message(msg,res[0], reply_markup=kb)
        await state.set_state(Gen.waiting_for_refund_method_damaged)
    else:
        instruction = instructions["base"] + instructions["problem"][2][
            "not_damaged"] + instructions["database"] + str(get_by_id(USER_ID))
        res = await utils.generate_response("", instruction_text=instruction)
        await state.set_state(Gen.waiting_for_question)
        await send_message(msg,res[0])


@router.message(Gen.waiting_for_refund_method_damaged)
async def choosing_refund_method_damaged(msg: Message, state: FSMContext):
    await send_message(msg,const_answers["gen_wait"])
    ans = await receive_message(msg)
    res = ""
    if ans == "Товар":
        instruction = instructions["base"] + \
                       instructions["selected_answer_damaged"]["product"] + \
                      instructions[
                          "database"] + str(get_by_id(USER_ID))
        res = await utils.generate_response("", instruction_text=instruction)
        await state.set_state(Gen.waiting_for_question)
    elif ans == "Купон":
        instruction = instructions["base"] + \
                       instructions["selected_answer_damaged"]["coupon"] + \
                       instructions[
                          "database"] + str(get_by_id(USER_ID))
        res = await utils.generate_response("", instruction_text=instruction)
        res = (res[0] + "\nВаш промокод: " + utils.generate_ticket(), "")
        await state.set_state(Gen.waiting_for_question)
    elif ans == "Карта":
        instruction = instructions["base"] + \
                      instructions["selected_answer_damaged"]["card"] + \
                      instructions[
                          "database"] + str(get_by_id(USER_ID))
        res = await utils.generate_response("", instruction_text=instruction)
        await state.set_state(Gen.waiting_for_question)
    else:
        res = "Пожалуйста, повторите Ваш вопрос."
    await send_message(msg,res[0])


async def order_expired(msg: Message, state: FSMContext):
    instruction = instructions["base"] + instructions["problem"][3]["base"] + \
                   instructions["database"] + str(get_by_id(USER_ID))
    res = await utils.generate_response(await receive_message(msg), instruction)
    await send_message(msg,res[0])  # Отправка ответа пользователю
    await state.set_state(Gen.waiting_for_expired_photo)


@router.message(Gen.waiting_for_expired_photo)
async def order_expired_photo(msg: Message, state: FSMContext):
    await send_message(msg,const_answers["gen_wait"])
    photo = msg.photo
    print("Данный товар с истекшим сроком годности?")
    # support_response = input("Да/Нет ")
    support_response = utils.generate_support_answer()
    if support_response == "Да":
        instruction = instructions["base"] + instructions["problem"][3][
            "expired"]  + instructions["database"] + str(get_by_id(USER_ID))
        res = await utils.generate_response("", instruction_text=instruction)
    else:
        instruction = instructions["base"] + instructions["problem"][3][
            "not_expired"] + instructions["database"] + str(get_by_id(USER_ID))
        res = await utils.generate_response("", instruction_text=instruction)
    await send_message(msg,res[0])
    await state.set_state(Gen.waiting_for_question)

async def order_wrong(msg: Message, state: FSMContext):
    instruction = instructions["base"] + instructions["problem"][4]["support"]
    res = await utils.generate_response("", instruction)
    await send_message(msg,res[0])
    await state.set_state(Gen.waiting_for_question)


# global_constants
USER_ID = 7

SCENARIOS = {
    0: other_problems,
    1: order_late,
    2: order_damaged,
    3: order_expired,
    4: order_wrong,
}
