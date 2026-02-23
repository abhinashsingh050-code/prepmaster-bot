from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from datetime import datetime
import asyncio
from PIL import Image
from fpdf import FPDF
import yt_dlp

tasks = {}
lectures = {}
exam_date = {}
user_images = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to PrepMaster Bot By ABHINASH!")

async def addtask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.id
    task = " ".join(context.args)
    if user not in tasks:
        tasks[user] = []
    tasks[user].append(task)
    await update.message.reply_text(f"Task added: {task}")

async def viewtasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.id
    if user in tasks and tasks[user]:
        msg = "\n".join([f"{i+1}. {t}" for i,t in enumerate(tasks[user])])
        await update.message.reply_text(f"Tasks:\n{msg}")
    else:
        await update.message.reply_text("No tasks.")

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.id
    try:
        index = int(context.args[0]) - 1
        completed = tasks[user].pop(index)
        await update.message.reply_text(f"Completed: {completed}")
    except:                                                                                                                         await update.message.reply_text("Use: /done task_number")

async def addlecture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.id
    subject = context.args[0]
    count = int(context.args[1])
    if user not in lectures:
        lectures[user] = {}
    lectures[user][subject] = count
    await update.message.reply_text(f"{subject}: {count} lectures added")

async def exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.id
    date = context.args[0]
    exam_date[user] = datetime.strptime(date, "%d-%m-%Y")
    await update.message.reply_text(f"Exam date set to {date}")

async def strategy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.id
    if user not in lectures or user not in exam_date:
        await update.message.reply_text("Add lectures and exam date first.")
        return
    total = sum(lectures[user].values())
    today = datetime.now()
    days_left = (exam_date[user] - today).days
    if days_left <= 0:
        await update.message.reply_text("Exam date passed!")
        return
    daily = round(total / days_left, 2)
    msg = f"Days left: {days_left}\nPending lectures: {total}\nDo {daily} lectures/day\n\nSuggested Plan:\n"
    for sub, val in lectures[user].items():
        msg += f"{sub}: {round(val/days_left,1)} lecture/day\n"
    await update.message.reply_text(msg)

async def focus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    minutes = int(context.args[0])
    await update.message.reply_text(f"Focus started for {minutes} minutes")
    await asyncio.sleep(minutes * 60)
    await update.message.reply_text("Time’s up! Mark your task done.")

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.id
    if user not in user_images:
        user_images[user] = []
    photo_file = await update.message.photo[-1].get_file()
    file_path = f"{user}_{len(user_images[user])}.jpg"
    await photo_file.download_to_drive(file_path)
    user_images[user].append(file_path)
    await update.message.reply_text("Image saved! Send more or type /makepdf")

async def makepdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.id
    if user not in user_images or not user_images[user]:
        await update.message.reply_text("No images found.")
        return
    pdf = FPDF()
    for img in user_images[user]:
        pdf.add_page()
        pdf.image(img, 10, 10, 190)
    pdf.output(f"{user}.pdf")
    with open(f"{user}.pdf", "rb") as f:
        await update.message.reply_document(f)
    user_images[user] = []

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    song = " ".join(context.args)
    await update.message.reply_text("Downloading...")
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"ytsearch:{song}"])
    await update.message.reply_audio(audio=open("song.mp3", "rb"))

import os
app = ApplicationBuilder().token(os.environ.get("8503308378:AAGx0i8uZodoLt17LmofQ_zwVYEtNHlLreQ")).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("addtask", addtask))
app.add_handler(CommandHandler("viewtasks", viewtasks))
app.add_handler(CommandHandler("done", done))
app.add_handler(CommandHandler("addlecture", addlecture))
app.add_handler(CommandHandler("exam", exam))
app.add_handler(CommandHandler("strategy", strategy))
app.add_handler(CommandHandler("focus", focus))
app.add_handler(CommandHandler("makepdf", makepdf))
app.add_handler(CommandHandler("play", play))
app.add_handler(MessageHandler(filters.PHOTO, photo))

app.run_polling()
