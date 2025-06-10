import sys
import os
from pathlib import Path
import tkinter as tk

# Adiciona o diretório raiz do projeto ao PATH
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

# Agora importe após configurar o path
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