import asyncio
import logging
import random
import os
from typing import Dict, Optional, List, Tuple
from enum import Enum
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    FSInputFile, InputMediaPhoto
)
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Вставьте ваш токен от BotFather
BOT_TOKEN = "8513872943:AAElYh_UqJkLVjKO28sAZ6xnyOQLMJMi8Ug"

# Путь к папке с изображениями
IMAGES_DIR = Path("hangman_images")

# Проверяем существование папки с изображениями
if not IMAGES_DIR.exists():
    logger.error(f"Папка с изображениями '{IMAGES_DIR}' не найдена!")
    logger.info("Пожалуйста, создайте папку 'hangman_images' и добавьте в неё файлы:")
    logger.info("1.png - пустая виселица")
    logger.info("2.png - первая ошибка (голова)")
    logger.info("3.png - вторая ошибка (тело)")
    logger.info("4.png - третья ошибка (левая рука)")
    logger.info("5.png - четвертая ошибка (правая рука)")
    logger.info("6.png - пятая ошибка (левая нога)")
    logger.info("7.png - шестая ошибка (правая нога, человек повешен)")
    IMAGES_DIR.mkdir(exist_ok=True)

# Слова для игры и их переводы на русский
WORDS_WITH_TRANSLATIONS: List[Tuple[str, str]] = [
    ("python", "Питон (язык программирования)"),
    ("programming", "Программирование"),
    ("computer", "Компьютер"),
    ("algorithm", "Алгоритм"),
    ("database", "База данных"),
    ("function", "Функция"),
    ("variable", "Переменная"),
    ("string", "Строка"),
    ("integer", "Целое число"),
    ("boolean", "Логический тип"),
    ("list", "Список"),
    ("dictionary", "Словарь"),
    ("tuple", "Кортеж"),
    ("module", "Модуль"),
    ("package", "Пакет"),
    ("library", "Библиотека"),
    ("framework", "Фреймворк"),
    ("developer", "Разработчик"),
    ("software", "Программное обеспечение"),
    ("hardware", "Аппаратное обеспечение"),
    ("network", "Сеть"),
    ("internet", "Интернет"),
    ("browser", "Браузер"),
    ("keyboard", "Клавиатура"),
    ("monitor", "Монитор"),
    ("printer", "Принтер"),
    ("scanner", "Сканер"),
    ("mouse", "Мышь"),
    ("speaker", "Колонка"),
    ("microphone", "Микрофон"),
    ("code", "Код"),
    ("debug", "Отладка"),
    ("compile", "Компиляция"),
    ("execute", "Выполнение"),
    ("server", "Сервер"),
    ("client", "Клиент"),
    ("website", "Веб-сайт"),
    ("application", "Приложение"),
    ("mobile", "Мобильный"),
    ("desktop", "Настольный компьютер"),
    ("laptop", "Ноутбук"),
    ("tablet", "Планшет"),
    ("router", "Маршрутизатор"),
    ("firewall", "Фаервол"),
    ("encryption", "Шифрование"),
    ("password", "Пароль"),
    ("username", "Имя пользователя"),
    ("email", "Электронная почта"),
    ("cloud", "Облако"),
    ("storage", "Хранилище"),
    ("memory", "Память"),
    ("processor", "Процессор"),
    ("graphics", "Графика"),
    ("display", "Дисплей"),
    ("touchscreen", "Сенсорный экран"),
    ("keyboard", "Клавиатура"),
    ("mouse", "Мышь"),
    ("webcam", "Веб-камера"),
    ("headphones", "Наушники"),
    ("microphone", "Микрофон"),
    ("speaker", "Колонка"),
    ("printer", "Принтер"),
    ("scanner", "Сканер"),
    ("monitor", "Монитор"),
    ("projector", "Проектор"),
    ("cable", "Кабель"),
    ("wireless", "Беспроводной"),
    ("bluetooth", "Блютуз"),
    ("wifi", "Wi-Fi"),
    ("ethernet", "Ethernet"),
    ("usb", "USB"),
    ("hdmi", "HDMI"),
    ("javascript", "JavaScript"),
    ("html", "HTML"),
    ("css", "CSS"),
    ("java", "Java"),
    ("csharp", "C#"),
    ("php", "PHP"),
    ("ruby", "Ruby"),
    ("go", "Go"),
    ("rust", "Rust"),
    ("kotlin", "Kotlin"),
    ("swift", "Swift"),
    ("typescript", "TypeScript"),
    ("sql", "SQL"),
    ("nosql", "NoSQL"),
    ("api", "API"),
    ("rest", "REST"),
    ("graphql", "GraphQL"),
    ("docker", "Docker"),
    ("kubernetes", "Kubernetes"),
    ("git", "Git"),
    ("github", "GitHub"),
    ("agile", "Гибкая методология"),
    ("scrum", "Scrum"),
    ("kanban", "Канбан"),
    ("devops", "DevOps"),
    ("backend", "Бэкенд"),
    ("frontend", "Фронтенд"),
    ("fullstack", "Фуллстек"),
    ("ui", "Пользовательский интерфейс"),
    ("ux", "Пользовательский опыт"),
    ("responsive", "Адаптивный дизайн"),
    ("accessibility", "Доступность"),
    ("performance", "Производительность"),
    ("security", "Безопасность"),
    ("testing", "Тестирование"),
    ("automation", "Автоматизация"),
    ("machinelearning", "Машинное обучение"),
    ("ai", "Искусственный интеллект"),
    ("datascience", "Наука о данных"),
    ("bigdata", "Большие данные"),
    ("blockchain", "Блокчейн"),
    ("cryptocurrency", "Криптовалюта"),
    ("metaverse", "Метавселенная"),
    ("ar", "Дополненная реальность"),
    ("vr", "Виртуальная реальность"),
    ("iot", "Интернет вещей"),
    ("smartphone", "Смартфон"),
    ("tablet", "Планшет"),
    ("wearable", "Носимая электроника"),
    ("smartwatch", "Умные часы"),
    ("fitness", "Фитнес-трекер"),
    ("gaming", "Игровая консоль"),
    ("console", "Игровая приставка"),
    ("controller", "Геймпад"),
    ("keyboard", "Клавиатура"),
    ("mouse", "Мышь"),
    ("monitor", "Монитор"),
    ("headset", "Гарнитура"),
    ("microphone", "Микрофон"),
    ("webcam", "Веб-камера"),
]


# Состояния FSM
class GameState(StatesGroup):
    playing = State()


class HangmanGame:
    def __init__(self, word: str, translation: str):
        self.word = word.lower()
        self.translation = translation
        self.guessed_letters = set()
        self.wrong_guesses = 0
        self.max_wrong = 6  # 6 ошибок (от 1 до 7 изображений)
        self.current_image = 1  # Начинаем с пустой виселицы (1.png)
        self.last_message_id = None  # ID последнего сообщения с изображением

    def get_display_word(self) -> str:
        """Возвращает слово с отгаданными буквами и пропусками"""
        return ' '.join(
            letter if letter in self.guessed_letters else '_'
            for letter in self.word
        )

    def guess_letter(self, letter: str) -> bool:
        """Пробует угадать букву, возвращает True если буква есть в слове"""
        letter = letter.lower()

        # Если буква уже угадывалась, возвращаем False
        if letter in self.guessed_letters:
            return False

        self.guessed_letters.add(letter)

        if letter in self.word:
            return True
        else:
            self.wrong_guesses += 1
            # Обновляем изображение: 1 + wrong_guesses (т.к. 1.png - пустая виселица)
            self.current_image = min(1 + self.wrong_guesses, 7)
            return False

    def is_won(self) -> bool:
        """Проверяет, выиграна ли игра"""
        return all(letter in self.guessed_letters for letter in self.word)

    def is_lost(self) -> bool:
        """Проверяет, проиграна ли игра"""
        return self.wrong_guesses >= self.max_wrong

    def get_image_path(self) -> str:
        """Возвращает путь к текущему изображению"""
        # Убедимся, что номер изображения в пределах допустимого (от 1 до 7)
        image_num = max(1, min(self.current_image, 7))
        return IMAGES_DIR / f"{image_num}.png"

    def get_status_text(self) -> str:
        """Возвращает текстовый статус игры"""
        word_display = self.get_display_word()
        wrong_letters = [
            l for l in self.guessed_letters
            if l not in self.word and l.isalpha()
        ]

        status = f"<b>Слово:</b> {word_display}\n"
        status += f"<b>Ошибок:</b> {self.wrong_guesses}/{self.max_wrong}\n"

        if wrong_letters:
            status += f"<b>Неправильные буквы:</b> {', '.join(sorted(wrong_letters))}\n"

        return status


# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Хранение ID последних сообщений с изображениями
game_messages: Dict[int, int] = {}


# Создание клавиатуры с буквами
def create_letter_keyboard(guessed_letters: set = None) -> InlineKeyboardMarkup:
    """Создает inline клавиатуру с буквами алфавита"""
    if guessed_letters is None:
        guessed_letters = set()

    letters = "abcdefghijklmnopqrstuvwxyz"
    keyboard = []
    row = []

    for letter in letters:
        # Если буква уже угадывалась, делаем её неактивной
        if letter in guessed_letters:
            row.append(
                InlineKeyboardButton(
                    text=f"❌ {letter.upper()}",
                    callback_data=f"already_guessed"
                )
            )
        else:
            row.append(
                InlineKeyboardButton(
                    text=letter.upper(),
                    callback_data=f"letter:{letter}"
                )
            )

        # Разбиваем на строки по 7 букв
        if len(row) == 7:
            keyboard.append(row)
            row = []

    if row:  # Добавляем последнюю строку если она не пустая
        keyboard.append(row)

    # Добавляем кнопки управления игрой
    keyboard.append([
        InlineKeyboardButton(text="🔄 Новая игра", callback_data="new_game"),
        InlineKeyboardButton(text="🚪 Выйти", callback_data="quit_game"),
        InlineKeyboardButton(text="📖 Помощь", callback_data="help")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Клавиатура для главного меню
def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру главного меню"""
    keyboard = [
        [
            InlineKeyboardButton(text="🎮 Начать игру", callback_data="new_game"),
            InlineKeyboardButton(text="📖 Как играть", callback_data="how_to_play")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Отправка изображения виселицы
async def send_hangman_image(chat_id: int, game: HangmanGame, caption: str = "",
                             reply_markup: Optional[InlineKeyboardMarkup] = None,
                             edit_message: bool = False, message_id: Optional[int] = None):
    """Отправляет или редактирует сообщение с изображением виселицы"""

    # Получаем путь к изображению
    image_path = game.get_image_path()

    # Проверяем существование файла
    if not image_path.exists():
        logger.error(f"Изображение не найдено: {image_path}")
        # Отправляем текстовое сообщение об ошибке
        if not edit_message:
            message = await bot.send_message(
                chat_id,
                f"⚠️ Изображение виселицы не найдено.\n\n{caption}",
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            return message.message_id
        else:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"⚠️ Изображение виселицы не найдено.\n\n{caption}",
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            return message_id

    try:
        # Создаем объект файла для отправки
        photo = FSInputFile(image_path)

        if edit_message and message_id:
            try:
                # Редактируем существующее сообщение с фото
                await bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    media=InputMediaPhoto(media=photo, caption=caption, parse_mode='HTML')
                )
                if reply_markup:
                    await bot.edit_message_reply_markup(
                        chat_id=chat_id,
                        message_id=message_id,
                        reply_markup=reply_markup
                    )
                return message_id
            except Exception as edit_error:
                # Если не удалось отредактировать, отправляем новое сообщение
                logger.warning(f"Не удалось отредактировать сообщение: {edit_error}")
                # Удаляем старое сообщение
                try:
                    await bot.delete_message(chat_id, message_id)
                except:
                    pass
                # Отправляем новое
                message = await bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=caption,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
                return message.message_id
        else:
            # Отправляем новое фото
            message = await bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=caption,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            return message.message_id

    except Exception as e:
        logger.error(f"Ошибка при отправке изображения: {e}")
        # Отправляем текстовое сообщение как запасной вариант
        if not edit_message:
            message = await bot.send_message(
                chat_id,
                caption,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            return message.message_id
        else:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=caption,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            return message_id


# Команда /start
@dp.message(CommandStart())
async def command_start(message: Message):
    """Обработчик команды /start"""
    welcome_text = (
        "🎯 <b>Добро пожаловать в игру 'Виселица'!</b>\n\n"
        "Я загадаю английское слово из мира технологий и программирования, "
        "а тебе нужно будет угадать его по буквам, прежде чем человечек будет повешен!\n\n"
        "Нажми кнопку ниже, чтобы начать новую игру!"
    )

    await message.answer(
        welcome_text,
        reply_markup=main_menu_keyboard(),
        parse_mode='HTML'
    )


# Команда /help
@dp.message(Command("help"))
async def command_help(message: Message):
    """Обработчик команды /help"""
    help_text = (
        "🤖 <b>Команды бота:</b>\n\n"
        "/start - Запустить бота и показать главное меню\n"
        "/newgame - Начать новую игру\n"
        "/help - Показать эту справку\n\n"
        "🎮 <b>Как играть:</b>\n"
        "Нажми 'Начать игру', чтобы начать. Используй кнопки с буквами для угадывания. "
        "У тебя есть 6 неправильных попыток, прежде чем человечек будет повешен!\n\n"
        "<i>Все слова на английском языке связаны с технологиями и программированием.</i>"
    )

    keyboard = [[InlineKeyboardButton(text="🎮 Начать игру", callback_data="new_game")]]

    await message.answer(
        help_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode='HTML'
    )


# Команда /newgame
@dp.message(Command("newgame"))
async def command_newgame(message: Message, state: FSMContext):
    """Обработчик команды /newgame"""
    await start_new_game(message, state)


# Начало новой игры
@dp.callback_query(F.data == "new_game")
async def process_new_game(callback: CallbackQuery, state: FSMContext):
    """Обработчик нажатия на кнопку начала игры"""
    await callback.answer()
    await start_new_game(callback.message, state, callback.from_user.id)


async def start_new_game(message_source, state: FSMContext, user_id: int = None):
    """Запускает новую игру"""
    if user_id is None:
        user_id = message_source.from_user.id

    # Выбираем случайное слово и его перевод
    word, translation = random.choice(WORDS_WITH_TRANSLATIONS)
    game = HangmanGame(word, translation)

    # Сохраняем игру в состоянии
    await state.update_data(game=game)
    await state.set_state(GameState.playing)

    # Создаем клавиатуру с буквами
    keyboard = create_letter_keyboard()

    # Текст для подписи к изображению
    caption = (
        f"🎮 <b>Новая игра началась!</b>\n\n"
        f"Угадай английское слово, связанное с технологиями или программированием.\n\n"
        f"{game.get_status_text()}\n"
        f"<i>Выбери букву:</i>"
    )

    # Определяем, откуда пришел запрос
    if isinstance(message_source, Message):
        chat_id = message_source.chat.id
        # Удаляем предыдущее сообщение с изображением, если есть
        if user_id in game_messages:
            try:
                await bot.delete_message(chat_id, game_messages[user_id])
            except:
                pass

        # Отправляем новое изображение
        message_id = await send_hangman_image(chat_id, game, caption, keyboard)
        if message_id:
            game_messages[user_id] = message_id
            game.last_message_id = message_id

    else:  # CallbackQuery
        chat_id = message_source.chat.id
        # Удаляем старое изображение, если есть
        if user_id in game_messages:
            try:
                await bot.delete_message(chat_id, game_messages[user_id])
            except:
                pass

        # Отправляем новое изображение
        message_id = await send_hangman_image(chat_id, game, caption, keyboard)
        if message_id:
            game_messages[user_id] = message_id
            game.last_message_id = message_id


# Как играть
@dp.callback_query(F.data == "how_to_play")
async def process_how_to_play(callback: CallbackQuery):
    """Показывает инструкцию как играть"""
    await callback.answer()

    instructions = (
        "🎮 <b>Как играть в 'Виселицу'</b>\n\n"
        "1. Я загадываю случайное английское слово\n"
        "2. Ты видишь пропуски для каждой буквы\n"
        "3. Угадывай буквы по одной с помощью кнопок\n"
        "4. Правильные буквы открываются в слове\n"
        "5. Неправильные буквы добавляют части к виселице\n"
        "6. Ты выигрываешь, если угадаешь слово до того, как человечек будет полностью повешен!\n\n"
        "💡 <b>Советы:</b>\n"
        "• Начни с частых гласных: A, E, I, O, U\n"
        "• Затем попробуй частые согласные: T, N, S, R, L\n"
        "• Все слова из категории: <i>Технологии и программирование</i>\n\n"
        "<b>Готов играть?</b>"
    )

    keyboard = [[InlineKeyboardButton(text="🎮 Начать игру", callback_data="new_game")]]

    await callback.message.edit_text(
        instructions,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode='HTML'
    )


# Обработка угадывания буквы
@dp.callback_query(F.data.startswith("letter:"), GameState.playing)
async def process_letter_guess(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает нажатие на букву"""
    await callback.answer()

    # Получаем букву из callback_data
    letter = callback.data.split(":")[1]

    # Получаем данные из состояния
    data = await state.get_data()
    game: HangmanGame = data.get("game")

    if not game:
        await callback.answer("Игра не найдена. Начни новую!", show_alert=True)
        return

    # Пробуем угадать букву
    is_correct = game.guess_letter(letter)

    # Сохраняем обновленную игру
    await state.update_data(game=game)

    # Проверяем статус игры
    if game.is_won():
        # Текст для сообщения о победе
        caption = (
            f"🎉 <b>Поздравляю! Ты выиграл(а)!</b>\n\n"
            f"{game.get_status_text()}\n"
            f"<b>Слово было:</b> {game.word.upper()}\n"
            f"<b>Перевод:</b> {game.translation}\n\n"
            f"🏆 Ты угадал(а) слово с {game.wrong_guesses} ошибкой(ами)!"
        )

        keyboard = [[InlineKeyboardButton(text="🔄 Играть снова", callback_data="new_game")]]

        # Обновляем изображение
        message_id = await send_hangman_image(
            callback.message.chat.id,
            game,
            caption,
            InlineKeyboardMarkup(inline_keyboard=keyboard),
            edit_message=True,
            message_id=game_messages.get(callback.from_user.id)
        )

        if message_id:
            game_messages[callback.from_user.id] = message_id

        await state.clear()
        return

    elif game.is_lost():
        # Текст для сообщения о поражении
        caption = (
            f"💀 <b>Игра окончена! Ты проиграл(а)!</b>\n\n"
            f"{game.get_status_text()}\n"
            f"<b>Слово было:</b> {game.word.upper()}\n"
            f"<b>Перевод:</b> {game.translation}\n\n"
            f"Попробуй еще раз!"
        )

        keyboard = [[InlineKeyboardButton(text="🔄 Попробовать снова", callback_data="new_game")]]

        # Обновляем изображение (последнее состояние - 7.png)
        message_id = await send_hangman_image(
            callback.message.chat.id,
            game,
            caption,
            InlineKeyboardMarkup(inline_keyboard=keyboard),
            edit_message=True,
            message_id=game_messages.get(callback.from_user.id)
        )

        if message_id:
            game_messages[callback.from_user.id] = message_id

        await state.clear()
        return

    else:
        # Игра продолжается
        # Добавляем сообщение о результате
        if is_correct:
            result_msg = f"✅ Буква '{letter.upper()}' есть в слове!"
        else:
            result_msg = f"❌ Буквы '{letter.upper()}' нет в слове!"

        caption = (
            f"{result_msg}\n\n"
            f"{game.get_status_text()}\n"
            f"<i>Выбери следующую букву:</i>"
        )

        # Обновляем клавиатуру (отключаем угаданные буквы)
        keyboard = create_letter_keyboard(game.guessed_letters)

        # Обновляем изображение
        message_id = await send_hangman_image(
            callback.message.chat.id,
            game,
            caption,
            keyboard,
            edit_message=True,
            message_id=game_messages.get(callback.from_user.id)
        )

        if message_id:
            game_messages[callback.from_user.id] = message_id


# Обработка уже угаданных букв
@dp.callback_query(F.data == "already_guessed")
async def process_already_guessed(callback: CallbackQuery):
    """Обрабатывает нажатие на уже угаданную букву"""
    await callback.answer("Ты уже угадывал(а) эту букву!", show_alert=True)


# Выход из игры
@dp.callback_query(F.data == "quit_game")
async def process_quit_game(callback: CallbackQuery, state: FSMContext):
    """Выход из текущей игры"""
    await callback.answer()

    # Получаем данные из состояния
    data = await state.get_data()
    game: HangmanGame = data.get("game")

    # Удаляем изображение игры
    user_id = callback.from_user.id
    if user_id in game_messages:
        try:
            await bot.delete_message(callback.message.chat.id, game_messages[user_id])
            del game_messages[user_id]
        except:
            pass

    if game:
        message_text = (
            f"Игра отменена.\n\n"
            f"<b>Слово было:</b> {game.word.upper()}\n"
            f"<b>Перевод:</b> {game.translation}\n\n"
            f"Начни новую игру, когда будешь готов(а)!"
        )
    else:
        message_text = "Нет активной игры для выхода."

    await state.clear()

    keyboard = [[InlineKeyboardButton(text="🎮 Начать новую игру", callback_data="new_game")]]

    await callback.message.answer(
        message_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode='HTML'
    )


# Обработка кнопки помощи из игры
@dp.callback_query(F.data == "help")
async def process_help_from_game(callback: CallbackQuery, state: FSMContext):
    """Показывает справку во время игры"""
    await callback.answer()

    # Сохраняем текущее состояние игры
    data = await state.get_data()
    game = data.get("game")

    help_text = (
        "🎮 <b>Как играть</b>\n\n"
        "Угадай английское слово по буквам с помощью кнопок.\n"
        "У тебя есть максимум 6 неправильных попыток.\n"
        "Слово связано с технологиями или программированием.\n\n"
        "<i>Нажми 'Вернуться в игру', чтобы продолжить.</i>"
    )

    keyboard = [
        [InlineKeyboardButton(text="↩️ Вернуться в игру", callback_data="back_to_game")],
        [InlineKeyboardButton(text="🚪 Выйти из игры", callback_data="quit_game")]
    ]

    # Сохраняем игру в callback_data для возврата
    if game:
        # Сохраняем ключевые данные игры
        game_data = {
            'word': game.word,
            'translation': game.translation,
            'guessed_letters': list(game.guessed_letters),
            'wrong_guesses': game.wrong_guesses,
            'current_image': game.current_image,
            'last_message_id': game.last_message_id
        }
        await state.update_data(saved_game=game_data)

    await callback.message.answer(
        help_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode='HTML'
    )


# Возврат к игре из помощи
@dp.callback_query(F.data == "back_to_game")
async def process_back_to_game(callback: CallbackQuery, state: FSMContext):
    """Возвращает к игре из меню помощи"""
    await callback.answer()

    # Восстанавливаем игру
    data = await state.get_data()
    saved_game = data.get('saved_game')

    if saved_game:
        # Создаем новую игру с сохраненными данными
        game = HangmanGame(saved_game['word'], saved_game['translation'])
        game.guessed_letters = set(saved_game['guessed_letters'])
        game.wrong_guesses = saved_game['wrong_guesses']
        game.current_image = saved_game['current_image']
        game.last_message_id = saved_game['last_message_id']

        await state.update_data(game=game)
        await state.set_state(GameState.playing)

        # Удаляем сообщение со справкой
        try:
            await callback.message.delete()
        except:
            pass

        # Показываем игру с сохраненным изображением
        caption = f"{game.get_status_text()}\n<i>Выбери букву:</i>"
        keyboard = create_letter_keyboard(game.guessed_letters)

        # Обновляем изображение
        message_id = await send_hangman_image(
            callback.message.chat.id,
            game,
            caption,
            keyboard,
            edit_message=True,
            message_id=game_messages.get(callback.from_user.id)
        )

        if message_id:
            game_messages[callback.from_user.id] = message_id
    else:
        # Если нет сохраненной игры, возвращаем в главное меню
        await callback.message.edit_text(
            "Не удалось восстановить игру. Начинаем новую...",
            reply_markup=main_menu_keyboard()
        )


# Команда /stats
@dp.message(Command("stats"))
async def command_stats(message: Message, state: FSMContext):
    """Показывает статистику"""
    data = await state.get_data()
    game: HangmanGame = data.get("game")

    if game:
        stats_text = (
            f"📊 <b>Текущая игра:</b>\n"
            f"Слово: {game.get_display_word()}\n"
            f"Ошибок: {game.wrong_guesses}/{game.max_wrong}\n"
            f"Угаданные буквы: {len(game.guessed_letters)}\n\n"
            f"Продолжай игру!"
        )
    else:
        stats_text = "У тебя нет активной игры. Начни новую с помощью /newgame"

    await message.answer(stats_text, parse_mode='HTML')


# Обработка других сообщений
@dp.message()
async def handle_other_messages(message: Message):
    """Обработчик всех остальных сообщений"""
    await message.answer(
        "Я понимаю только команды и нажатия на кнопки! 🤖\n\n"
        "Используй /start чтобы начать или /help для инструкций.",
        reply_markup=main_menu_keyboard()
    )


# Основная функция запуска бота
async def main():
    """Основная функция запуска бота"""
    print("Бот запускается...")
    print(f"Папка с изображениями: {IMAGES_DIR.absolute()}")

    # Проверяем наличие изображений
    for i in range(1, 8):  # Проверяем файлы от 1.png до 7.png
        image_path = IMAGES_DIR / f"{i}.png"
        if image_path.exists():
            print(f"✓ Найдено изображение: {image_path.name}")
        else:
            print(f"✗ Отсутствует изображение: {image_path.name}")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())