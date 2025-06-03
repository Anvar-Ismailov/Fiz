import os
import requests
import logging
from flask import Flask, request, jsonify
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# Токен бота
TOKEN = os.environ.get('BOT_TOKEN', "7179080851:AAGu_seX2xH6Q9WeY7tu6qT0i4BR6K1yje4")
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'https://your-app-name.onrender.com')

# Flask приложение
app = Flask(__name__)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Данные бота
TERMS = {
    "инерция": "Инерция — дененің өз қозғалыс күйін сақтау қасиеті. Егер денеге сырттан күш әсер етпесе, дене өзінің бастапқы тыныштық күйін немесе түзу сызықты бірқалыпты қозғалысын сақтайды...",
    "жылдамдық": "Жылдамдық — қозғалыстағы дененің орын ауыстыруының уақытқа қатынасы. Бұл — векторлық шама...",
    "масса": "Масса — дененің инерциясының және гравитациялық өзара әрекеттестіктің өлшемі...",
    "күш": "Күш — денелердің қозғалысын немесе пішінін өзгертуге әсер ететін физикалық шама...",
    "үдеу": "Үдеу — дененің жылдамдығының уақыт бойынша өзгеру жылдамдығы...",
    "энергия": "Энергия — дененің жұмыс істеу қабілетін сипаттайтын скалярлық шама...",
    "кинетикалық энергия": "Кинетикалық энергия — қозғалыстағы дененің энергиясы. Ek = (mv²)/2...",
    "потенциалдық энергия": "Потенциалдық энергия — дененің орналасуына немесе серпімділік күйіне байланысты жинақталған энергия...",
    "импульс": "Импульс — дененің қозғалысын сипаттайтын векторлық шама. p = mv...",
    "қысым": "Қысым — бірлік ауданға түсірілген күш. P = F/S...",
    "тығыздық": "Тығыздық — заттың бірлік көлеміндегі массасы. Формула: ρ = m/V...",
    "жұмыс": "Жұмыс — күш әсерінен орын ауыстыру кезінде орындалатын физикалық шама...",
    "қуат": "Қуат — жұмыстың орындалу жылдамдығы. N = A/t...",
    "ом заңы": "Ом заңы — өткізгіштегі ток күші I өткізгіш ұштарындағы кернеуге U тура пропорционал, кедергіге R кері пропорционал: I = U/R...",
    "магнит өрісі": "Магнит өрісі — электр зарядтарының қозғалысы кезінде пайда болатын күш өрісі...",
    "электр өрісі": "Электр өрісі — электр зарядтарының айналасында пайда болатын күш өрісі...",
    "кернеу": "Кернеу — электр өрісіндегі екі нүктенің потенциалдар айырмасы...",
    "ток күші": "Ток күші — өткізгіштің көлденең қимасы арқылы өтетін электр зарядының уақытқа қатынасы...",
    "индукция": "Индукция — магнит өрісінің өзгерісі кезінде электр қозғаушы күштің пайда болуы...",
    "изотермиялық процесс": "Изотермиялық процесс — температура тұрақты сақталатын термодинамикалық процесс...",
    "изохорлық процесс": "Изохорлық процесс — көлем тұрақты, қысым мен температура өзгеретін процесс...",
    "изобаралық процесс": "Изобаралық процесс — қысым тұрақты, көлем мен температура өзгеретін процесс...",
    "радиоактивтілік": "Радиоактивтілік — тұрақсыз атом ядроларының өздігінен ыдырап, жаңа ядролар мен бөлшектер шығару қасиеті...",
    "атом": "Атом — химиялық элементтің ең кіші бөлшегі, ядро мен электрондардан тұрады...",
    "молекула": "Молекула — заттың қасиеттерін сақтайтын ең кіші бөлшек...",
    "электрон": "Электрон — теріс зарядталған элементар бөлшек, атом ядросын айнала қозғалады...",
    "фотон": "Фотон — жарықтың және электромагниттік толқынның элементар бөлшегі...",
    "толқын": "Толқын — кеңістікте тербеліс энергиясын тасымалдайтын процесс...",
    "интерференция": "Интерференция — екі немесе бірнеше толқын қабаттасқанда, күшейтілген және әлсіреген аймақтардың пайда болуы...",
    "дифракция": "Дифракция — толқынның кедергіні айналып өтуі немесе саңылаудан өткенде бағыттарының өзгеруі...",
    "поляризация": "Поляризация — жарықтың немесе басқа толқындардың белгілі бір бағытта тербелу қасиеті...",
    "энтропия": "Энтропия — жүйенің ретсіздік дәрежесін сипаттайтын шама...",
}

FORMULAS = {
    "жылдамдық": "v = s/t",
    "кинетикалық энергия": "Ek = (mv²)/2",
    "потенциалдық энергия": "Ep = mgh немесе Ep = (k*x²)/2",
    "қысым": "P = F/S, сұйықтықта: P = ρgh",
    "тығыздық": "ρ = m/V",
    "импульс": "p = mv",
    "жұмыс": "A = F·s·cos(α), электр жұмысы: A = UIt",
    "қуат": "N = A/t, N = UI",
    "ом заңы": "I = U/R",
    "ток күші": "I = q/t",
    "кернеу": "U = A/q",
    "идеал газ теңдеуі": "pV = nRT",
    "бойль-мариотт заңы": "pV = const",
    "гей-люссак заңы": "V/T = const",
    "шарль заңы": "p/T = const",
    "жиілік": "ν = 1/T",
    "толқын ұзындығы": "λ = v/ν",
    "фотон энергиясы": "E = hν",
    "радиоактивті ыдырау": "N = N₀·e^(−λt)",
    "салыстырмалылық": "E = mc²",
}

THEORIES = {
    "ньютон заңдары": "Ньютонның үш заңы — механиканың негізі...",
    "энергия сақталу заңы": "Тұйық жүйеде энергия жойылмайды және жоқтан пайда болмайды...",
    "архимед заңы": "Сұйыққа немесе газға батырылған денеге ығыстырылған сұйықтың салмағына тең көтеруші күш әсер етеді...",
    "ом заңы": "Электр тізбегіндегі ток күші кернеуге тура, кедергіге кері пропорционал: I = U/R...",
    "термодинамиканың бірінші заңы": "Жүйеге берілген жылу оның ішкі энергиясын өзгертуге және жұмыс істеуге жұмсалады...",
    "толқындық теория": "Жарық толқын ретінде таралады. Интерференция, дифракция, поляризация — толқындық қасиеттердің дәлелі...",
    "электромагниттік индукция": "Магнит ағыны өзгергенде тұйық тізбекте электр қозғаушы күш пайда болады (Фарадей заңы)...",
    "салыстырмалылық теориясы": "Эйнштейннің салыстырмалылық теориясы — кеңістік, уақыт және масса-энергияның өзара байланысын сипаттайды...",
}

EXPERIMENTS = {
    "Архимед тәжірибесі": "Архимед тәжірибесі — сұйыққа толық батырылған денеге әсер ететін көтеруші күшті көрсету...",
    "Галилей шары тәжірибесі": "Галилей шары тәжірибесі — вакуумда әртүрлі массалы денелердің бірдей үдеумен құлауын көрсету...",
    "Фарадей индукция тәжірибесі": "Фарадей тәжірибесі — магнит өрісі өзгергенде тұйық тізбекте электр тогының пайда болуын дәлелдейді...",
    "Джоуль жылу тәжірибесі": "Джоуль тәжірибесі — механикалық энергияның жылу энергиясына айналуын көрсетеді...",
    "Юнг тәжірибесі": "Юнг тәжірибесі — жарық интерференциясын көрсетуге арналған...",
    "Эрстед тәжірибесі": "Эрстед тәжірибесі — электр тогының магнит өрісін тудыратынын көрсетеді...",
    "Ньютон маятнигі": "Ньютон маятнигі — импульс пен энергия сақталу заңдарын көрсету...",
}

HELP = {
    "Bot пайдалану нұсқаулығы": "FIzBot-ты пайдалану үшін төменгі мәзірдегі бөлімдерді таңдаңыз...",
    "Формула іздеу көмегі": "Қажетті формуланы іздеу үшін формула атауын немесе физикалық құбылысты жазыңыз...",
    "Категориялар бойынша іздеу": "Ботта барлық мәліметтер 6 негізгі категорияға бөлінген...",
    "Сұрақ қою үлгілері": "Мысал сұрақтар:\n- Архимед заңы қалай дәлелденеді?\n- Жылдамдық пен үдеу айырмашылығы неде? ...",
}

CATEGORIES = {
    "Терминдер": "Физиканың негізгі ұғымдары мен сөздіктері...",
    "Формулалар": "Физикадағы негізгі формулалар мен олардың түсіндірмесі...",
    "Теориялар": "Физикадағы басты теориялар, заңдар, олардың ашылу тарихы...",
    "Тәжрибелер": "Тарихи және классикалық ғылыми тәжірибелер...",
    "Көмек": "Ботпен жұмыс істеу, формула немесе теория іздеу, категориялар бойынша сұраныс жасау...",
}

VIDEOS = {
    "Кинетикалық энергия": "https://youtu.be/58426pBfNow?si=3xa70q_nss-twhG0",
    "Инерция және Ньютон заңдары": "https://youtu.be/MFb8F_DbGNk?si=2cXP7Dz3627eKe3T",
    "Архимед заңы": "https://youtu.be/E56HmuL2TX0?si=ipPQXUHWtcq28lgX",
    "Энергия сақталу заңы": "https://youtu.be/I1ytuqPDjMM?si=tRnQqB8P0luaBRu8",
    "Толқындар және интерференция": "https://youtu.be/9L4NOXQpk34?si=TE5_iZ3fYtFiXPuT",
    "Электр тогы және Ом заңы": "https://youtu.be/C8r5UxMWZFs?si=FBPgca4m-53eeis3",
    "Қысым және гидростатика": "https://youtu.be/OuSjiNDT-94?si=NNW2OnrXVNa-ai3-",
    "Салыстырмалылық теориясы": "https://youtu.be/njw91NOOqY8?si=83Nt-sBb9M4qR26k",
    "Фотон, жарық және толқындық қасиеттері": "https://youtu.be/BwjNRBfNfts?si=dqd089eudwcaW1l1",
    "Фарадей индукция тәжірибесі": "https://youtu.be/DSEI3N-GMHw?si=xrIjNl48cU0gyhT8",
    "Жылдамдық пен үдеу": "https://youtu.be/recc-PvfPsY?si=2ucZbjVMWU43L6d4",
    "Молекулалық-кинетикалық теория": "https://youtu.be/WsiLxwMsX1c?si=9JeZIyC6l82Qq90G"
}

QUIZZES = [
    {
        "question": "Ньютонның бірінші заңы қалай аталады?",
        "options": ["Инерция заңы", "Әрекет және қарсы әрекет заңы", "Динамика заңы"],
        "answer": 0
    },
    {
        "question": "Энергия сақталу заңы қалай тұжырымдалады?",
        "options": [
            "Энергия жойылады",
            "Энергия сақталады және тек түрленеді",
            "Энергия массамен тең"
        ],
        "answer": 1
    },
    {
        "question": "Ньютонның екінші заңы нені сипаттайды?",
        "options": ["Дене тыныштықта болады", "Күш пен үдеу арасындағы байланысты", "Әрекетке қарсы әрекет"],
        "answer": 1
    },
    {
        "question": "Ньютонның үшінші заңының мәні неде?",
        "options": ["Үдеу күшке тура пропорционал", "Дене өзінің күйін сақтайды", "Әрекетке тең және қарама-қарсы әрекет болады"],
        "answer": 2
    },
    {
        "question": "Инерция дегеніміз не?",
        "options": ["Дененің массасы", "Дененің қозғалысқа қарсыласуы", "Қысым"],
        "answer": 1
    },
    {
        "question": "Күштің өлшем бірлігі қандай?",
        "options": ["Джоуль", "Ньютон", "Ватт"],
        "answer": 1
    },
    {
        "question": "Денеге әрекет ететін күштер теңгерілген болса, дене неістейді?",
        "options": ["Қозғалысын өзгертеді", "Үдей қозғалады", "Жылдамдығын өзгертпей қозғалады немесе тыныштықта болады"],
        "answer": 2
    },
    {
        "question": "Масса нені сипаттайды?",
        "options": ["Дененің көлемін", "Дененің салмағын", "Инерция шамасын"],
        "answer": 2
    },
    {
        "question": "Гравитациялық күш неге тәуелді?",
        "options": ["Денелердің массасына және арақашықтығына", "Тек жылдамдыққа", "Температураға"],
        "answer": 0
    },
    {
        "question": "Үдеу мен масса арасындағы байланыс қандай?",
        "options": ["Тікелей пропорционал", "Кері пропорционал", "Байланыс жоқ"],
        "answer": 1
    },
    {
        "question": "1 Ньютон күш неге тең?",
        "options": ["1 кг/м²", "1 кг·м/с²", "1 м/с²"],
        "answer": 1
    }
]

RESOURCES = {
    "Кітаптар": [
        "1. Р. Фейнман. Фейнман лекциялары по физике.",
        "2. Д. Халидей, Р. Резник, К. Уокер. Физика.",
        "3. Л.Д. Ландау, Е.М. Лифшиц. Теоретическая физика."
    ],
    "Сайты": [
        "https://www.khanacademy.org/science/physics",
        "https://phys.org/",
        "https://www.fizmat.kz/"
    ],
    "Онлайн-курстар": [
        "Coursera: https://www.coursera.org/courses?query=physics",
        "edX: https://www.edx.org/learn/physics",
        "Stepik: https://stepik.org/catalog/search?query=физика"
    ]
}

# Глобальные переменные
USER_DATA = {}
FEEDBACK = 1

# Создание приложения Telegram
application = None

def main_keyboard():
    keyboard = [
        [InlineKeyboardButton("📚 Терминдер", callback_data='terms')],
        [InlineKeyboardButton("🔬 Теориялар", callback_data='theories')],
        [InlineKeyboardButton("📐 Формулалар", callback_data='formulas')],
        [InlineKeyboardButton("🧪 Тәжрибелер", callback_data='experiments')],
        [InlineKeyboardButton("🎬 Бейнелер", callback_data='videos')],
        [InlineKeyboardButton("📝 Квиз/Тест", callback_data='quiz')],
        [InlineKeyboardButton("📚 Ресурстар", callback_data='resources')],
        [InlineKeyboardButton("🌐 Wikipedia/Wolfram", callback_data='external')],
        [InlineKeyboardButton("✉️ Обратная связь", callback_data='feedback')],
        [InlineKeyboardButton("👤 Кабинет/Прогресс", callback_data='profile')],
        [InlineKeyboardButton("🗂 Категориялар", callback_data='categories')],
        [InlineKeyboardButton("🆘 Көмек", callback_data='help')],
        [InlineKeyboardButton("❓ Сұрақ қою", callback_data='ask')]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Артқа", callback_data='back')]])

async def show_main_menu(update, context):
    if update.callback_query:
        await update.callback_query.edit_message_text(
            "Сәлем! Мен FIzBot — физика бойынша көмекшіңізмін. Төменнен бөлімді таңдаңыз:",
            reply_markup=main_keyboard()
        )
    else:
        await update.message.reply_text(
            "Сәлем! Мен FIzBot — физика бойынша көмекшіңізмін. Төменнен бөлімді таңдаңыз:",
            reply_markup=main_keyboard()
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update, context)

async def quiz_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    index = USER_DATA.get(user_id, {}).get("quiz_index", 0)
    if index >= len(QUIZZES):
        await update.callback_query.edit_message_text(
            "Квиз аяқталды! Дұрыс жауаптар саны: {}\n\n".format(
                USER_DATA[user_id].get("quiz_score", 0)
            ),
            reply_markup=back_keyboard()
        )
        return
    q = QUIZZES[index]
    keyboard = [
        [InlineKeyboardButton(opt, callback_data=f'quiz_answer_{i}')] for i, opt in enumerate(q["options"])
    ]
    await update.callback_query.edit_message_text(
        q["question"],
        reply_markup=InlineKeyboardMarkup(keyboard + [[InlineKeyboardButton("🔙 Артқа", callback_data='back')]])
    )

async def handle_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    index = USER_DATA.get(user_id, {}).get("quiz_index", 0)
    answer = int(query.data.split("_")[-1])
    correct = QUIZZES[index]["answer"]
    score = USER_DATA.get(user_id, {}).get("quiz_score", 0)
    if answer == correct:
        result = "✅ Дұрыс!"
        score += 1
    else:
        result = "❌ Қате! Дұрыс жауап: {}".format(QUIZZES[index]["options"][correct])
    USER_DATA.setdefault(user_id, {})["quiz_score"] = score
    USER_DATA[user_id]["quiz_index"] = index + 1
    await query.edit_message_text(result, reply_markup=back_keyboard())
    await quiz_handler(update, context)

async def resources_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "<b>Пайдалы ресурстар:</b>\n\n"
    for section, lst in RESOURCES.items():
        text += f"<b>{section}:</b>\n"
        text += "\n".join(lst) + "\n\n"
    await update.callback_query.edit_message_text(text, parse_mode="HTML", reply_markup=back_keyboard())

async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    quiz_score = USER_DATA.get(user_id, {}).get("quiz_score", 0)
    quiz_index = USER_DATA.get(user_id, {}).get("quiz_index", 0)
    history = USER_DATA.get(user_id, {}).get("history", [])
    bookmarks = USER_DATA.get(user_id, {}).get("bookmarks", [])
    text = (
        f"👤 <b>Сіздің кабинетіңіз:</b>\n"
        f"📝 Квиз нәтижесі: {quiz_score} дұрыс жауап (барлығы {len(QUIZZES)} сұрақ)\n"
        f"⭐️ Сақталған сұраныстар: {len(bookmarks)}\n"
        f"📜 Сұраныстар тарихы (соңғы 5):\n" +
        ("\n".join(history[-5:]) if history else "Жоқ")
    )
    await update.callback_query.edit_message_text(text, parse_mode="HTML", reply_markup=back_keyboard())

async def feedback_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(
        "✉️ Өз ұсынысыңызды, сұрағыңызды немесе шағымыңызды жазыңыз. Сообщение будет передано разработчику.",
        reply_markup=back_keyboard()
    )
    return FEEDBACK

async def feedback_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"Feedback from {user.username} ({user.id}): {update.message.text}")
    await update.message.reply_text("✅ Спасибо! Ваше сообщение отправлено разработчику.", reply_markup=back_keyboard())
    return ConversationHandler.END

async def external_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(
        "🌐 Поиск по Wikipedia. Введите ваш физический вопрос или термин:"
        "\n\nПример: масса электрона, закон Архимеда, энергия фотона и т.п.",
        reply_markup=back_keyboard()
    )
    context.user_data["external"] = True

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'terms':
        text = "Терминдер тізімі:\n" + "\n".join([f"- {t}" for t in TERMS])
        await query.edit_message_text(text, reply_markup=back_keyboard())
    elif query.data == 'theories':
        text = "Теориялар тізімі:\n" + "\n".join([f"- {t}" for t in THEORIES])
        await query.edit_message_text(text, reply_markup=back_keyboard())
    elif query.data == 'formulas':
        text = "Формулалар тізімі:\n" + "\n".join([f"- {t}" for t in FORMULAS])
        await query.edit_message_text(text, reply_markup=back_keyboard())
    elif query.data == 'experiments':
        text = "Тәжрибелер тізімі:\n" + "\n".join([f"- {t}" for t in EXPERIMENTS])
        await query.edit_message_text(text, reply_markup=back_keyboard())
    elif query.data == 'videos':
        text = "🎬 Физика бейнелері мен анимациялар:\n\n"
        for name, url in VIDEOS.items():
            text += f"▪️ <a href=\"{url}\">{name}</a>\n"
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=back_keyboard(), disable_web_page_preview=False)
    elif query.data == 'help':
        text = "Көмек бөлімдері:\n" + "\n".join([f"- {t}" for t in HELP])
        await query.edit_message_text(text, reply_markup=back_keyboard())
    elif query.data == 'categories':
        text = "Категориялар:\n" + "\n".join([f"- {name}: {desc}" for name, desc in CATEGORIES.items()])
        await query.edit_message_text(text, reply_markup=back_keyboard())
    elif query.data == 'quiz':
        user_id = update.effective_user.id
        USER_DATA.setdefault(user_id, {})["quiz_index"] = 0
        USER_DATA[user_id]["quiz_score"] = 0
        await quiz_handler(update, context)
    elif query.data.startswith('quiz_answer_'):
        await handle_quiz_answer(update, context)
    elif query.data == 'resources':
        await resources_handler(update, context)
    elif query.data == 'profile':
        await profile_handler(update, context)
    elif query.data == 'feedback':
        await feedback_start(update, context)
    elif query.data == 'external':
        await external_handler(update, context)
    elif query.data == 'ask':
        await query.edit_message_text(
            "❓ Сұрағыңызды жазыңыз. Мен физика бойынша көмектесуге дайынмын!",
            reply_markup=back_keyboard()
        )
        context.user_data["ask_mode"] = True
    elif query.data == 'back':
        await show_main_menu(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.lower()
    
    # Сохраняем историю запросов
    USER_DATA.setdefault(user_id, {}).setdefault("history", []).append(text)
    
    # Обработка внешнего поиска
    if context.user_data.get("external"):
        context.user_data["external"] = False
        try:
            # Простой поиск в Wikipedia API
            wiki_url = f"https://ru.wikipedia.org/api/rest_v1/page/summary/{text.replace(' ', '%20')}"
            response = requests.get(wiki_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                summary = data.get('extract', 'Информация не найдена')
                await update.message.reply_text(
                    f"🌐 <b>Wikipedia результат:</b>\n\n{summary[:800]}...\n\n"
                    f"<a href=\"{data.get('content_urls', {}).get('desktop', {}).get('page', '')}\">Толық мақала</a>",
                    parse_mode="HTML",
                    reply_markup=back_keyboard()
                )
            else:
                await update.message.reply_text(
                    "❌ Wikipedia-дан мәлімет табылмады. Басқа термин көрсетіңіз.",
                    reply_markup=back_keyboard()
                )
        except Exception as e:
            logger.error(f"Wikipedia search error: {e}")
            await update.message.reply_text(
                "❌ Іздеу кезінде қате орын алды.",
                reply_markup=back_keyboard()
            )
        return
    
    # Поиск по базе знаний
    found_results = []
    
    # Поиск в терминах
    for term, definition in TERMS.items():
        if term in text or any(word in term.lower() for word in text.split()):
            found_results.append(f"📚 <b>{term.title()}:</b>\n{definition}")
    
    # Поиск в формулах
    for formula_name, formula in FORMULAS.items():
        if formula_name in text or any(word in formula_name.lower() for word in text.split()):
            found_results.append(f"📐 <b>{formula_name.title()}:</b>\n{formula}")
    
    # Поиск в теориях
    for theory, description in THEORIES.items():
        if theory in text or any(word in theory.lower() for word in text.split()):
            found_results.append(f"🔬 <b>{theory.title()}:</b>\n{description}")
    
    # Поиск в экспериментах
    for experiment, description in EXPERIMENTS.items():
        if experiment in text or any(word in experiment.lower() for word in text.split()):
            found_results.append(f"🧪 <b>{experiment.title()}:</b>\n{description}")
    
    if found_results:
        # Показываем первые 3 результата
        response_text = "🔍 <b>Табылған нәтижелер:</b>\n\n" + "\n\n".join(found_results[:3])
        if len(found_results) > 3:
            response_text += f"\n\n<i>Тағы {len(found_results) - 3} нәтиже табылды...</i>"
        
        # Добавляем закладку
        bookmark_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⭐ Сақтау", callback_data=f'bookmark_{text}')],
            [InlineKeyboardButton("🔙 Артқа", callback_data='back')]
        ])
        
        await update.message.reply_text(
            response_text, 
            parse_mode="HTML", 
            reply_markup=bookmark_keyboard
        )
    else:
        # Предлагаем похожие запросы
        suggestions = []
        all_terms = list(TERMS.keys()) + list(FORMULAS.keys()) + list(THEORIES.keys())
        
        for term in all_terms[:5]:  # Показываем первые 5 похожих
            if any(word in term.lower() for word in text.split()) or any(word in text for word in term.split()):
                suggestions.append(term)
        
        if suggestions:
            suggestion_text = "❓ Мүмкін, сіз мынаны іздеп жүрсіз:\n\n" + "\n".join([f"• {s}" for s in suggestions])
        else:
            suggestion_text = "❌ Өкінішке орай, сұрағыңыз бойынша ештеңе табылмады.\n\nБасқа терминдерді қолданып көріңіз немесе мәзірден таңдаңыз."
        
        await update.message.reply_text(
            suggestion_text,
            reply_markup=back_keyboard()
        )

async def handle_bookmark(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    bookmark_text = query.data.replace('bookmark_', '')
    
    USER_DATA.setdefault(user_id, {}).setdefault("bookmarks", []).append(bookmark_text)
    await query.answer("⭐ Сақталды!")

# Webhook обработчик
@app.route('/webhook', methods=['POST'])
async def webhook():
    try:
        json_data = request.get_json()
        if json_data:
            update = Update.de_json(json_data, application.bot)
            await application.process_update(update)
        return jsonify({'status': 'ok'})
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Установка webhook
@app.route('/set_webhook', methods=['GET'])
async def set_webhook():
    try:
        webhook_url = f"{WEBHOOK_URL}/webhook"
        await application.bot.set_webhook(webhook_url)
        return f"Webhook установлен: {webhook_url}"
    except Exception as e:
        return f"Ошибка установки webhook: {e}", 500

# Главная страница
@app.route('/')
def index():
    return "FIzBot работает! 🤖"

# Создание и настройка приложения
async def create_application():
    global application
    application = Application.builder().token(TOKEN).build()
    
    # Обработчик обратной связи
    feedback_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(feedback_start, pattern='^feedback')],
        states={
            FEEDBACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, feedback_receive)]
        },
        fallbacks=[CommandHandler('cancel', show_main_menu)]
    )
                                           
# Запуск приложения
if __name__ == '__main__':
    import asyncio
    import sys
    
    async def main():
        await create_application()
        
if __name__ == '__main__':
    import asyncio
    import sys
    
    async def main():
        await create_application()
        
        if len(sys.argv) > 1 and sys.argv[1] == 'local':
            print("Запуск в режиме polling...")
            await application.run_polling()
    
    # Для продакшена
    if len(sys.argv) <= 1 or sys.argv[1] != 'local':
        asyncio.run(create_application())
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        asyncio.run(main())
    
    # Для синхронного запуска Flask в продакшене
    if len(sys.argv) <= 1 or sys.argv[1] != 'local':
        asyncio.run(create_application())
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        asyncio.run(main())
        states={
            FEEDBACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, feedback_receive)]
        },
        fallbacks=[CommandHandler('cancel', show_main_menu)]
    
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CallbackQueryHandler(handle_bookmark, pattern='^bookmark_'))
    application.add_handler(feedback_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Инициализация приложения
asyncio.run(application.initialize())
def some_function():
    # код функции
    return application  # здесь return разрешен
# Запуск приложения
if __name__ == '__main__':
    import asyncio
    import sys
    
    async def main():
        await create_application()
        
        if len(sys.argv) > 1 and sys.argv[1] == 'local':
            print("Запуск в режиме polling...")
            await application.run_polling()
    
    # Для синхронного запуска Flask в продакшене
    if len(sys.argv) <= 1 or sys.argv[1] != 'local':
        asyncio.run(create_application())
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        asyncio.run(main())