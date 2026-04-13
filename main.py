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
SCORES_FILE = "player_scores.json"

# Technical vocabulary with translations
WORDS_WITH_TRANSLATIONS: List[Tuple[str, str]] = [
    # Core Programming Concepts
    ("algorithm", "Step-by-step procedure for solving a problem"),
    ("function", "Reusable block of code that performs a specific task"),
    ("variable", "Named storage location for data in memory"),
    ("constant", "Value that cannot be changed after initialization"),
    ("parameter", "Input variable passed to a function"),
    ("argument", "Actual value supplied to a function parameter"),
    ("statement", "Single instruction in a programming language"),
    ("expression", "Combination of values and operators that evaluates to a value"),
    ("operator", "Symbol that performs an operation on operands"),
    ("operand", "Value or variable that an operator acts upon"),
    ("condition", "Boolean expression controlling program flow"),
    ("loop", "Structure that repeats code execution"),
    ("iteration", "Single pass through a loop body"),
    ("recursion", "Technique where a function calls itself"),
    ("exception", "Error event that disrupts normal program flow"),
    ("debugging", "Process of finding and fixing errors in code"),
    ("compilation", "Translation of source code to machine code"),
    ("execution", "Running a computer program"),
    ("syntax", "Rules governing code structure and formatting"),
    ("semantics", "Meaning and logic behind code constructs"),

    # Data Structures
    ("array", "Collection of elements stored at contiguous memory locations"),
    ("list", "Ordered collection that can contain duplicate items"),
    ("dictionary", "Collection of key-value pairs for fast lookup"),
    ("tuple", "Immutable ordered collection of elements"),
    ("collection", "Group of objects stored together"),
    ("element", "Single item within a collection"),
    ("index", "Numerical position of an element in a sequence"),
    ("stack", "Data structure with last-in-first-out access"),
    ("queue", "Data structure with first-in-first-out access"),
    ("linkedlist", "Linear collection where elements point to each other"),
    ("node", "Basic unit of a data structure containing data and links"),
    ("tree", "Hierarchical data structure with parent-child relationships"),
    ("root", "Topmost node in a tree structure"),
    ("leaf", "Node with no children in a tree"),
    ("graph", "Collection of vertices connected by edges"),
    ("vertex", "Point or node in a graph structure"),
    ("edge", "Connection between two vertices in a graph"),
    ("hashmap", "Data structure mapping keys to values using hash function"),
    ("hashtable", "Data structure implementing associative array"),
    ("vector", "Dynamic array that can resize automatically"),

    # Software Development
    ("development", "Process of creating software applications"),
    ("requirement", "Necessary feature or condition for software"),
    ("design", "Planning phase of software architecture"),
    ("implementation", "Writing actual code for software"),
    ("testing", "Verifying software correctness and quality"),
    ("integration", "Combining software components together"),
    ("deployment", "Making software available for users"),
    ("maintenance", "Ongoing updates and fixes for software"),
    ("refactoring", "Restructuring code without changing behavior"),
    ("documentation", "Written description of software functionality"),
    ("repository", "Storage location for source code"),
    ("versioncontrol", "System tracking changes to files over time"),
    ("branch", "Separate line of development in version control"),
    ("merge", "Combining different development branches"),
    ("commit", "Saving changes to version control repository"),
    ("workflow", "Sequence of automated or manual steps"),
    ("pipeline", "Series of data processing stages"),
    ("automation", "Technology performing tasks without human intervention"),
    ("script", "Short program automating repetitive tasks"),
    ("toolchain", "Set of programming tools used to build software"),

    # Databases
    ("database", "Organized collection of structured information"),
    ("table", "Collection of related data in rows and columns"),
    ("row", "Single record in a database table"),
    ("column", "Single field in a database table"),
    ("query", "Request for data from a database"),
    ("index", "Data structure improving database lookup speed"),
    ("primarykey", "Unique identifier for a database record"),
    ("foreignkey", "Reference to a primary key in another table"),
    ("migration", "Process of changing database schema"),
    ("transaction", "Unit of work performed on a database"),
    ("backup", "Copy of data for recovery purposes"),
    ("restore", "Process of recovering data from backup"),

    # Web Development
    ("server", "Computer providing services to other computers"),
    ("client", "Computer requesting services from a server"),
    ("browser", "Software application for accessing websites"),
    ("website", "Collection of web pages under one domain"),
    ("webpage", "Single document on the world wide web"),
    ("hyperlink", "Reference linking to another document"),
    ("url", "Web address pointing to a resource"),
    ("domain", "Human-readable website name"),
    ("hosting", "Service providing server space for websites"),
    ("backend", "Server-side part of a web application"),
    ("frontend", "Client-side part of a web application visible to users"),
    ("middleware", "Software connecting different applications"),
    ("endpoint", "One end of a communication channel"),
    ("request", "Message sent from client to server"),
    ("response", "Message sent from server back to client"),
    ("session", "Temporary interactive information exchange"),
    ("cookie", "Small data file stored by websites"),
    ("cache", "Hardware or software storing temporary data"),
    ("buffer", "Temporary storage area for data transfer"),

    # Networking
    ("network", "Connected computing devices sharing resources"),
    ("internet", "Global system of interconnected computer networks"),
    ("connection", "Link between two devices on a network"),
    ("bandwidth", "Maximum data transfer rate of a network"),
    ("latency", "Delay between sending and receiving data"),
    ("packet", "Unit of data transmitted over a network"),
    ("router", "Device forwarding data between networks"),
    ("firewall", "Network security system monitoring traffic"),
    ("encryption", "Converting data into secret code"),
    ("decryption", "Converting encrypted data back to original"),
    ("authentication", "Process of verifying identity"),
    ("authorization", "Process of checking access rights"),
    ("certificate", "Digital document verifying identity"),
    ("protocol", "Set of rules for data exchange"),
    ("gateway", "Node connecting different networks"),

    # Operating Systems
    ("operatingsystem", "Software managing computer hardware and software"),
    ("kernel", "Core component of an operating system"),
    ("process", "Program in execution with its own memory space"),
    ("thread", "Lightweight unit of execution within a process"),
    ("memory", "Computer component storing data temporarily"),
    ("storage", "Hardware retaining data permanently"),
    ("filesystem", "Method for storing and organizing files"),
    ("directory", "Folder containing files and other directories"),
    ("permission", "Rule controlling access to resources"),
    ("interface", "Boundary allowing interaction between components"),
    ("driver", "Software controlling a hardware device"),
    ("firmware", "Permanent software stored in hardware"),
    ("scheduling", "Method of allocating resources to tasks"),
    ("synchronization", "Coordinating simultaneous execution"),
    ("deadlock", "Situation where processes wait indefinitely for resources"),

    # Hardware
    ("processor", "Central component executing computer instructions"),
    ("motherboard", "Main circuit board connecting computer components"),
    ("memorymodule", "Hardware component storing temporary data"),
    ("storagedevice", "Hardware retaining data permanently"),
    ("harddrive", "Magnetic storage device for permanent data"),
    ("solidstatedrive", "Flash-based storage device with no moving parts"),
    ("graphicscard", "Component rendering images and video"),
    ("soundcard", "Component handling audio input and output"),
    ("networkcard", "Component enabling network connectivity"),
    ("powersupply", "Hardware converting and providing electrical power"),
    ("coolingsystem", "Hardware removing heat from computer components"),
    ("peripheral", "External device connected to a computer"),
    ("keyboard", "Input device with keys for typing"),
    ("mouse", "Pointing device for computer interaction"),
    ("monitor", "Display device showing visual output"),
    ("printer", "Device producing physical copies of documents"),
    ("scanner", "Device converting physical documents to digital"),
    ("speaker", "Device producing sound output"),
    ("microphone", "Device capturing sound input"),
    ("webcam", "Camera capturing video for computers"),
    ("headphones", "Personal audio output devices"),

    # Software Engineering
    ("engineering", "Discipline of designing and building software"),
    ("architecture", "High-level structure of software systems"),
    ("methodology", "System of methods used in software development"),
    ("waterfall", "Sequential software development process"),
    ("agile", "Iterative approach to software development"),
    ("scrum", "Framework for managing complex product development"),
    ("planning", "Process of defining software project scope"),
    ("estimation", "Predicting effort required for development"),
    ("deadline", "Time by which a task must be completed"),
    ("milestone", "Significant event in project timeline"),
    ("deliverable", "Tangible product produced during development"),
    ("quality", "Degree of excellence in software products"),
    ("performance", "Speed and efficiency of software execution"),
    ("reliability", "Probability of software functioning correctly"),
    ("scalability", "Ability to handle growing amounts of work"),
    ("availability", "Percentage of time software is operational"),
    ("usability", "Ease of use for software products"),
    ("accessibility", "Design making software usable for everyone"),

    # Cloud Computing
    ("cloudcomputing", "Delivery of computing services over the internet"),
    ("virtualmachine", "Software emulation of a physical computer"),
    ("container", "Standardized unit packaging software and dependencies"),
    ("virtualization", "Creating virtual versions of hardware platforms"),
    ("scalability", "Ability to handle increasing workload"),
    ("redundancy", "Duplication of critical components for reliability"),
    ("loadbalancing", "Distributing workload across multiple resources"),
    ("elasticity", "Ability to scale resources up and down automatically"),

    # Artificial Intelligence
    ("artificialintelligence", "Machine simulating human intelligence"),
    ("machinelearning", "Artificial intelligence learning from data"),
    ("neuralnetwork", "Computational system inspired by biological brains"),
    ("deeplearning", "Advanced machine learning using multiple layers"),
    ("training", "Process of teaching artificial intelligence using data"),
    ("model", "Trained artificial intelligence system"),
    ("prediction", "Output estimate from artificial intelligence"),
    ("classification", "Categorizing data using artificial intelligence"),
    ("recognition", "Identifying patterns in data"),
    ("dataset", "Collection of data used for training"),
    ("feature", "Individual measurable property of data"),
    ("label", "Expected output value for training example"),

    # Security
    ("security", "Protection of computer systems from threats"),
    ("malware", "Software designed to harm computer systems"),
    ("virus", "Self-replicating malicious code attaching to programs"),
    ("worm", "Self-replicating malware spreading without user action"),
    ("trojan", "Malware disguised as legitimate software"),
    ("ransomware", "Malware encrypting data and demanding payment"),
    ("spyware", "Malware secretly collecting user information"),
    ("antivirus", "Software detecting and removing malware"),
    ("phishing", "Fraudulent attempt to obtain sensitive information"),
    ("spam", "Unsolicited electronic messages sent in bulk"),
    ("vulnerability", "Weakness allowing attacker to compromise system"),
    ("exploit", "Code taking advantage of a vulnerability"),
    ("patch", "Software update fixing security issues"),
    ("update", "New version of software with improvements"),

    # General Technical Terms
    ("abstraction", "Hiding implementation details to reduce complexity"),
    ("modularity", "Dividing software into separate interchangeable modules"),
    ("encapsulation", "Bundling data with methods operating on that data"),
    ("inheritance", "Mechanism for deriving classes from existing classes"),
    ("polymorphism", "Ability to present same interface for different types"),
    ("interface", "Shared boundary for interaction between components"),
    ("instance", "Single occurrence of an object at runtime"),
    ("object", "Collection of data and methods in programming"),
    ("class", "Blueprint for creating objects in programming"),
    ("method", "Function belonging to an object or class"),
    ("property", "Attribute or characteristic of an object"),
    ("constructor", "Method initializing newly created objects"),
    ("destructor", "Method cleaning up before object destruction"),
    ("overloading", "Multiple implementations with same name"),
    ("overriding", "Replacing inherited implementation"),
    ("callback", "Function passed as argument to another function"),
    ("event", "Action or occurrence detected by software"),
    ("handler", "Code responding to events"),
    ("listener", "Object waiting for specific events"),
    ("stream", "Sequence of data elements made available over time"),
    ("token", "Symbol representing something else in computing"),
    ("metadata", "Data providing information about other data"),
    ("hardcoding", "Fixing values directly in source code"),
    ("workaround", "Temporary solution for a problem"),
    ("legacy", "Old software systems still in use"),
    ("standalone", "Software operating independently without dependencies"),
    ("realitime", "System responding to events within time constraints"),
    ("batchprocessing", "Executing jobs without manual intervention"),
    ("background", "Process running without user interface")
]

# Класс для управления очками игроков
class ScoreManager:
    def __init__(self, filename: str = SCORES_FILE):
        self.filename = filename
        self.scores = self.load_scores()

    def load_scores(self) -> Dict[int, dict]:
        """Loads scores from file"""
        try:
            if Path(self.filename).exists():
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {int(k): v for k, v in data.items()}
        except Exception as e:
            logger.error(f"Error loading scores: {e}")
        return {}

    def save_scores(self):
        """Saves scores to file"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.scores, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving scores: {e}")

    def get_score(self, user_id: int) -> int:
        """Gets player's total score"""
        return self.scores.get(user_id, {}).get('total', 0)

    def get_stats(self, user_id: int) -> dict:
        """Gets player's statistics"""
        return self.scores.get(user_id, {
            'total': 0,
            'games_won': 0,
            'games_lost': 0,
            'hints_used': 0,
            'last_game': None
        })

    def add_points(self, user_id: int, points: int, game_result: str, hint_used: bool = False):
        """Adds points and updates statistics"""
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


# Initialize score manager
score_manager = ScoreManager()


# FSM States
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
        self.hint_used = hint_used
        self.hint_shown = False
        self.hint_text = None

    def get_display_word(self) -> str:
        """Returns word with guessed letters revealed"""
        return ' '.join(
            letter if letter in self.guessed_letters else '_'
            for letter in self.word
        )

    def guess_letter(self, letter: str) -> bool:
        """Attempts to guess a letter, returns True if letter is in word"""
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
        """Uses hint (word translation)"""
        self.hint_used = True
        self.hint_shown = True
        self.hint_text = f"💡 <b>Hint:</b> {self.translation}"
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

        if include_hint and self.hint_shown and self.hint_text:
            status += f"{self.hint_text}\n\n"

        status += f"<b>Word:</b> {word_display}\n"
        status += f"<b>Wrong guesses:</b> {self.wrong_guesses}/{self.max_wrong}\n"

        if wrong_letters:
            status += f"<b>Wrong letters:</b> {', '.join(sorted(wrong_letters))}\n"

        if self.hint_shown:
            status += f"\n<i>Hint already used!</i>\n"

        return status


# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Store message IDs for game images
game_messages: Dict[int, int] = {}


# Create letter keyboard
def create_letter_keyboard(guessed_letters: set = None, hint_used: bool = False) -> InlineKeyboardMarkup:
    """Creates inline keyboard with alphabet letters"""
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

    # Game control buttons
    control_buttons = []

    if not hint_used:
        control_buttons.append(
            InlineKeyboardButton(text="💡 Hint", callback_data="hint")
        )

    control_buttons.extend([
        InlineKeyboardButton(text="🔄 New Game", callback_data="new_game"),
        InlineKeyboardButton(text="🚪 Quit", callback_data="quit_game"),
        InlineKeyboardButton(text="📖 Help", callback_data="help")
    ])

    keyboard.append(control_buttons)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Main menu keyboard
def main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="🎮 Start Game", callback_data="new_game"),
            InlineKeyboardButton(text="📊 My Stats", callback_data="stats")
        ],
        [
            InlineKeyboardButton(text="📖 How to Play", callback_data="how_to_play")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Send hangman image
async def send_hangman_image(chat_id: int, game: HangmanGame, caption: str = "",
                             reply_markup: Optional[InlineKeyboardMarkup] = None,
                             edit_message: bool = False, message_id: Optional[int] = None):
    """Sends or edits message with hangman image"""

    image_path = game.get_image_path()

    if not image_path.exists():
        logger.error(f"Image not found: {image_path}")
        if not edit_message:
            message = await bot.send_message(
                chat_id,
                f"⚠️ Hangman image not found.\n\n{caption}",
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            return message.message_id
        else:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"⚠️ Hangman image not found.\n\n{caption}",
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
                logger.warning(f"Failed to edit message: {edit_error}")
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
        logger.error(f"Error sending image: {e}")
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


# Command /start
@dp.message(CommandStart())
async def command_start(message: Message):
    welcome_text = (
        "🎯 <b>Welcome to Hangman Game!</b>\n\n"
        "I'll think of an English technical word, and you need to guess it "
        "letter by letter before the man gets hanged!\n\n"
        "🎮 <b>Game Features:</b>\n"
        "• Victory without hint: +10 points\n"
        "• Victory with hint: +5 points\n"
        "• You can use one hint (translation) per game\n\n"
        "Press the button below to start a new game!"
    )

    await message.answer(
        welcome_text,
        reply_markup=main_menu_keyboard(),
        parse_mode='HTML'
    )


# Command /help
@dp.message(Command("help"))
async def command_help(message: Message):
    help_text = (
        "🤖 <b>Bot Commands:</b>\n\n"
        "/start - Launch bot and show main menu\n"
        "/newgame - Start a new game\n"
        "/stats - Show my statistics\n"
        "/help - Show this help message\n\n"
        "🎮 <b>How to Play:</b>\n"
        "Press 'Start Game' to begin. Use letter buttons to guess. "
        "You have 6 wrong attempts before the man is hanged!\n\n"
        "💡 <b>Hint:</b>\n"
        "If you don't know the word, you can use a hint - it shows the meaning.\n"
        "Hint can be used only once per game, but victory with hint gives "
        "fewer points (5 instead of 10).\n\n"
        "<i>All words are technical terms related to programming and IT.</i>"
    )

    keyboard = [[InlineKeyboardButton(text="🎮 Start Game", callback_data="new_game")]]

    await message.answer(
        help_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode='HTML'
    )


# Command /stats
@dp.message(Command("stats"))
async def command_stats(message: Message):
    """Shows player statistics"""
    user_id = message.from_user.id
    stats = score_manager.get_stats(user_id)

    stats_text = (
        f"📊 <b>Player Statistics</b>\n\n"
        f"🏆 <b>Total Score:</b> {stats['total']}\n"
        f"🎮 <b>Games Won:</b> {stats['games_won']}\n"
        f"💀 <b>Games Lost:</b> {stats['games_lost']}\n"
        f"💡 <b>Hints Used:</b> {stats['hints_used']}\n"
    )

    if stats['games_won'] > 0:
        win_rate = (stats['games_won'] / (stats['games_won'] + stats['games_lost'])) * 100
        stats_text += f"\n📈 <b>Win Rate:</b> {win_rate:.1f}%"

    if stats['last_game']:
        stats_text += f"\n\n🕐 <b>Last Game:</b> {stats['last_game'][:10]}"

    keyboard = [[InlineKeyboardButton(text="🎮 New Game", callback_data="new_game")]]

    await message.answer(
        stats_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode='HTML'
    )


# Show stats via button
@dp.callback_query(F.data == "stats")
async def show_stats(callback: CallbackQuery):
    """Shows statistics via button"""
    await callback.answer()
    user_id = callback.from_user.id
    stats = score_manager.get_stats(user_id)

    stats_text = (
        f"📊 <b>Player Statistics</b>\n\n"
        f"🏆 <b>Total Score:</b> {stats['total']}\n"
        f"🎮 <b>Games Won:</b> {stats['games_won']}\n"
        f"💀 <b>Games Lost:</b> {stats['games_lost']}\n"
        f"💡 <b>Hints Used:</b> {stats['hints_used']}\n"
    )

    if stats['games_won'] > 0:
        win_rate = (stats['games_won'] / (stats['games_won'] + stats['games_lost'])) * 100
        stats_text += f"\n📈 <b>Win Rate:</b> {win_rate:.1f}%"

    keyboard = [[InlineKeyboardButton(text="🎮 New Game", callback_data="new_game")]]

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


# Command /newgame
@dp.message(Command("newgame"))
async def command_newgame(message: Message, state: FSMContext):
    await start_new_game(message, state)


# Start new game
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
        f"🎮 <b>New Game Started!</b>\n\n"
        f"Guess the technical English word related to programming and IT.\n\n"
        f"{game.get_status_text(include_hint=False)}\n"
        f"<i>Choose a letter or use the hint 💡</i>"
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


# Handle hint
@dp.callback_query(F.data == "hint", GameState.playing)
async def process_hint(callback: CallbackQuery, state: FSMContext):
    """Handles hint request"""
    data = await state.get_data()
    game: HangmanGame = data.get("game")

    if not game:
        await callback.answer("Game not found!", show_alert=True)
        return

    if game.hint_shown:
        await callback.answer("You've already used the hint in this game!", show_alert=True)
        return

    translation = game.use_hint()

    await state.update_data(game=game)

    keyboard = create_letter_keyboard(game.guessed_letters, hint_used=True)

    caption = (
        f"{game.get_status_text(include_hint=True)}\n"
        f"<i>Choose a letter:</i>"
    )

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

    await callback.answer(f"💡 Hint: {translation}", show_alert=True)


# How to play
@dp.callback_query(F.data == "how_to_play")
async def process_how_to_play(callback: CallbackQuery):
    await callback.answer()

    instructions = (
        "🎮 <b>How to Play Hangman</b>\n\n"
        "1. I think of a random English technical word\n"
        "2. You see blanks for each letter\n"
        "3. Guess letters one by one using the buttons\n"
        "4. Correct guesses reveal the letter\n"
        "5. Wrong guesses add parts to the hangman\n"
        "6. You win if you guess the word before the man is fully hanged!\n\n"
        "💡 <b>Scoring System:</b>\n"
        "• Victory without hint: <b>+10 points</b>\n"
        "• Victory with hint: <b>+5 points</b>\n"
        "• No points for loss\n\n"
        "💡 <b>Tips:</b>\n"
        "• Start with common vowels: A, E, I, O, U\n"
        "• Then try common consonants: T, N, S, R, L\n"
        "• All words are <i>technical terms from programming and IT</i>\n\n"
        "<b>Ready to play?</b>"
    )

    keyboard = [[InlineKeyboardButton(text="🎮 Start Game", callback_data="new_game")]]

    await callback.message.edit_text(
        instructions,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode='HTML'
    )


# Handle letter guess
@dp.callback_query(F.data.startswith("letter:"), GameState.playing)
async def process_letter_guess(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    letter = callback.data.split(":")[1]
    data = await state.get_data()
    game: HangmanGame = data.get("game")

    if not game:
        await callback.answer("Game not found. Start a new game!", show_alert=True)
        return

    is_correct = game.guess_letter(letter)
    await state.update_data(game=game)

    if game.is_won():
        points = 5 if game.hint_used else 10
        score_manager.add_points(callback.from_user.id, points, 'win', game.hint_used)

        caption = (
            f"🎉 <b>Congratulations! You won!</b>\n\n"
            f"{game.get_status_text(include_hint=True)}\n"
            f"<b>The word was:</b> {game.word.upper()}\n"
            f"<b>Meaning:</b> {game.translation}\n"
            f"{'💡 Hint was used' if game.hint_used else '🏆 Without hint'}\n\n"
            f"✨ <b>You earned +{points} points!</b>\n"
            f"📊 <b>Total score:</b> {score_manager.get_score(callback.from_user.id)}"
        )

        keyboard = [[InlineKeyboardButton(text="🔄 Play Again", callback_data="new_game")]]

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
            f"💀 <b>Game Over! You lost!</b>\n\n"
            f"{game.get_status_text(include_hint=True)}\n"
            f"<b>The word was:</b> {game.word.upper()}\n"
            f"<b>Meaning:</b> {game.translation}\n\n"
            f"Try again!\n"
            f"📊 <b>Total score:</b> {score_manager.get_score(callback.from_user.id)}"
        )

        keyboard = [[InlineKeyboardButton(text="🔄 Try Again", callback_data="new_game")]]

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
            result_msg = f"✅ Letter '{letter.upper()}' is in the word!"
        else:
            result_msg = f"❌ Letter '{letter.upper()}' is not in the word!"

        caption = (
            f"{result_msg}\n\n"
            f"{game.get_status_text(include_hint=True)}\n"
            f"<i>Choose the next letter:</i>"
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


# Handle already guessed letters
@dp.callback_query(F.data == "already_guessed")
async def process_already_guessed(callback: CallbackQuery):
    await callback.answer("You've already guessed this letter!", show_alert=True)


# Quit game
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
            f"Game cancelled.\n\n"
            f"<b>The word was:</b> {game.word.upper()}\n"
            f"<b>Meaning:</b> {game.translation}\n\n"
            f"📊 <b>Your score:</b> {score_manager.get_score(user_id)}\n\n"
            f"Start a new game when you're ready!"
        )
    else:
        message_text = "No active game to quit."

    await state.clear()

    keyboard = [[InlineKeyboardButton(text="🎮 Start New Game", callback_data="new_game")]]

    await callback.message.answer(
        message_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode='HTML'
    )


# Help button during game
@dp.callback_query(F.data == "help")
async def process_help_from_game(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    game = data.get("game")

    help_text = (
        "🎮 <b>How to Play</b>\n\n"
        "Guess the English technical word using the letter buttons.\n"
        "You have a maximum of 6 wrong attempts.\n"
        "The word is related to programming and IT.\n\n"
        "💡 <b>Hint:</b> Shows the word meaning (once per game)\n"
        "🏆 <b>Points:</b> +10 without hint, +5 with hint\n\n"
        "<i>Press 'Back to Game' to continue playing.</i>"
    )

    keyboard = [
        [InlineKeyboardButton(text="↩️ Back to Game", callback_data="back_to_game")],
        [InlineKeyboardButton(text="🚪 Quit Game", callback_data="quit_game")]
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


# Return to game from help
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

        caption = f"{game.get_status_text(include_hint=True)}\n<i>Choose a letter:</i>"
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
            "Could not restore the game. Starting a new one...",
            reply_markup=main_menu_keyboard()
        )


# Handle other messages
@dp.message()
async def handle_other_messages(message: Message):
    await message.answer(
        "I only understand commands and button clicks! 🤖\n\n"
        "Use /start to begin or /help for instructions.",
        reply_markup=main_menu_keyboard()
    )


# Main function to run the bot
async def main():
    print("Bot is starting...")
    print(f"Images folder: {IMAGES_DIR.absolute()}")
    print(f"Statistics file: {SCORES_FILE}")

    # Check for images
    for i in range(1, 8):
        image_path = IMAGES_DIR / f"{i}.png"
        if image_path.exists():
            print(f"✓ Found image: {image_path.name}")
        else:
            print(f"✗ Missing image: {image_path.name}")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())