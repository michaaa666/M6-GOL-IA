import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
import requests

TOKEN = "8686894438:AAGmzCI2Av0jpATPGWM42UyRxvgRB2G8MVQ"
bot = telebot.TeleBot(TOKEN)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"M6-GOL-IA Bot is running 24/7!")

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

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
        bot.answer_callback_query(call.id, "Consultando partidos en vivo...")
        try:
            url = "https://v3.football.api-sports.io/fixtures?live=all"
            headers = {
                "x-rapidapi-key": "TU_API_KEY_AQUI",
                "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
            }
            response = requests.get(url, headers=headers)
            data = response.json()
            
            matches = data.get("response", [])
            if not matches:
                bot.send_message(call.message.chat.id, "⚽ **Partidos en Vivo:**\nNo hay partidos jugándose en este momento.")
            else:
                texto = "⚽ **Partidos en Vivo (En directo):**\n"
                for match in matches[:5]:
                    home = match["teams"]["home"]["name"]
                    away = match["teams"]["away"]["name"]
                    goals_home = match["goals"]["home"]
                    goals_away = match["goals"]["away"]
                    texto += f"• {home} {goals_home} - {goals_away} {away}\n"
                bot.send_message(call.message.chat.id, texto)
        except Exception as e:
            bot.send_message(call.message.chat.id, "⚠️ Error al conectar con la API deportiva.")

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
    print("Iniciando bot M6-GOL-IA con soporte para API...")
    bot.infinity_polling()

