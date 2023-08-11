from aiogram.fsm.state import StatesGroup, State


class Gen(StatesGroup):
    text_response = State()
    audio_response = State()
