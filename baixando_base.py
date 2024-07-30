import pyautogui
import keyboard
import time
from pymongo import MongoClient
import re
import dotenv
import os
import pyperclip
import tkinter as tk
from tkinter import messagebox

dotenv.load_dotenv()
CLONA_BASE1 = os.getenv('CLONA_BASE1')
CLONA_BASE2 = os.getenv('CLONA_BASE2')
CLONA_BASE3 = os.getenv('CLONA_BASE3')

# Conectar ao servidor MongoDB
client = MongoClient("mongodb://localhost:27017/")

db = client['BaseSistemaWL']

collection = db['ASPNETUsers']
collection_licenses = db['DtoLicencaSistema']

# Função para buscar DbServerRegion e Id pelo Email
def find_by_email(email):
    # Buscar o documento que contém o Email fornecido
    document = collection.find_one({"Email": email})
    
    if document:
        db_server_region = document.get("DbServerRegion", "Região não especificada")
        id_value = document.get("_id")
        return db_server_region, id_value
    else:
        return None, None

# Função para buscar WLID pelo CID
def find_wlid_by_cid(cid):
    document = collection_licenses.find_one({"CID": cid})
    if document:
        wlid = document.get("WLID", "WLID não especificado")
        return wlid
    else:
        return None

def ultimo_numero_na_string(s):
    '''
    Retorna o último número encontrado em uma string.
    '''
    return re.findall(r'\d+', s)[-1]

def write_and_press(command):
    pyautogui.write(command)
    pyautogui.press('enter')
    
def clonar_base():
    email_cliente = email_entry.get()
    db_server_region, id_value = find_by_email(email_cliente)

    if db_server_region and id_value:
        region = str(ultimo_numero_na_string(db_server_region))
        clona_base = f"{CLONA_BASE1}{region}{CLONA_BASE2}{id_value}{CLONA_BASE3}"

        pyautogui.hotkey('winleft', 'r')
        write_and_press('cmd')
        time.sleep(1)
        write_and_press('cd C:\\mongo\\bin')
        time.sleep(1)
        # Pyautogui estava com problemas com caracteres especiais no comando abaixo (interrogação) e foi usado o keyboard como alternativa
        keyboard.write(clona_base)
        pyautogui.press('enter')

        wlid = find_wlid_by_cid(id_value)
        if wlid:
            pyperclip.copy(wlid)
            time.sleep(5)
            messagebox.showinfo("Sucesso", "Base está sendo clonada e WLID já foi copiado para a área de transferência.")
        else:
            messagebox.showerror("Erro", "WLID não encontrado.")
    else:
        messagebox.showerror("Erro", "Email não encontrado ou DbServerRegion não especificado.")

# Carregar as variáveis do arquivo .env
CLONA_BASE1 = os.getenv('CLONA_BASE1')
CLONA_BASE2 = os.getenv('CLONA_BASE2')
CLONA_BASE3 = os.getenv('CLONA_BASE3')

# Criar a interface gráfica
root = tk.Tk()
root.title("Clonar Base")

tk.Label(root, text="Email do Cliente:").pack(pady=5)
email_entry = tk.Entry(root, width=50)
email_entry.pack(pady=5)

clonar_button = tk.Button(root, text="Clonar Base", command=clonar_base)
clonar_button.pack(pady=20)

root.mainloop()