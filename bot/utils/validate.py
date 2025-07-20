import re

from bot.utils.exceptions import IncorrectPhone, IncorrectInsurance, IncorrectAgreement

class InvoiceValidator:
    """
    Класс для валидации введённых данных.

    Методы класса проверяют:
        - номер договора (agreement),
        - номер телефона,
        - сумму страхования.

    Для валидации используются регулярные выражения.

    Исключения:
        При некорректных данных выбрасываются кастомные исключения:
        IncorrectAgreement, IncorrectPhone, IncorrectInsurance.
    """
    
    AGREEMENT_PATTERN = re.compile(r"^(IM|SZ|KU|ИМ|СЗ|КУ)-([A-Za-z]{3}|[А-Яа-я]{3})\d-\d{1,3}$")
    PHONE_NUMBER = re.compile(r"^7\d{10}$")
    INSURANCE_AMOUNT = re.compile(r"^\d+$")
    
    @classmethod
    async def correct_agreement_validator(cls, *, text: str) -> bool:
        """Проверяет совпадение номера договора с паттерном."""
        
        return bool(cls.AGREEMENT_PATTERN.fullmatch(text))
    
    @classmethod
    async def correct_phone_validator(cls, *, text: str) -> bool:
        """Проверяет совпадение номера телефона с паттерном."""
        
        return bool(cls.PHONE_NUMBER.fullmatch(text))
    
    @classmethod
    async def correct_insurance_validator(cls, *, text: str) -> bool:
        """Проверяет совпадение суммы страхования с паттерном."""
        
        return bool(cls.INSURANCE_AMOUNT.fullmatch(text))
    
    @classmethod
    async def correct_agreement(cls, *, text: str) -> bool:
        """
        Проверяет номер договора.
        Формат: префикс из IM|SZ|KU|ИМ|СЗ|КУ, дефис, три буквы (лат/кирилл), одна цифра, дефис, от 1 до 3 цифр.
        Пример: IM-ABC1-123
        """
        
        if not await cls.correct_agreement_validator(text=text):
            raise IncorrectAgreement(IncorrectAgreement.__doc__)
        
        return True

    @classmethod
    async def correct_phone(cls, *, text: str) -> bool:
        """
        Проверяет формат введенного номера телефона.
        
        Формат: 7ХХХХХХХХХХ
        
        Пример: 79042803001

        """
        
        if not await cls.correct_phone_validator(text=text):
            raise IncorrectPhone(IncorrectPhone.__doc__)
        
        return True
    
    @classmethod
    async def correct_insurance(cls, *, text: str) -> bool:
        """
        Проверяет формат ввода суммы страхования.
        
        Формат: Число от 0 и больше, без букв и пробелов.

        """
        
        if not await cls.correct_insurance_validator(text=text):
            raise IncorrectInsurance(IncorrectInsurance.__doc__)
        
        return True