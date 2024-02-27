import telebot
from telebot.types import (ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup,
                           InlineKeyboardButton)
import logging
import config
import time
from gpt import generate_story
from data import save_user_data, record_user_data, load_user_data

token = config.BOT_TOKEN
bot = telebot.TeleBot(token)

image_addresses = config.image_addresses

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.txt", filemode="w",
)


@bot.message_handler(commands=["start"])
def start_command(message):
    user_name = message.from_user.first_name
    messages_for_user = (f"Хаюшки {user_name}! Тебе говорит привет тот самый зелёный. Я тебе сегодня готов помочь! "
                         f"Выбери тут варик. Мой рекомендасьён падает на инструкцию, если ты впервые "
                         f"ко мне зашёл.")
    bot.send_photo(message.chat.id, image_addresses["Картинки"]["1"], messages_for_user,
                   reply_markup=create_replymarkup(["📚Почитать состав освежителя", "НАЧИНАЕМ!",
                                                    "🤖Бумажка обо мне"]))


@bot.message_handler(commands=["help"])
def help_command(message):
    message_text = message.text
    if message_text == "/help":
        bot.send_message(message.chat.id, "Клавиатурные кнопки были убраны", reply_markup=ReplyKeyboardRemove())
    bot.send_message(message.chat.id, "Инструкция по использованию репликона:\n\n"
                                      "Во-первых, ты теперь пацан! Поэтому есть два варика со мной базарить: "
                                      "First - это использование команд, способ прикольный, но неуден для "
                                      "чушпанов, так как ДУМАТЬ НАДО ;) "
                                      "Ты можешь найти список команд слева от поля ввода текста, в меню. И второй "
                                      "способ - всплывающие жмакалки. К некоторым ПИСЬМАМ "
                                      "будут прикреплены жмакалки с ответами, нужно лишь нажмать на них. "
                                      "Этот метод кайфовый, но менее прошаренный. Выберите, что к душе лежит "
                                      "из методов на свой вкус.\n\n Когда ты черкаешь /solve_task или жмакаешь "
                                      "жмакалку «НАЧИНАЕМ!» - я попрошу тебя прислать мне запрос, то есть,"
                                      "текст из которого я пойму чего те надобно. После того как "
                                      "ты отправишь запрос, тебе трэба будет подождать некоторое время, обычно это "
                                      "занимает около 3-5 минут. Через некоторое время я закину тебе твой "
                                      "ответ;\n— Команда /continue или жмакалка «Продолжить» - нужна в тех случаях, "
                                      "когда я не дописал ответ. Если ты хочешь, чтобы я завершил ответ до "
                                      "конца, то тыкай эту команду или жми кнопку.\n— Команда /end_dialog или "
                                      "кнопка «Завершить» - завершает диалог с ботом, и он забывает ваши предыдущие "
                                      "сообщения.\n— Команда /reset или кнопка «Перезапустить гнома» - перезапускает "
                                      "меня и возвращает тебя к началу.")


@bot.message_handler(commands=["about"])
def about_command(message):
    message_text = message.text
    if message_text == "/about":
        bot.send_message(message.chat.id, "Жмакалки были убраны", reply_markup=ReplyKeyboardRemove())
    bot.send_message(message.chat.id, "Описание бота:\n\n— Этот домашний репликон для помощи во всяких "
                                      "ситуациях. Благодаря своим возможностям, зелёный может написать историю "
                                      "основываясь на ваших пожеланиях и идеях. Он может предложить свои варианты "
                                      "развития сюжета, персонажей и идей. Так же может дать ответ на прочие вопросики")


@bot.message_handler(commands=['debug'])
def send_logs(message):
    with open("log_file.txt", "rb") as f:
        bot.send_document(message.chat.id, f)


def create_replymarkup(button_labels):
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for label in button_labels:
        markup.add(KeyboardButton(label))
    return markup


def create_inlinemarkup(button_labels):
    markup = InlineKeyboardMarkup()
    for label in button_labels:
        markup.add(InlineKeyboardButton(label, callback_data=label))
    return markup


@bot.message_handler(commands=['end_dialog'])
@bot.callback_query_handler(func=lambda call: call.data == 'Завершить')
def end_dialog(message):
    user_id = str(message.from_user.id)
    user_data = load_user_data()
    user_info = user_data.get(user_id, {})
    record_user_data(message)
    if isinstance(message, telebot.types.CallbackQuery):
        message = message.message
        pass
    if user_id not in user_data or user_info["progress"] == "user_first_response":
        bot.send_message(message.chat.id, "А ты сначала сообщение напиши ;)")
        bot.register_next_step_handler(message, get_promt)
        return
    answer = generate_story("Завершить")
    if isinstance(answer, str):
        bot.send_message(message.chat.id, answer)

    else:
        bot.send_message(message.chat.id, f"Произошла ошибка: {answer}")
    return


@bot.message_handler(commands=['continue'])
@bot.callback_query_handler(func=lambda call: call.data == 'Продолжить')
def continue_commands(message):
    user_id = str(message.from_user.id)
    user_data = load_user_data()
    user_info = user_data.get(user_id, {})
    record_user_data(message)
    if user_id not in user_data or user_info["progress"] == "user_first_response":
        bot.send_message(message.chat.id, "Введи свой запрос")
        bot.register_next_step_handler(message, get_promt)
        return
    if isinstance(message, telebot.types.CallbackQuery):
        message = message.message
        pass
    bot.send_message(message.chat.id, "Над этой задачкой работают наши репликоны."
                                      "За ожидание начислим 5 бонусов спасибо!"
                     )
    answer = generate_story("Продолжить")
    if isinstance(answer, str):
        bot.send_message(message.chat.id, "Ля, что получилось:")
        time.sleep(1)
        bot.send_message(message.chat.id, answer, reply_markup=create_inlinemarkup(["Продолжить", "Завершить",
                                                                                    "Перезапустить бота"]))
    else:
        bot.send_message(message.chat.id, f"Произошла ошибка: {answer}")
    bot.register_next_step_handler(message, get_promt)


@bot.message_handler(commands=["reset"])
@bot.callback_query_handler(func=lambda call: call.data == 'Перезапустить главного репликона')
def reset_command(message):
    record_user_data(message)
    if isinstance(message, telebot.types.CallbackQuery):
        message = message.message
        pass
    bot.send_message(message.chat.id, "перезагрузка зелёного . . .", reply_markup=ReplyKeyboardRemove())
    time.sleep(3)
    start_command(message)


@bot.message_handler(commands=["solve_task"])
def solve_task_command(message):
    bot.send_message(message.chat.id, "Начеркай свой запрос:")
    bot.register_next_step_handler(message, get_promt)


@bot.message_handler(content_types=["text"])
def user_first_response(message):
    message_text = message.text
    if message_text == "📚Почитать состав освежителя":
        help_command(message)
        bot.send_message(message.chat.id, "Почитай и затем жмакай на тыкалку",
                         reply_markup=create_replymarkup(["Прочёл_ла состав и готов_а к запуску!"]))
    elif message_text == "🤖Бумажка обо мне":
        about_command(message)
        bot.send_message(message.chat.id, "Бумажка обо мне",
                         reply_markup=create_replymarkup(["Прочитал_а и готов_а!"]))
    elif message_text == "Пропустить всякие бумажки и начать":
        bot.send_message(message.chat.id, "Супер!")
        time.sleep(1)
        bot.send_message(message.chat.id, "Напишите свой запросик:")
    else:
        bot.send_message(message.chat.id, "Я не понял вашего действия, выберите жмакалку на которую можно тыкнуть")
        return
    record_user_data(message)
    bot.register_next_step_handler(message, get_promt)


def get_promt(message):
    message_text = message.text
    user_id = str(message.from_user.id)
    user_data = load_user_data()
    user_info = user_data.get(user_id, {})
    if message_text in ["Прочёл_ла состав и готов_а к запуску!", "Прочитал_а и готов_а!"]:
        bot.send_message(message.chat.id, "Напишите свой запрос:")
        bot.register_next_step_handler(message, get_promt)
        return
    if message.content_type != "text":
        bot.send_message(message.chat.id, "А ну-ка пиши по русски!")
        bot.register_next_step_handler(message, get_promt)
        return
    user_info["progress"] = "get_promt"
    save_user_data(user_data)
    user_promt = message_text
    bot.send_message(message.chat.id, "Над рассказом пашут репликоны. За ожидание дадим 5 бонусов спасибо!", )
    answer = generate_story(user_promt)
    if isinstance(answer, str):
        bot.send_message(message.chat.id, "Лови ответ!")
        time.sleep(1)
        bot.send_message(message.chat.id, answer, reply_markup=create_inlinemarkup(["Продолжить", "Завершить",
                                                                                    "Перезапустить зелёного"]))
    else:
        bot.send_message(message.chat.id, f"Произошла ошибка: {answer}")
    if user_info["progress"] != "get_promt":
        bot.register_next_step_handler(message, get_promt)
        return


bot.polling(timeout=60)
