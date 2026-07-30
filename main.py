import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot

TOKEN = "8686894438:AAGmzCI2Av0jpATPGWM42UyRxvgRB2G8MVQ"
bot = telebot.TeleBot(TOKEN)

# Servidor HTTP temporal para que Render detecte el puerto abierto
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"M6-GOL-IA Bot is running 24/7!")

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# Iniciar el servidor web en un hilo paralelo
threading.Thread(target=run_http_server, daemon=True).start()

@bot.message_handler(commands=['start', 'menu'])
def send_welcome_and_menu(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        telebot.types.InlineKeyboardButton("⚽ Partidos en Vivo", callback_data="live_matches"),
        telebot.types.InlineKeyboardButton("🏆 Ligas Destacadas", callback_data="leagues"),
        telebot.types.InlineKeyboardButton("📊 Analizar Apuesta", callback_data="analyze_bet"),
        telebot.types.InlineKeyboardButton("⚙️ Configuración", callback_data="settings")
    )
    
    bot.reply_to(
        message, 
        "¡Bienvenido apostador! M6-GOL-IA está en línea y operando 24/7.\n\n⚽ **Panel Principal**\nSelecciona una opción del menú de apuestas:", 
        reply_markup=markup, 
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "live_matches":
        bot.answer_callback_query(call.id, "Cargando partidos...")
        bot.send_message(call.message.chat.id, "⚽ **Partidos en Vivo:**\n• Sincronizando datos de los próximos encuentros...")
    elif call.data == "leagues":
        bot.answer_callback_query(call.id, "Cargando ligas...")
        bot.send_message(call.message.chat.id, "🏆 **Ligas disponibles:**\n1. Liga MX\n2. La Liga\n3. Premier League")
    elif call.data == "analyze_bet":
        bot.answer_callback_query(call.id, "Listo para análisis...")
        bot.send_message(call.message.chat.id, "📊 Envía el nombre del partido o equipo que deseas consultar.")
    elif call.data == "settings":
        bot.answer_callback_query(call.id, "Configuración")
        bot.send_message(call.message.chat.id, "⚙️ Sistema operando 24/7 en la nube.")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    bot.reply_to(message, "Mensaje recibido. Procesando datos de apuestas...")

if __name__ == "__main__":
    print("Iniciando bot M6-GOL-IA con bienvenida y menú...")
    bot.infinity_polling()



