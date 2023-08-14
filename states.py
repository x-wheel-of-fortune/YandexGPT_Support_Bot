from aiogram.fsm.state import StatesGroup, State


class Gen(StatesGroup):
    waiting_for_question = State()
    order_late = State()
    order_damaged = State()
    order_expired = State()
    order_wrong = State()
    order_other_problem = State()
    order_problem = {
        0: order_other_problem,
        1: order_late,
        2: order_damaged,
        3: order_expired,
        4: order_wrong
    }
