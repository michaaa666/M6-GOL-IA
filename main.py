import telebot

TOKEN = "8686894438:AAGmzCI2Av0jpATPGWM42UyRxvgRB2G8MVQ"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "¡Bienvenido apostador! M6-GOL-IA está en línea y operando 24/7.")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    bot.reply_to(message, "Mensaje recibido. Procesando datos de apuestas...")

if __name__ == "__main__":
    print("Iniciando bot de Telegram...")
    bot.infinity_polling()


