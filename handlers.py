import os

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram import flags
from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
import utils
from states import Gen
from pathlib import Path
import kb
import text
import config

bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
router = Router()

@router.message(Command("start"))
async def start_handler(msg: Message, state: FSMContext):
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)
    #await state.set_state(Gen.text_response)

# #@router.message()
# async def menu(msg: Message):
#     problem_type = utils.classify(msg.text)
#     #await msg.answer(text.menu, reply_markup=kb.menu)

@router.callback_query(F.data == "text_response")
async def input_text_prompt(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.text_response)
    await clbck.message.answer(text.gen_text)


@router.callback_query(F.data == "audio_response")
async def input_text_prompt(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.audio_response)
    await clbck.message.answer(text.gen_text)


@router.message(Gen.text_response)
@flags.chat_action("typing")
async def text_response(msg: Message, state: FSMContext):
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
    mesg = await msg.answer(text.gen_wait)
    res = await utils.generate_classified_response(prompt)
    if not res or not res[0]:
        return await mesg.edit_text(text.gen_error, reply_markup=kb.iexit_kb)
    await mesg.edit_text(res[0] + text.text_watermark, disable_web_page_preview=True)


@router.message(Gen.audio_response)
@flags.chat_action("typing")
async def audio_response(msg: Message, state: FSMContext):
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
    mesg = await msg.answer(text.gen_wait)
    res = await utils.generate_classified_response(prompt)
    if not res:
        return await mesg.edit_text(text.gen_error, reply_markup=kb.iexit_kb)
    out_filename = await utils.tts(res[0])
    # Отправка голосового сообщения
    path = Path("", out_filename)
    voice = FSInputFile(path)
    await bot.send_voice(msg.from_user.id, voice)

    os.remove(out_filename)  # Удаление временного файла