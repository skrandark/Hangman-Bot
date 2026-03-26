import asyncio
import logging
import random
import json
from typing import Dict, Optional, List, Tuple
from pathlib import Path
from datetime import datetime

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
SCORES_FILE = "player_scores.json"  # Файл для сохранения очков

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
    ("headset", "Гарнитура"),
    ("webcam", "Веб-камера"),
]


# Класс для управления очками игроков
class ScoreManager:
    def __init__(self, filename: str = SCORES_FILE):
        self.filename = filename
        self.scores = self.load_scores()

    def load_scores(self) -> Dict[int, dict]:
        """Загружает очки из файла"""
        try:
            if Path(self.filename).exists():
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {int(k): v for k, v in data.items()}
        except Exception as e:
            logger.error(f"Ошибка загрузки очков: {e}")
        return {}

    def save_scores(self):
        """Сохраняет очки в файл"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.scores, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения очков: {e}")

    def get_score(self, user_id: int) -> int:
        """Получает очки игрока"""
        return self.scores.get(user_id, {}).get('total', 0)

    def get_stats(self, user_id: int) -> dict:
        """Получает статистику игрока"""
        return self.scores.get(user_id, {
            'total': 0,
            'games_won': 0,
            'games_lost': 0,
            'hints_used': 0,
            'last_game': None
        })

    def add_points(self, user_id: int, points: int, game_result: str, hint_used: bool = False):
        """Добавляет очки и обновляет статистику"""
        stats = self.get_stats(user_id)
        stats['total'] += points

        if game_result == 'win':
            stats['games_won'] += 1
            if hint_used:
                stats['hints_used'] += 1
        elif game_result == 'loss':
            stats['games_lost'] += 1

        stats['last_game'] = datetime.now().isoformat()
        self.scores[user_id] = stats
        self.save_scores()


# Инициализация менеджера очков
score_manager = ScoreManager()


# Состояния FSM
class GameState(StatesGroup):
    playing = State()


class HangmanGame:
    def __init__(self, word: str, translation: str, hint_used: bool = False):
        self.word = word.lower()
        self.translation = translation
        self.guessed_letters = set()
        self.wrong_guesses = 0
        self.max_wrong = 6
        self.current_image = 1
        self.last_message_id = None
        self.hint_used = hint_used  # Флаг использования подсказки
        self.hint_shown = False  # Была ли показана подсказка в этой игре
        self.hint_text = None  # Текст подсказки для отображения

    def get_display_word(self) -> str:
        """Возвращает слово с отгаданными буквами и пропусками"""
        return ' '.join(
            letter if letter in self.guessed_letters else '_'
            for letter in self.word
        )

    def guess_letter(self, letter: str) -> bool:
        """Пробует угадать букву, возвращает True если буква есть в слове"""
        letter = letter.lower()

        if letter in self.guessed_letters:
            return False

        self.guessed_letters.add(letter)

        if letter in self.word:
            return True
        else:
            self.wrong_guesses += 1
            self.current_image = min(1 + self.wrong_guesses, 7)
            return False

    def use_hint(self) -> str:
        """Использует подсказку (перевод слова)"""
        self.hint_used = True
        self.hint_shown = True
        self.hint_text = f"💡 <b>Подсказка:</b> {self.translation}"
        return self.translation

    def is_won(self) -> bool:
        return all(letter in self.guessed_letters for letter in self.word)

    def is_lost(self) -> bool:
        return self.wrong_guesses >= self.max_wrong

    def get_image_path(self) -> str:
        image_num = max(1, min(self.current_image, 7))
        return IMAGES_DIR / f"{image_num}.png"

    def get_status_text(self, include_hint: bool = True) -> str:
        word_display = self.get_display_word()
        wrong_letters = [
            l for l in self.guessed_letters
            if l not in self.word and l.isalpha()
        ]

        status = ""

        # Добавляем подсказку, если она была использована
        if include_hint and self.hint_shown and self.hint_text:
            status += f"{self.hint_text}\n\n"

        status += f"<b>Слово:</b> {word_display}\n"
        status += f"<b>Ошибок:</b> {self.wrong_guesses}/{self.max_wrong}\n"

        if wrong_letters:
            status += f"<b>Неправильные буквы:</b> {', '.join(sorted(wrong_letters))}\n"

        if self.hint_shown:
            status += f"\n<i>Подсказка уже использована!</i>\n"

        return status


# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Хранение ID последних сообщений с изображениями
game_messages: Dict[int, int] = {}


# Создание клавиатуры с буквами
def create_letter_keyboard(guessed_letters: set = None, hint_used: bool = False) -> InlineKeyboardMarkup:
    """Создает inline клавиатуру с буквами алфавита"""
    if guessed_letters is None:
        guessed_letters = set()

    letters = "abcdefghijklmnopqrstuvwxyz"
    keyboard = []
    row = []

    for letter in letters:
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

        if len(row) == 7:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    # Кнопки управления игрой
    control_buttons = []

    # Кнопка подсказки (только если еще не использована)
    if not hint_used:
        control_buttons.append(
            InlineKeyboardButton(text="💡 Подсказка", callback_data="hint")
        )

    control_buttons.extend([
        InlineKeyboardButton(text="🔄 Новая игра", callback_data="new_game"),
        InlineKeyboardButton(text="🚪 Выйти", callback_data="quit_game"),
        InlineKeyboardButton(text="📖 Помощь", callback_data="help")
    ])

    keyboard.append(control_buttons)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Клавиатура для главного меню
def main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="🎮 Начать игру", callback_data="new_game"),
            InlineKeyboardButton(text="📊 Моя статистика", callback_data="stats")
        ],
        [
            InlineKeyboardButton(text="📖 Как играть", callback_data="how_to_play")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Отправка изображения виселицы
async def send_hangman_image(chat_id: int, game: HangmanGame, caption: str = "",
                             reply_markup: Optional[InlineKeyboardMarkup] = None,
                             edit_message: bool = False, message_id: Optional[int] = None):
    """Отправляет или редактирует сообщение с изображением виселицы"""

    image_path = game.get_image_path()

    if not image_path.exists():
        logger.error(f"Изображение не найдено: {image_path}")
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
        photo = FSInputFile(image_path)

        if edit_message and message_id:
            try:
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
                logger.warning(f"Не удалось отредактировать сообщение: {edit_error}")
                try:
                    await bot.delete_message(chat_id, message_id)
                except:
                    pass
                message = await bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=caption,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
                return message.message_id
        else:
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
    welcome_text = (
        "🎯 <b>Добро пожаловать в игру 'Виселица'!</b>\n\n"
        "Я загадаю английское слово из мира технологий и программирования, "
        "а тебе нужно будет угадать его по буквам, прежде чем человечек будет повешен!\n\n"
        "🎮 <b>Особенности игры:</b>\n"
        "• За победу без подсказки: +10 очков\n"
        "• За победу с подсказкой: +5 очков\n"
        "• Можно использовать подсказку (перевод слова) один раз за игру\n\n"
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
    help_text = (
        "🤖 <b>Команды бота:</b>\n\n"
        "/start - Запустить бота и показать главное меню\n"
        "/newgame - Начать новую игру\n"
        "/stats - Показать мою статистику\n"
        "/help - Показать эту справку\n\n"
        "🎮 <b>Как играть:</b>\n"
        "Нажми 'Начать игру', чтобы начать. Используй кнопки с буквами для угадывания. "
        "У тебя есть 6 неправильных попыток, прежде чем человечек будет повешен!\n\n"
        "💡 <b>Подсказка:</b>\n"
        "Если не знаешь слово, можешь использовать подсказку - она покажет перевод.\n"
        "Подсказку можно использовать только один раз за игру, но за победу с подсказкой "
        "ты получишь меньше очков (5 вместо 10).\n\n"
        "<i>Все слова на английском языке связаны с технологиями и программированием.</i>"
    )

    keyboard = [[InlineKeyboardButton(text="🎮 Начать игру", callback_data="new_game")]]

    await message.answer(
        help_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode='HTML'
    )


# Команда /stats
@dp.message(Command("stats"))
async def command_stats(message: Message):
    """Показывает статистику игрока"""
    user_id = message.from_user.id
    stats = score_manager.get_stats(user_id)

    stats_text = (
        f"📊 <b>Статистика игрока</b>\n\n"
        f"🏆 <b>Всего очков:</b> {stats['total']}\n"
        f"🎮 <b>Игр выиграно:</b> {stats['games_won']}\n"
        f"💀 <b>Игр проиграно:</b> {stats['games_lost']}\n"
        f"💡 <b>Использовано подсказок:</b> {stats['hints_used']}\n"
    )

    if stats['games_won'] > 0:
        win_rate = (stats['games_won'] / (stats['games_won'] + stats['games_lost'])) * 100
        stats_text += f"\n📈 <b>Процент побед:</b> {win_rate:.1f}%"

    if stats['last_game']:
        stats_text += f"\n\n🕐 <b>Последняя игра:</b> {stats['last_game'][:10]}"

    keyboard = [[InlineKeyboardButton(text="🎮 Новая игра", callback_data="new_game")]]

    await message.answer(
        stats_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode='HTML'
    )


# Показать статистику через кнопку
@dp.callback_query(F.data == "stats")
async def show_stats(callback: CallbackQuery):
    """Показывает статистику через кнопку"""
    await callback.answer()
    user_id = callback.from_user.id
    stats = score_manager.get_stats(user_id)

    stats_text = (
        f"📊 <b>Статистика игрока</b>\n\n"
        f"🏆 <b>Всего очков:</b> {stats['total']}\n"
        f"🎮 <b>Игр выиграно:</b> {stats['games_won']}\n"
        f"💀 <b>Игр проиграно:</b> {stats['games_lost']}\n"
        f"💡 <b>Использовано подсказок:</b> {stats['hints_used']}\n"
    )

    if stats['games_won'] > 0:
        win_rate = (stats['games_won'] / (stats['games_won'] + stats['games_lost'])) * 100
        stats_text += f"\n📈 <b>Процент побед:</b> {win_rate:.1f}%"

    keyboard = [[InlineKeyboardButton(text="🎮 Новая игра", callback_data="new_game")]]

    if callback.message.text:
        await callback.message.edit_text(
            stats_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode='HTML'
        )
    else:
        await callback.message.answer(
            stats_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode='HTML'
        )


# Команда /newgame
@dp.message(Command("newgame"))
async def command_newgame(message: Message, state: FSMContext):
    await start_new_game(message, state)


# Начало новой игры
@dp.callback_query(F.data == "new_game")
async def process_new_game(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await start_new_game(callback.message, state, callback.from_user.id)


async def start_new_game(message_source, state: FSMContext, user_id: int = None):
    if user_id is None:
        user_id = message_source.from_user.id

    word, translation = random.choice(WORDS_WITH_TRANSLATIONS)
    game = HangmanGame(word, translation)

    await state.update_data(game=game)
    await state.set_state(GameState.playing)

    keyboard = create_letter_keyboard()

    caption = (
        f"🎮 <b>Новая игра началась!</b>\n\n"
        f"Угадай английское слово, связанное с технологиями или программированием.\n\n"
        f"{game.get_status_text(include_hint=False)}\n"
        f"<i>Выбери букву или используй подсказку 💡</i>"
    )

    if isinstance(message_source, Message):
        chat_id = message_source.chat.id
        if user_id in game_messages:
            try:
                await bot.delete_message(chat_id, game_messages[user_id])
            except:
                pass

        message_id = await send_hangman_image(chat_id, game, caption, keyboard)
        if message_id:
            game_messages[user_id] = message_id
            game.last_message_id = message_id

    else:
        chat_id = message_source.chat.id
        if user_id in game_messages:
            try:
                await bot.delete_message(chat_id, game_messages[user_id])
            except:
                pass

        message_id = await send_hangman_image(chat_id, game, caption, keyboard)
        if message_id:
            game_messages[user_id] = message_id
            game.last_message_id = message_id


# Обработка подсказки
@dp.callback_query(F.data == "hint", GameState.playing)
async def process_hint(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает запрос подсказки"""
    data = await state.get_data()
    game: HangmanGame = data.get("game")

    if not game:
        await callback.answer("Игра не найдена!", show_alert=True)
        return

    if game.hint_shown:
        await callback.answer("Ты уже использовал(а) подсказку в этой игре!", show_alert=True)
        return

    # Показываем подсказку
    translation = game.use_hint()

    # Обновляем игру в состоянии
    await state.update_data(game=game)

    # Обновляем клавиатуру (убираем кнопку подсказки)
    keyboard = create_letter_keyboard(game.guessed_letters, hint_used=True)

    # Формируем текст с подсказкой
    caption = (
        f"{game.get_status_text(include_hint=True)}\n"
        f"<i>Выбери букву:</i>"
    )

    # Обновляем сообщение
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

    # Отправляем отдельное уведомление о подсказке
    await callback.answer(f"💡 Подсказка: {translation}", show_alert=True)


# Как играть
@dp.callback_query(F.data == "how_to_play")
async def process_how_to_play(callback: CallbackQuery):
    await callback.answer()

    instructions = (
        "🎮 <b>Как играть в 'Виселицу'</b>\n\n"
        "1. Я загадываю случайное английское слово\n"
        "2. Ты видишь пропуски для каждой буквы\n"
        "3. Угадывай буквы по одной с помощью кнопок\n"
        "4. Правильные буквы открываются в слове\n"
        "5. Неправильные буквы добавляют части к виселице\n"
        "6. Ты выигрываешь, если угадаешь слово до того, как человечек будет полностью повешен!\n\n"
        "💡 <b>Система очков:</b>\n"
        "• Победа без подсказки: <b>+10 очков</b>\n"
        "• Победа с подсказкой: <b>+5 очков</b>\n"
        "• За поражение очки не начисляются\n\n"
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
    await callback.answer()

    letter = callback.data.split(":")[1]
    data = await state.get_data()
    game: HangmanGame = data.get("game")

    if not game:
        await callback.answer("Игра не найдена. Начни новую!", show_alert=True)
        return

    is_correct = game.guess_letter(letter)
    await state.update_data(game=game)

    if game.is_won():
        # Определяем количество очков
        points = 5 if game.hint_used else 10
        score_manager.add_points(callback.from_user.id, points, 'win', game.hint_used)

        caption = (
            f"🎉 <b>Поздравляю! Ты выиграл(а)!</b>\n\n"
            f"{game.get_status_text(include_hint=True)}\n"
            f"<b>Слово было:</b> {game.word.upper()}\n"
            f"<b>Перевод:</b> {game.translation}\n"
            f"{'💡 Подсказка использована' if game.hint_used else '🏆 Без подсказки'}\n\n"
            f"✨ <b>Ты получил(а) +{points} очков!</b>\n"
            f"📊 <b>Всего очков:</b> {score_manager.get_score(callback.from_user.id)}"
        )

        keyboard = [[InlineKeyboardButton(text="🔄 Играть снова", callback_data="new_game")]]

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
        score_manager.add_points(callback.from_user.id, 0, 'loss', game.hint_used)

        caption = (
            f"💀 <b>Игра окончена! Ты проиграл(а)!</b>\n\n"
            f"{game.get_status_text(include_hint=True)}\n"
            f"<b>Слово было:</b> {game.word.upper()}\n"
            f"<b>Перевод:</b> {game.translation}\n\n"
            f"Попробуй еще раз!\n"
            f"📊 <b>Всего очков:</b> {score_manager.get_score(callback.from_user.id)}"
        )

        keyboard = [[InlineKeyboardButton(text="🔄 Попробовать снова", callback_data="new_game")]]

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
        if is_correct:
            result_msg = f"✅ Буква '{letter.upper()}' есть в слове!"
        else:
            result_msg = f"❌ Буквы '{letter.upper()}' нет в слове!"

        caption = (
            f"{result_msg}\n\n"
            f"{game.get_status_text(include_hint=True)}\n"
            f"<i>Выбери следующую букву:</i>"
        )

        keyboard = create_letter_keyboard(game.guessed_letters, game.hint_used)

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
    await callback.answer("Ты уже угадывал(а) эту букву!", show_alert=True)


# Выход из игры
@dp.callback_query(F.data == "quit_game")
async def process_quit_game(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    game: HangmanGame = data.get("game")

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
            f"📊 <b>Твои очки:</b> {score_manager.get_score(user_id)}\n\n"
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
    await callback.answer()

    data = await state.get_data()
    game = data.get("game")

    help_text = (
        "🎮 <b>Как играть</b>\n\n"
        "Угадай английское слово по буквам с помощью кнопок.\n"
        "У тебя есть максимум 6 неправильных попыток.\n"
        "Слово связано с технологиями или программированием.\n\n"
        "💡 <b>Подсказка:</b> показывает перевод слова (один раз за игру)\n"
        "🏆 <b>Очки:</b> +10 без подсказки, +5 с подсказкой\n\n"
        "<i>Нажми 'Вернуться в игру', чтобы продолжить.</i>"
    )

    keyboard = [
        [InlineKeyboardButton(text="↩️ Вернуться в игру", callback_data="back_to_game")],
        [InlineKeyboardButton(text="🚪 Выйти из игры", callback_data="quit_game")]
    ]

    if game:
        game_data = {
            'word': game.word,
            'translation': game.translation,
            'guessed_letters': list(game.guessed_letters),
            'wrong_guesses': game.wrong_guesses,
            'current_image': game.current_image,
            'last_message_id': game.last_message_id,
            'hint_used': game.hint_used,
            'hint_shown': game.hint_shown,
            'hint_text': game.hint_text
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
    await callback.answer()

    data = await state.get_data()
    saved_game = data.get('saved_game')

    if saved_game:
        game = HangmanGame(saved_game['word'], saved_game['translation'], saved_game['hint_used'])
        game.guessed_letters = set(saved_game['guessed_letters'])
        game.wrong_guesses = saved_game['wrong_guesses']
        game.current_image = saved_game['current_image']
        game.last_message_id = saved_game['last_message_id']
        game.hint_shown = saved_game['hint_shown']
        game.hint_text = saved_game.get('hint_text')

        await state.update_data(game=game)
        await state.set_state(GameState.playing)

        try:
            await callback.message.delete()
        except:
            pass

        caption = f"{game.get_status_text(include_hint=True)}\n<i>Выбери букву:</i>"
        keyboard = create_letter_keyboard(game.guessed_letters, game.hint_used)

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
        await callback.message.edit_text(
            "Не удалось восстановить игру. Начинаем новую...",
            reply_markup=main_menu_keyboard()
        )


# Обработка других сообщений
@dp.message()
async def handle_other_messages(message: Message):
    await message.answer(
        "Я понимаю только команды и нажатия на кнопки! 🤖\n\n"
        "Используй /start чтобы начать или /help для инструкций.",
        reply_markup=main_menu_keyboard()
    )


# Основная функция запуска бота
async def main():
    print("Бот запускается...")
    print(f"Папка с изображениями: {IMAGES_DIR.absolute()}")
    print(f"Файл статистики: {SCORES_FILE}")

    # Проверяем наличие изображений
    for i in range(1, 8):
        image_path = IMAGES_DIR / f"{i}.png"
        if image_path.exists():
            print(f"✓ Найдено изображение: {image_path.name}")
        else:
            print(f"✗ Отсутствует изображение: {image_path.name}")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())