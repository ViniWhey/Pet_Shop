import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk

# Adiciona o diretório raiz do projeto ao PATH
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

# Função customizada de messagebox
def show_custom_messagebox(master, title, message, icon="info", accent=None):
    if accent is None:
        if icon == "info":
            accent = "#2196f3"
        elif icon == "warning":
            accent = "#ffb300"
        elif icon == "error":
            accent = "#e53935"
        else:
            accent = "#4CAF50"

    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Dialog.TFrame", background="#23272e", borderwidth=0, relief="flat")
    style.configure("Dialog.TLabel", background="#23272e", foreground="#EEEEEE", font=("Segoe UI", 12))
    style.configure("DialogTitle.TLabel", background="#23272e", foreground=accent, font=("Segoe UI", 15, "bold"))
    style.configure("DialogAccent.TButton", background=accent, foreground="#fff", font=("Segoe UI", 11, "bold"), borderwidth=0, focusthickness=3, focuscolor=accent)
    style.map("DialogAccent.TButton",
              background=[("active", "#1769aa" if icon == "info" else "#b28704" if icon == "warning" else "#b71c1c")],
              foreground=[("active", "#fff")])

    dialog = tk.Toplevel(master)
    dialog.title(title)
    dialog.transient(master)
    dialog.grab_set()
    dialog.resizable(False, False)
    dialog.configure(bg="#23272e")

    dialog.update_idletasks()
    w = 420
    h = 210
    x = master.winfo_rootx() + master.winfo_width()//2 - w//2
    y = master.winfo_rooty() + master.winfo_height()//2 - h//2
    dialog.geometry(f"{w}x{h}+{x}+{y}")

    frame = ttk.Frame(dialog, style="Dialog.TFrame", padding=(24, 18, 24, 18))
    frame.pack(expand=True, fill="both")

    title_label = ttk.Label(frame, text=title, style="DialogTitle.TLabel")
    title_label.pack(anchor="w", pady=(0, 8))

    content_frame = tk.Frame(frame, bg="#23272e")
    content_frame.pack(fill="x", pady=(0, 10))

    canvas = tk.Canvas(content_frame, width=44, height=44, bg="#23272e", highlightthickness=0)
    canvas.pack(side="left", padx=(0, 10))
    canvas.create_oval(2, 2, 42, 42, fill=accent, outline=accent)
    if icon == "info":
        canvas.create_text(22, 22, text="i", fill="white", font=("Segoe UI", 22, "bold"))
    elif icon == "warning":
        canvas.create_text(22, 22, text="!", fill="white", font=("Segoe UI", 22, "bold"))
    elif icon == "error":
        canvas.create_text(22, 22, text="✖", fill="white", font=("Segoe UI", 20, "bold"))
    else:
        canvas.create_text(22, 22, text="?", fill="white", font=("Segoe UI", 22, "bold"))

    msg_label = ttk.Label(content_frame, text=message, style="Dialog.TLabel", wraplength=320, justify="left")
    msg_label.pack(side="left", fill="x", expand=True)

    ok_btn = ttk.Button(frame, text="OK", command=dialog.destroy, style="DialogAccent.TButton", cursor="hand2")
    ok_btn.pack(pady=(10, 0), ipadx=18, ipady=2)
    ok_btn.focus_set()

    dialog.wait_window(dialog)

from ui.tela_principal import TelaPrincipal
from database.db_manager import DatabaseManager

def main():
    # Inicializa o banco de dados
    if DatabaseManager():
        print("Banco de dados inicializado com sucesso!")
    else:
        print("Erro ao inicializar o banco de dados")
        return
    
    # Inicia a aplicação
    root = tk.Tk()
    app = TelaPrincipal(root)
    root.mainloop()

if __name__ == "__main__":
    main()