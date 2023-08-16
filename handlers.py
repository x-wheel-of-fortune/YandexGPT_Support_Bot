import os
from pathlib import Path
import datetime

from aiogram import F, Router, types, Bot, flags
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command, Text, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile
from aiogram.types.callback_query import CallbackQuery

import keyboard
import utils
from resources.yaml_resource import load_yaml_resource
from states import Gen
from database_queries import get_by_id

# Load resources and configuration
cfg = load_yaml_resource('resources/config.yaml')
instructions = load_yaml_resource('resources/instructions.yaml')
const_answers = load_yaml_resource('resources/const_answers.yaml')

bot = Bot(token=cfg["BOT_TOKEN"], parse_mode=ParseMode.HTML)
router = Router()
SESSION_TIMEOUT = datetime.timedelta(minutes=30)

user_last_interaction = {}


#global_constants
USER_ID = 7

SCENARIOS = {
    0: other_problems,
    1: order_late,
    2: order_damaged,
    3: order_expired,
    4: order_wrong,
}



@router.message(Command("start"))
@router.message(StateFilter(None))
async def start_handler(msg: Message, state: FSMContext):
    await msg.answer(
        const_answers["greet"].format(name=msg.from_user.full_name))
    user_id = 7  # msg.from_user.id
    await state.set_state(Gen.waiting_for_question)
    user_last_interaction[user_id] = datetime.datetime.now()


@router.callback_query(F.data == "text_response")
async def input_text_prompt(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.text_response)
    await clbck.message.answer(const_answers["gen_text"],
                               reply_markup=keyboard.exit_kb)


@router.callback_query(F.data == "audio_response")
async def input_text_prompt(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.audio_response)
    await clbck.message.answer(const_answers["gen_text"],
                               reply_markup=keyboard.exit_kb)


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
    mesg = await msg.answer(const_answers["gen_wait"])
    # print(await order_wrong_cut(msg, state))
    problem_type = await utils.classify(prompt)
    await SCENARIOS[problem_type](msg, state)


async def receive_message(message: Message):
    if message.content_type == types.ContentType.TEXT:
        return message.text
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path("", f"{file_id}.tmp")
    await bot.download_file(file_path, destination=file_on_disk)
    prompt = await utils.speech.text_to_speech(file_on_disk)
    # print(prompt)
    os.remove(file_on_disk)  # Удаление временного файла
    return prompt


async def send_message(msg: Message, res, mesg, user_id):
    if msg.content_type == types.ContentType.TEXT:
        await mesg.edit_text(res[0], disable_web_page_preview=True)
    else:
        # голосовое сообщение
        out_filename = await utils.speech.text_to_speech(res[0])
        path = Path("", out_filename)
        voice = FSInputFile(path)
        await bot.send_voice(msg.from_user.id, voice)
        os.remove(out_filename)
        user_id = msg.from_user.id
    user_last_interaction[user_id] = datetime.datetime.now()


async def other_problems(msg: Message, state: FSMContext):
    instruction = instructions["problem"][0]["classify"]
    type = await utils.generate_response(msg.text, instruction)
    if not type[0] or not type[0].isdigit() or int(type[0]) < 0 or int(
            type[0]) > 1:
        prob = 0
    else:
        prob = 1
    if prob == 0:
        instruction = instructions["problem"][0]["not_support"]
        res = await utils.generate_response("", instruction)
        await msg.answer(res[0])
        await state.set_state(Gen.waiting_for_question)
    else:
        instruction = instructions["problem"][0]["support"]
        res = await utils.generate_response("", instruction)
        await msg.answer(res[0])
        # support_response = input()


async def order_late(msg: Message, state: FSMContext):
    user_question = msg.text
    instruction_yes = instructions["problem"][1]["delivery_goes"] + \
                      instructions["database"] + str(get_by_id(user_id))
    instruction_no = instructions["problem"][1]["delivery_failed"] + \
                     instructions["database"] + str(get_by_id(user_id))
    print("Вы задерживаетесь с доставкой. Вы привезете заказ?")
    delivery_response = input("Да/Нет ")
    # delivery_response = utils.generate_support_answer()
    if delivery_response == "Да":
        res = await utils.generate_response(user_question, instruction_yes)
        await msg.answer(res[
                             0] + "\nВаш промокод на следующий заказ " +
                         utils.generate_ticket())
        await state.set_state(Gen.waiting_for_question)

    else:
        res = await utils.generate_response(user_question, instruction_no)
        await msg.answer(res[0],
                         reply_markup=keyboard.choice_of_answer_order_damaged)
        await state.set_state(Gen.waiting_for_refund_method_damaged)


async def order_damaged(msg: Message, state: FSMContext):
    instruction = instructions["base"] + instructions["problem"][3]["base"] + \
                  instructions["database"] + str(get_by_id(user_id))
    res = await utils.generate_response(msg.text, instruction)
    await msg.answer(res[0])  # Отправка ответа пользователю
    await state.set_state(Gen.waiting_for_damaged_photo)


@router.message(Gen.waiting_for_damaged_photo)
async def order_damaged_photo(msg: Message, state: FSMContext):
    await msg.answer(const_answers["gen_wait"])
    photo = msg.photo
    # print("Данный товар считается поврежденным?")
    support_response = input("Да/Нет ")
    # support_response = utils.generate_support_answer()
    if support_response == "Да":
        instruction = instructions["base"] + instructions["problem"][2][
            "damaged"] + instructions["database"] + str(get_by_id(user_id))
        res = await utils.generate_response("", instruction_text=instruction)
        #    Вставить кнопки в клавиатуру пользователя при нажатии на
        #    которые отправится сообщение
        kb = keyboard.choice_of_answer_order_damaged
        await msg.answer(res[0], reply_markup=kb)
        await state.set_state(Gen.waiting_for_refund_method_damaged)
    else:
        instruction = instructions["base"] + instructions["problem"][2][
            "not_damaged"] + instructions["database"] + str(get_by_id(user_id))
        res = await utils.generate_response("", instruction_text=instruction)
        await state.set_state(Gen.waiting_for_other_question)
        await msg.answer(res[0])


@router.message(Gen.waiting_for_refund_method_damaged)
async def choosing_refund_method_damaged(msg: Message, state: FSMContext):
    await msg.answer(const_answers["gen_wait"])
    ans = msg.text
    res = ""
    if ans == "Товар":
        instruction = instructions["base"] + \
                      instructions["selected_answer_damaged"]["product"] + \
                      instructions[
                          "database"] + str(get_by_id(user_id))
        res = await utils.generate_response("", instruction_text=instruction)
    elif ans == "Купон":
        instruction = instructions["base"] + \
                      instructions["selected_answer_damaged"]["coupon"] + \
                      instructions[
                          "database"] + str(get_by_id(
            user_id)) + "Это купон для клиента, предоставь код купона " \
                        "клиенту" + utils.generate_ticket()
        res = await utils.generate_response("", instruction_text=instruction)
    elif ans == "Карта":
        instruction = instructions["base"] + \
                      instructions["selected_answer_damaged"]["card"] + \
                      instructions[
                          "database"] + str(get_by_id(user_id))
        res = await utils.generate_response("", instruction_text=instruction)
    else:
        res = "Пожалуйста, повторите Ваш вопрос."
    await msg.answer(res[0])


async def order_expired(msg: Message, state: FSMContext):
    instruction = instructions["base"] + instructions["problem"][3]["base"] + \
                  instructions["database"] + str(get_by_id(user_id))
    res = await utils.generate_response(msg.text, instruction)
    await msg.answer(res[0])  # Отправка ответа пользователю
    await state.set_state(Gen.waiting_for_expired_photo)


@router.message(Gen.waiting_for_expired_photo)
async def order_expired_photo(msg: Message, state: FSMContext):
    await msg.answer(const_answers["gen_wait"])
    photo = msg.photo
    print("Данный товар с истекшим сроком годности?")
    # support_response = input("Да/Нет ")
    support_response = utils.generate_support_answer()
    if support_response == "Да":
        instruction = instructions["base"] + instructions["problem"][3][
            "expired"] + instructions["database"] + str(get_by_id(user_id))
        res = await utils.generate_response("", instruction_text=instruction)
    else:
        instruction = instructions["base"] + instructions["problem"][3][
            "not_expired"] + instructions["database"] + str(get_by_id(user_id))
        res = await utils.generate_response("", instruction_text=instruction)
    await msg.answer(res[0])
    await state.set_state(Gen.waiting_for_other_question)


async def order_wrong(msg: Message, state: FSMContext):
    instruction = instructions["base"] + instructions["problem"][4]["support"]
    res = await utils.generate_response("", instruction)
    await msg.answer(res[0])