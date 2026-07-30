import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
import requests

TOKEN = "8686894438:AAGmzCI2Av0jpATPGWM42UyRxvgRB2G8MVQ"
bot = telebot.TeleBot(TOKEN)

API_KEY = "44cce749a8msh1eeac7591aba73fp1212dbjsn510a23c7d8fd"
API_HOST = "apifootball3.p.rapidapi.com"

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
            url = f"https://{API_HOST}/"
            querystring = {"action": "get_events", "match_live": "1"}
            headers = {
                "x-rapidapi-key": API_KEY,
                "x-rapidapi-host": API_HOST
            }
            response = requests.get(url, headers=headers, params=querystring)
            data = response.json()
            
            if isinstance(data, dict):
                data = data.get("result", data.get("response", []))
            
            if not data or not isinstance(data, list):
                bot.send_message(call.message.chat.id, "⚽ **Partidos en Vivo:**\nNo hay partidos jugándose en este momento.")
            else:
                texto = "⚽ **Partidos en Vivo (En directo):**\n"
                for match in data[:5]:
                    home = match.get("match_hometeam_name", "Local")
                    away = match.get("match_awayteam_name", "Visitante")
                    score_home = match.get("match_live_home_score", "0")
                    score_away = match.get("match_live_away_score", "0")
                    texto += f"• {home} {score_home} - {score_away} {away}\n"
                bot.send_message(call.message.chat.id, texto)
        except Exception as e:
            bot.send_message(call.message.chat.id, "⚠️ Error al conectar con la API deportiva.")

    elif call.data == "leagues":
        bot.answer_callback_query(call.id, "Cargando ligas...")
        bot.send_message(call.message.chat.id, "🏆 **Ligas disponibles:**\n1. Liga MX\n2. La Liga\n3. Premier League")
    elif call.data == "analyze_bet":
        bot.answer_callback_query(call.id, "Listo para análisis...")
        bot.send_message(call.message.chat.id, "📊 Envía el nombre del equipo que deseas analizar (ej: Real Madrid, Barcelona, America).")
    elif call.data == "settings":
        bot.answer_callback_query(call.id, "Configuración")
        bot.send_message(call.message.chat.id, "⚙️ Sistema operando 24/7 en la nube.")

@bot.message_handler(func=lambda message: True)
def handle_team_search(message):
    team_name = message.text.strip()
    bot.reply_to(message, f"🔍 Buscando información para: **{team_name}**...", parse_mode="Markdown")
    try:
        url = f"https://{API_HOST}/"
        headers = {
            "x-rapidapi-key": API_KEY,
            "x-rapidapi-host": API_HOST
        }
        
        querystring = {"action": "get_teams", "team_name": team_name}
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
        
        if isinstance(data, dict):
            data = data.get("result", data.get("response", []))
        
        if not data or not isinstance(data, list) or len(data) == 0:
            querystring = {"action": "get_teams", "search": team_name}
            response = requests.get(url, headers=headers, params=querystring)
            data = response.json()
            if isinstance(data, dict):
                data = data.get("result", data.get("response", []))
        
        if not data or not isinstance(data, list) or len(data) == 0:
            bot.send_message(message.chat.id, f"❌ No se encontró información para '{team_name}'. Prueba escribiendo el nombre completo.")
        else:
            team = data[0]
            t_name = team.get("team_name", "Desconocido")
            t_country = team.get("country_name", "No especificado")
            t_founded = team.get("team_founded", "N/D")
            t_logo = team.get("team_badge", "")
            
            texto = f"📊 **Análisis de Equipo**\n\n"
            texto += f"🛡️ **Equipo:** {t_name}\n"
            texto += f"🌍 **País:** {t_country}\n"
            texto += f"📅 **Fundación:** {t_founded}\n"
            if t_logo:
                texto += f"🔗 [Ver Escudo Oficial]({t_logo})\n"
            
            bot.send_message(message.chat.id, texto, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, "⚠️ Ocurrió un error al procesar el análisis del equipo.")

if __name__ == "__main__":
    print("Iniciando bot M6-GOL-IA con parseo robusto...")
    bot.infinity_polling()

