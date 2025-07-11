from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import random
import re

# Estados del flujo de conversación
NOMBRE, VALOR, NUMERO = range(3)

# Inicio
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bienvenido. Vamos a generar tu comprobante.\n\n🔤 ¿Cuál es el *nombre*?")
    return NOMBRE

# Recibe nombre
async def recibir_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre = update.message.text.strip()
    if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ ]+", nombre):
        await update.message.reply_text("❌ Nombre inválido. Solo letras y espacios.")
        return NOMBRE
    context.user_data["nombre"] = nombre
    await update.message.reply_text("💰 ¿Cuál es el *valor* (solo número, ej: 20000)?")
    return VALOR

# Recibe valor
async def recibir_valor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    valor = update.message.text.strip()
    if not valor.isdigit():
        await update.message.reply_text("❌ Valor inválido. Solo números sin puntos ni comas.")
        return VALOR
    valor_entero = int(valor)
    valor_formateado = "$ {:,},00".format(valor_entero).replace(",", ".")
    context.user_data["valor"] = valor_formateado
    await update.message.reply_text("📞 ¿Cuál es el *número Nequi* (10 dígitos)?")
    return NUMERO

# Recibe número, genera imagen y responde
async def recibir_numero(update: Update, context: ContextTypes.DEFAULT_TYPE):
    numero = update.message.text.strip().replace(" ", "").replace("-", "")
    if not (numero.isdigit() and len(numero) == 10):
        await update.message.reply_text("❌ Número inválido. Debe tener 10 dígitos.")
        return NUMERO

    numero_formateado = f"{numero[:3]} {numero[3:6]} {numero[6:]}"
    context.user_data["numero"] = numero_formateado
    await update.message.reply_text("🧾 Generando comprobante...")

    # Cargar imagen y fuente
    imagen = Image.open("comprobante.png.png")
    dibujo = ImageDraw.Draw(imagen)
    fuente = ImageFont.truetype("Montserrat-Medium.ttf", 27)
    color = (55, 55, 55)

    # Datos
    nombre = context.user_data["nombre"]
    valor = context.user_data["valor"]
    numero = context.user_data["numero"]
    disponible = "Disponible"
    referencia = "M" + str(random.randint(100000000, 999999999))

    meses = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }
    fecha_actual = datetime.now()
    hora = fecha_actual.strftime("%I:%M %p").lower().replace("am", "a. m.").replace("pm", "p. m.")
    fecha_formateada = f"{fecha_actual.day} de {meses[fecha_actual.month]} de {fecha_actual.year} a las {hora}"

    # Insertar en plantilla (ajusta coordenadas si cambia)
    dibujo.text((60, 770), nombre, font=fuente, fill=color)
    dibujo.text((60, 880), valor, font=fuente, fill=color)
    dibujo.text((60, 985), numero, font=fuente, fill=color)
    dibujo.text((60, 1100), fecha_formateada, font=fuente, fill=color)
    dibujo.text((60, 1200), referencia, font=fuente, fill=color)
    dibujo.text((60, 1300), disponible, font=fuente, fill=color)

    # Guardar imagen final
    archivo = f"comprobante_{random.randint(1000,9999)}.png"
    imagen.save(archivo)

    # Enviar imagen al usuario
    await update.message.reply_photo(photo=open(archivo, "rb"), caption="✅ Aquí está tu comprobante.")
    return ConversationHandler.END

# Cancelar
async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Operación cancelada.")
    return ConversationHandler.END

# MAIN del bot
def main():
    app = Application.builder().token("7285473475:AAGrLwAY75mFH7MLQqLRrT1MlowI-xQEPGY").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("comprobante", start)],
        states={
            NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_nombre)],
            VALOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_valor)],
            NUMERO: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_numero)],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
