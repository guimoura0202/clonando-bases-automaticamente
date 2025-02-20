import pyautogui
import keyboard
import time
from pymongo import MongoClient
import re
import dotenv
import os
import pyperclip
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import platform

dotenv.load_dotenv()
CLONA_BASE1 = dotenv.get("CLONA_BASE1")
CLONA_BASE2 = dotenv.get("CLONA_BASE2")
CLONA_BASE3 = dotenv.get("CLONA_BASE3")

client = MongoClient("mongodb://localhost:27017/")
db = client['BaseSistemaWL']
collection = db['ASPNETUsers']
collection_licenses = db['DtoLicencaSistema']
collection_config = db['Config']

def find_by_email(email):
    document = collection.find_one({"Email": email})
    if document:
        db_server_region = document.get("DbServerRegion", "Região não especificada")
        id_value = document.get("_id")
        return db_server_region, id_value
    else:
        return None, None

def find_wlid_by_cid(cid):
    document = collection_licenses.find_one({"CID": cid})
    if document:
        wlid = document.get("WLID", "WLID não especificado")
        return wlid
    else:
        return None

def ultimo_numero_na_string(s):
    return re.findall(r'\d+', s)[-1]

def write_and_press(command):
    pyautogui.write(command)
    pyautogui.press('enter')


def open_terminal():
    if platform.system() == 'Windows':
        pyautogui.hotkey('winleft', 'r')
        write_and_press('cmd')
    elif platform.system() == 'Darwin':  # macOS
        pyautogui.hotkey('command', 'space')
        time.sleep(1)
        write_and_press('Terminal')
    elif platform.system() == 'Linux':
        pyautogui.hotkey('ctrl', 'alt', 't')

def clonar_base():
    email_cliente = app.email_entry.get()
    mongo_path = app.path_entry.get()

    if not mongo_path:
        messagebox.showerror("Erro", "Por favor, insira um caminho válido para o MongoDB.")
        return

    app.progress_label.configure(text="Buscando informações no banco de dados...")
    app.update()

    db_server_region, id_value = find_by_email(email_cliente)
    if db_server_region and id_value:
        region = str(ultimo_numero_na_string(db_server_region))
        clona_base = f"{CLONA_BASE1}{region}{CLONA_BASE2}{id_value}{CLONA_BASE3}"

        open_terminal()
        time.sleep(1)
        write_and_press(f'cd {mongo_path}')
        time.sleep(1)
        keyboard.write(clona_base)
        pyautogui.press('enter')
        pyautogui.press('enter')
        time.sleep(1)

        app.progress_label.configure(text="Base está sendo clonada...")
        app.update()

        wlid = find_wlid_by_cid(id_value)
        if wlid:
            pyperclip.copy(wlid)
            time.sleep(5)
            messagebox.showinfo("Sucesso", "Base está sendo clonada e a WLID já foi copiada para a área de transferência.")
        else:
            messagebox.showerror("Erro", "WLID não encontrado.")
    else:
        messagebox.showerror("Erro", "Email não encontrado ou DbServerRegion não especificado.")

    # Save the mongo path to the database
    save_mongo_path(mongo_path)
    app.progress_label.configure(text="")

def toggle_path_entry():
    if app.path_entry.winfo_viewable():
        app.path_entry.grid_remove()
    else:
        app.path_entry.grid()

def save_mongo_path(path):
    collection_config.update_one({"config": "mongo_path"}, {"$set": {"path": path}}, upsert=True)

def load_mongo_path():
    document = collection_config.find_one({"config": "mongo_path"})
    if document:
        return document.get("path", "")
    else:
        return ""

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.center_window(600, 300)
        self.title("Clonar Base")
        self.resizable(False, False)

        self.grid_config()

        self.title_label = ctk.CTkLabel(master=self,
                                        text="Clonar Base",
                                        font=ctk.CTkFont(size=30, weight="bold"))

        self.url_label = ctk.CTkLabel(master=self,
                                      text="Email do Cliente:",
                                      font=ctk.CTkFont(size=15, weight="normal"))

        self.email_entry = ctk.CTkEntry(master=self,
                                        width=400,
                                        height=30,
                                        border_width=2,
                                        corner_radius=10)

        self.path_entry = ctk.CTkEntry(master=self,
                                       width=400,
                                       height=30,
                                       border_width=2,
                                       corner_radius=10)

        # Load the mongo path from the database and insert it into the entry
        mongo_path = load_mongo_path()
        if mongo_path:
            self.path_entry.insert(0, mongo_path)
        else:
            self.path_entry.insert(0, "C:\\mongo\\bin" if platform.system() == 'Windows' else "/mongo/bin")

        self.toggle_path_label = ctk.CTkLabel(master=self,
                                              text="Alterar caminho para o MongoDB",
                                              font=ctk.CTkFont(size=12, weight="normal"),
                                              text_color="#1f6aa5",  # Azul do botão
                                              cursor="hand2")
        self.toggle_path_label.bind("<Button-1>", lambda e: toggle_path_entry())

        self.clonar_btn = ctk.CTkButton(master=self,
                                        height=30,
                                        text="Clonar Base",
                                        width=195,
                                        command=clonar_base)

        self.progress_label = ctk.CTkLabel(master=self,
                                           text="",
                                           font=ctk.CTkFont(size=15, weight="normal"))

        self.title_label.grid(row=0, column=0, columnspan=4, pady=20)
        self.url_label.grid(row=1, column=0, sticky='e')
        self.email_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=10)
        self.toggle_path_label.grid(row=2, column=1, columnspan=2, pady=10, sticky='w')
        self.path_entry.grid(row=3, column=1, columnspan=2, padx=10, pady=10)
        self.path_entry.grid_remove()  # Ensure the path entry is hidden on start
        self.clonar_btn.grid(row=4, column=1, columnspan=2, pady=20)
        self.progress_label.grid(row=5, column=0, columnspan=4)

    def center_window(self, width, height):
        width_screen = self.winfo_screenwidth()
        height_screen = self.winfo_screenheight()
        x = (width_screen / 2) - (width / 2)
        y = (height_screen / 2) - (height / 2)
        self.geometry('%dx%d+%d+%d' % (width, height, x, y))

    def grid_config(self):
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

if __name__ == "__main__":
    app = App()
    app.mainloop()
