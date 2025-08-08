from aiogram.fsm.state import State, StatesGroup


class Merch(StatesGroup):
    """
    Состояние для получения мерча, после введения ИНН.

    Атрибуты:
        tin (State): Состояние для ввода ИНН.
    """
    tin = State()