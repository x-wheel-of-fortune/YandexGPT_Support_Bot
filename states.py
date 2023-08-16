from aiogram.fsm.state import StatesGroup, State


class Gen(StatesGroup):
    waiting_for_question = State()
    waiting_for_damaged_photo = State()
    waiting_for_expired_photo = State()
    waiting_for_wrong_order_description = State()
    waiting_for_other_question = State()
    order_problem = {
       2: waiting_for_damaged_photo,
       3: waiting_for_expired_photo,
       4: waiting_for_wrong_order_description,
       0: waiting_for_other_question,
    }
