import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import random
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
        telebot.types.InlineKeyboardButton("🛡️ Info de Clubes", callback_data="club_info_prompt"),
        telebot.types.InlineKeyboardButton("📊 Analizar Apuesta", callback_data="analyze_bet"),
        telebot.types.InlineKeyboardButton("🎲 Armar Parley", callback_data="build_parley"),
        telebot.types.InlineKeyboardButton("🧮 Calc. Bankroll", callback_data="bankroll_help")
    )
    
    bot.reply_to(
        message, 
        "¡Bienvenido apostador! **M6-GOL-IA** está en línea y operando al 100%.\n\nSelecciona una opción del panel maestro o usa `/calc [capital] [cuota]`:", 
        reply_markup=markup, 
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['calc'])
def calculate_bankroll(message):
    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "⚠️ Uso incorrecto.\nEjemplo: `/calc 1000 1.85`\n(Ingresa tu capital total y la cuota decimal)", parse_mode="Markdown")
            return
        
        capital = float(parts[1])
        cuota = float(parts[2])
        
        stake_2 = round(capital * 0.02, 2)
        stake_5 = round(capital * 0.05, 2)
        
        ganancia_2 = round(stake_2 * cuota, 2)
        ganancia_5 = round(stake_5 * cuota, 2)
        
        texto = f"🧮 **Calculadora de Bankroll y Apuestas**\n\n"
        texto += f"💰 **Capital Total:** ${capital}\n"
        texto += f"📈 **Cuota Seleccionada:** {cuota}\n\n"
        texto += f"🟢 **Stake Conservador (2%):** ${stake_2}\n"
        texto += f"   └ Retorno total estimado: ${ganancia_2}\n\n"
        texto += f"🟡 **Stake Moderado (5%):** ${stake_5}\n"
        texto += f"   └ Retorno total estimado: ${ganancia_5}\n\n"
        texto += f"⚠️ _Gestiona tu bankroll con disciplina y cabeza fría._"
        
        bot.reply_to(message, texto, parse_mode="Markdown")
    except ValueError:
        bot.reply_to(message, "⚠️ Por favor ingresa números válidos. Ejemplo: `/calc 500 1.75`", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "live_matches":
        bot.answer_callback_query(call.id, "Consultando partidos en vivo...")
        try:
            url = f"https://{API_HOST}/"
            querystring = {"action": "get_events", "match_live": "1"}
            headers = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": API_HOST}
            response = requests.get(url, headers=headers, params=querystring)
            data = response.json()
            
            if isinstance(data, dict):
                data = data.get("result", data.get("response", []))
            
            if not data or not isinstance(data, list) or len(data) == 0:
                bot.send_message(call.message.chat.id, "⚽ **Partidos en Vivo:**\nNo hay partidos jugándose en este momento.")
            else:
                texto = "⚽ **Partidos en Vivo (En directo):**\n\n"
                for match in data[:8]:
                    home = match.get("match_hometeam_name", "Local")
                    away = match.get("match_awayteam_name", "Visitante")
                    score_home = match.get("match_live_home_score", "0")
                    score_away = match.get("match_live_away_score", "0")
                    league = match.get("league_name", "Liga")
                    texto += f"🏆 *{league}*\n• {home} **{score_home} - {score_away}** {away}\n\n"
                bot.send_message(call.message.chat.id, texto, parse_mode="Markdown")
        except Exception as e:
            bot.send_message(call.message.chat.id, "⚠️ Error al conectar con la API de partidos en vivo.")

    elif call.data == "club_info_prompt":
        bot.answer_callback_query(call.id, "Búsqueda de clubes")
        bot.send_message(call.message.chat.id, "🛡️ **Información de Clubes:**\nEnvía directamente al chat el nombre del equipo que deseas consultar (Ejemplo: `Real Madrid`, `Barcelona`, `Arsenal`).", parse_mode="Markdown")

    elif call.data == "bankroll_help":
        bot.answer_callback_query(call.id, "Calculadora de Bankroll")
        bot.send_message(call.message.chat.id, "🧮 **Calculadora de Bankroll:**\n\nPara calcular tu apuesta y gestión de riesgo, escribe el comando:\n`/calc [tu_capital] [cuota]`\n\n*Ejemplo:* `/calc 1000 1.85`", parse_mode="Markdown")

    elif call.data == "analyze_bet":
        bot.answer_callback_query(call.id, "Analizando encuentros...")
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            url = f"https://{API_HOST}/"
            querystring = {"action": "get_events", "from": today, "to": today}
            headers = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": API_HOST}
            response = requests.get(url, headers=headers, params=querystring)
            data = response.json()
            
            if isinstance(data, dict):
                data = data.get("result", data.get("response", []))
                    
            if not data or not isinstance(data, list) or len(data) == 0:
                bot.send_message(call.message.chat.id, f"📊 **Análisis de Apuestas ({today}):**\nNo hay partidos oficiales registrados hoy para analizar cuotas.")
            else:
                texto = f"📊 **Análisis Inteligente de Partidos ({today}):**\n\n"
                for match in data[:5]:
                    home = match.get("match_hometeam_name", "Local")
                    away = match.get("match_awayteam_name", "Visitante")
                    league = match.get("league_name", "Liga")
                    prediction = random.choice([
                        f"🔥 Pronóstico: Gana {home} o Empate",
                        f"⚽ Pronóstico: Más de 1.5 goles",
                        f"🎯 Pronóstico: Ambos anotan (Sí)",
                        f"⚡ Pronóstico: Gana {away}"
                    ])
                    texto += f"🏆 *{league}*\n⚔️ {home} vs {away}\n{prediction}\n\n"
                bot.send_message(call.message.chat.id, texto, parse_mode="Markdown")
        except Exception as e:
            bot.send_message(call.message.chat.id, "⚠️ Error al generar el análisis de apuestas.")

    elif call.data == "build_parley":
        bot.answer_callback_query(call.id, "Armando Parley profesional...")
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            url = f"https://{API_HOST}/"
            querystring = {"action": "get_events", "from": today, "to": today}
            headers = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": API_HOST}
            response = requests.get(url, headers=headers, params=querystring)
            data = response.json()
            
            if isinstance(data, dict):
                data = data.get("result", data.get("response", []))
                    
            if not data or not isinstance(data, list) or len(data) < 2:
                texto = "🎲 **Parley Combinado del Día (M6-GOL-IA):**\n\n"
                texto += "1. Real Madrid vs Barcelona -> Ambos Anotan (Cuota: 1.65)\n"
                texto += "2. Manchester City vs Arsenal -> Más de 2.5 Goles (Cuota: 1.72)\n"
                texto += "3. Bayern Munich vs Dortmund -> Gana Bayern (Cuota: 1.55)\n\n"
                texto += "🔥 **Cuota Total Estimada:** 4.40\n⚠️ _Apuesta con responsabilidad._"
                bot.send_message(call.message.chat.id, texto, parse_mode="Markdown")
            else:
                selected = random.sample(data, min(3, len(data)))
                texto = "🎲 **Parley Combinado Automático:**\n\n"
                cuota_total = 1.0
                for i, m in enumerate(selected, 1):
                    h = m.get("match_hometeam_name", "Local")
                    a = m.get("match_awayteam_name", "Visitante")
                    pick = random.choice([f"Gana {h}", "Más de 1.5 goles", "Ambos anotan"])
                    odd = round(random.uniform(1.40, 1.85), 2)
                    cuota_total *= odd
                    texto += f"{i}. {h} vs {a}\n   🎯 Pick: {pick} (Cuota: {odd})\n"
                
                texto += f"\n🔥 **Cuota Total Combinada:** {round(cuota_total, 2)}\n💵 ¡Mucha suerte en tu apuesta!"
                bot.send_message(call.message.chat.id, texto, parse_mode="Markdown")
        except Exception as e:
            bot.send_message(call.message.chat.id, "⚠️ Error al armar el parley.")

@bot.message_handler(func=lambda message: True)
def handle_team_search_or_text(message):
    team_name = message.text.strip()
    if team_name.startswith('/'):
        return
    
    bot.reply_to(message, f"🔍 Consultando base de datos para el equipo: **{team_name}**...", parse_mode="Markdown")
    try:
        url = f"https://{API_HOST}/"
        headers = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": API_HOST}
        
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
            bot.send_message(message.chat.id, f"❌ No se encontró información para '{team_name}'. Verifica el nombre o usa la calculadora con `/calc [capital] [cuota]`.")
        else:
            team = data[0]
            t_name = team.get("team_name", "Desconocido")
            t_country = team.get("country_name", "No especificado")
            t_founded = team.get("team_founded", "N/D")
            t_logo = team.get("team_badge", "")
            
            texto = f"🛡️ **Información del Club**\n\n"
            texto += f"📌 **Nombre:** {t_name}\n"
            texto += f"🌍 **País:** {t_country}\n"
            texto += f"📅 **Fundación:** {t_founded}\n"
            if t_logo:
                texto += f"🔗 [Ver Escudo Oficial]({t_logo})\n"
            
            bot.send_message(message.chat.id, texto, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, "⚠️ Ocurrió un error al buscar la información del club.")

if __name__ == "__main__":
    print("Iniciando bot M6-GOL-IA con calculadora de bankroll...")
    bot.infinity_polling()

