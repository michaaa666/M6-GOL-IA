import logging
import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Obtenemos el token de forma segura desde el sistema
TOKEN = os.getenv("TELEGRAM_TOKEN", "8686894438:AAGmzCI2Av0jpATPGWM42UyRxvgRB2G8MVQ")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teclado = [
        [InlineKeyboardButton("⚽ Filtrar Partidos por Liga", callback_data='menu_ligas')],
        [InlineKeyboardButton("💡 Tips de Apuestas Deportivas", callback_data='tips')],
        [InlineKeyboardButton("📊 Calculadora de Stake y Bankroll", callback_data='stake_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(teclado)
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="¡Hola! Soy M6 GOL IA. ⚽🤖\nTu asistente avanzado de fútbol. Selecciona una opción o usa `/stake [monto]`:",
        reply_markup=reply_markup
    )

async def obtener_partidos_por_liga(liga_filtro):
    try:
        url = "https://www.thesportsdb.com/api/v1/json/3/eventsday.php?d=2026-07-30&s=Soccer"
        response = requests.get(url, timeout=5)
        data = response.json()
        eventos = data.get('events')
        
        if not eventos:
            return "⚽ No hay partidos registrados para hoy."
        
        filtrados = []
        for evento in eventos:
            liga = evento.get('strLeague', '')
            if liga_filtro.lower() in liga.lower() or liga_filtro == 'todos':
                filtrados.append(evento)
        
        if not filtrados:
            return f"⚽ No hay partidos disponibles hoy para la liga seleccionada."
        
        texto = f"⚽ **Partidos ({liga_filtro.upper() if liga_filtro != 'todos' else 'Todos'}):**\n\n"
        for evento in filtrados[:5]:
            liga = evento.get('strLeague', 'Liga')
            local = evento.get('strHomeTeam', 'Local')
            visitante = evento.get('strAwayTeam', 'Visitante')
            texto += f"🏆 *{liga}*\n🔥 {local} vs {visitante}\n\n"
        return texto
    except Exception:
        return "⚠️ Error al conectar con el servidor de la API."

async def calcular_stake(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        capital = float(context.args[0])
        s1 = capital * 0.01
        s3 = capital * 0.03
        s5 = capital * 0.05
        
        mensaje = (
            f"💰 **Cálculo de Bankroll: ${capital:.2f}**\n\n"
            f"🔹 **Stake 1 (1%):** ${s1:.2f}\n"
            f"🔸 **Stake 3 (3%):** ${s3:.2f}\n"
            f"🔥 **Stake 5 (5%):** ${s5:.2f}\n\n"
            f"_¡Disciplina total en cada jornada!_"
        )
        await update.message.reply_text(mensaje)
    except (IndexError, ValueError):
        await update.message.reply_text(
            "⚠️ Por favor, ingresa un monto válido después del comando.\nEjemplo: `/stake 150`"
        )

async def boton_pulsado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'menu_ligas':
        teclado_ligas = [
            [InlineKeyboardButton("🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League", callback_data='liga_premier')],
            [InlineKeyboardButton("🇪🇸 La Liga", callback_data='liga_laliga')],
            [InlineKeyboardButton("🇦🇷 Argentina", callback_data='liga_arg')],
            [InlineKeyboardButton("🌍 Ver Todos", callback_data='liga_todos')],
            [InlineKeyboardButton("⬅️ Volver al Menú", callback_data='menu_principal')]
        ]
        await query.edit_message_text(
            text="🏆 Selecciona la liga que deseas consultar:",
            reply_markup=InlineKeyboardMarkup(teclado_ligas)
        )
    elif query.data.startswith('liga_'):
        tipo = query.data.split('_')[1]
        filtro_map = {
            'premier': 'Premier League',
            'laliga': 'Spanish Primera Division',
            'arg': 'Argentinian',
            'todos': 'todos'
        }
        liga_busqueda = filtro_map.get(tipo, 'todos')
        await query.edit_message_text(text="🔄 Consultando partidos...")
        resultado = await obtener_partidos_por_liga(liga_busqueda)
        
        volver = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Volver a Ligas", callback_data='menu_ligas')]])
        await query.edit_message_text(text=resultado, reply_markup=volver, parse_mode='Markdown')
        
    elif query.data == 'menu_principal':
        teclado = [
            [InlineKeyboardButton("⚽ Filtrar Partidos por Liga", callback_data='menu_ligas')],
            [InlineKeyboardButton("💡 Tips de Apuestas Deportivas", callback_data='tips')],
            [InlineKeyboardButton("📊 Calculadora de Stake y Bankroll", callback_data='stake_menu')]
        ]
        await query.edit_message_text(
            text="¡Hola! Soy M6 GOL IA. ⚽🤖\nTu asistente avanzado de fútbol. Selecciona una opción o usa `/stake [monto]`:",
            reply_markup=reply_markup
        )
    elif query.data == 'tips':
        teclado_volver = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Volver", callback_data='menu_principal')]])
        await query.edit_message_text(
            text="💡 **Tip Pro de Fútbol:**\n\nAnaliza siempre las alineaciones confirmadas y las bajas de última hora antes de apostar.",
            reply_markup=teclado_volver
        )
    elif query.data == 'stake_menu':
        teclado_volver = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Volver", callback_data='menu_principal')]])
        await query.edit_message_text(
            text="📊 **Calculadora de Bankroll:**\n\nEscribe en el chat el comando con tu capital:\n`/stake [monto]`\nEjemplo: `/stake 200`",
            reply_markup=teclado_volver
        )

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('stake', calcular_stake))
    application.add_handler(CallbackQueryHandler(boton_pulsado))
    
    print("M6 GOL IA listo para la nube... Presiona Ctrl+C para apagar.")
    application.run_polling()
