# Custom Exceptions
class InvalidTokenException(Exception):
    """Токен не передан, попробуйте позже"""

    pass

class EmptyHistoryException(Exception):
    """⚠️ История пуста! Нет ни одного заказа."""
    
    pass
class TariffNotExistException(Exception):
    """💰 Тариф не найден"""
    
    pass

class CustomerAlreadyExistsException(Exception):
    """👤 Пользователь уже существует"""

    pass

class AlreadyLoggedException(Exception):
    """👤 Пользователь уже авторизован в системе."""

    pass
class InvalidRoleException(Exception):
    """❌ Недопустимая роль! Доступны только 'user' или 'admin'."""
    
    pass

class UserNotExistsException(Exception):
    """
    Пользователя не существует. Попробуйте заново.
    """
    
    pass

class IncorrectPasswordException(Exception):
    """
    Неверный пароль. Попробуйте заново.
    """
    
    pass

class InvalidPasswordException(Exception):
    """
    🔒 Пароль не соответствует требованиям безопасности!

    Чтобы защитить твою учётную запись, пароль должен содержать:
    • минимум 8 символов
    • хотя бы одну заглавную букву (A–Z)
    • хотя бы одну строчную букву (a–z)
    • хотя бы одну цифру (0–9)

    Попробуй ещё раз — у тебя всё получится! 💪
    """
    
    pass

class IncorrectAgreementException(Exception):
    """
    ❗ Ой, кажется, номер договора введён неправильно!
    Он должен выглядеть так:
    <b>Префикс</b> (IM, SZ, KU, ИМ, СЗ или КУ), потом дефис,
    затем <b>три буквы</b> (любые), <b>одна цифра</b>, дефис,
    и в конце — <b>от 1 до 3 цифр</b>.
    <b>Например: KU-ABC7-123</b>
    Попробуй ещё раз, я уверен, у тебя получится! 😊
    """
    
    pass

class IncorrectPhoneException(Exception):
    """
    📱 Упс! Номер телефона введён неверно. 
    Пожалуйста, введи номер в формате: <b>8XXXXXXXXXX</b>, 
    где 8 — первая цифра, а дальше — 10 цифр.
    <b>Например: 79513053036</b>
    Попробуй ещё раз — всё получится! 😊
    """
    
    pass

class IncorrectInsuranceException(Exception):
    """
    💰 Неверный ввод суммы страховки!
    Пожалуйста, введи только число, начиная с 0 и больше.
    Без знаков, пробелов и букв — просто цифры.
    <b>Например: 0 или 1500 или 99999</b>
    Попробуй ещё раз, всё получится! 😊
    """
    
    pass

class IncorrectTinNumberException(Exception):
    """
    🧾 Неверный ИНН!
    Пожалуйста, введи только цифры — от 10 до 15 символов.
    Без пробелов, букв и знаков — только числа.
    <b>Например: 1234567890 или 123456789012345</b>
    Проверь ещё раз и попробуй снова, у тебя точно получится! 🚀
    """
    
    pass

class IncorrectFileNameException(Exception):
    """
    📎 Неверное имя файла!
    Название файла должно строго соответствовать формату:
    <b>ГородОтправления-ГородПолучателя-НомерНакладной</b>

    ❌ Примеры неправильных названий:
    - document.pdf
    - moscow_dankov_123.pdf
    - Чаплыгин-Данков.pdf

    ✅ Пример правильного названия:
    <b>Чаплыгин-Данков-10133345678.pdf</b>

    Переименуй файл и попробуй снова — всё получится! 💪
    """
    
    pass

class RequestErrorException(Exception):
    """❌ Сервер временно недоступен, попробуйте позже"""

    pass