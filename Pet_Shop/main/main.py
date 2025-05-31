import sys
from pathlib import Path

# Corrige o path de importação
sys.path.insert(0, str(Path(__file__).parent.parent))

import tkinter as tk
from ui.tela_principal import TelaPrincipal
from database.db_manager import criar_banco

if __name__ == "__main__":
    criar_banco()  # Garante que o banco e as tabelas existem
    root = tk.Tk()
    app = TelaPrincipal(root)
    root.mainloop()