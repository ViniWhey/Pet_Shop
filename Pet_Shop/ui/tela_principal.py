import tkinter as tk
from tkinter import ttk

class TelaPrincipal:
    def __init__(self, master):
        self.master = master
        self.master.title("Sys.Pet_Shop")
        self.master.geometry("400x500")
        self.master.configure(bg='#f0f0f0')
        
        self.criar_widgets()

    def criar_widgets(self):

        # Cores e estilos
        button_bg = '#4CAF50'  # Verde
        button_fg = 'white'
        button_font = ('Arial', 10, 'bold')
        
        # Título
        titulo = tk.Label(self.master, 
                         text="Espaço_Pet", 
                         font=("Arial", 16, "bold"),
                         bg='#f0f0f0')
        titulo.pack(pady=20)

        # Frame para os botões principais
        button_frame = tk.Frame(self.master, bg='#f0f0f0')
        button_frame.pack(pady=10)

        # Botões principais
        btn_pets = tk.Button(button_frame, 
                            text="Ponto de Venda", 
                            width=25,
                            bg=button_bg,
                            fg=button_fg,
                            font=button_font,
                            command=self.abrir_Pdv)
        btn_pets.grid(row=0, column=0, pady=5, padx=20)
        
        btn_produtos = tk.Button(button_frame, 
                                text="Controle de Produtos", 
                                width=25,
                                bg=button_bg,
                                fg=button_fg,
                                font=button_font,
                                command=self.abrir_produtos)
        btn_produtos.grid(row=1, column=0, pady=5, padx=10)

        btn_produtos = tk.Button(button_frame, 
                                text="Dashboard", 
                                width=25,
                                bg=button_bg,
                                fg=button_fg,
                                font=button_font,
                                command=self.abrir_dashboard)
        btn_produtos.grid(row=2, column=0, pady=5, padx=10)

        #botao revenda
        btn_revenda = tk.Button(button_frame, 
                                text="Revenda", 
                                width=25,
                                bg=button_bg,
                                fg=button_fg,
                                font=button_font,
                                command=self.abrir_revenda)
        btn_revenda.grid(row=3, column=0, pady=5, padx=10)

        # Botão Sair
        btn_sair = tk.Button(self.master, 
                            text="Sair", 
                            width=25,
                            bg='#f44336',
                            fg='white',
                            font=button_font,
                            command=self.master.quit)
        btn_sair.pack(pady=20)

        # Barra de status
        self.status_bar = tk.Label(self.master, 
                                 text="Bem-vindo ao Sistema de Gestão do Espaço_Pet", 
                                 bd=1, relief=tk.SUNKEN, 
                                 anchor=tk.W,
                                 bg='#e0e0e0')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def abrir_Pdv(self):

        from pdv.Pdv import PontoDeVenda
        nova_janela = tk.Toplevel(self.master)
        PontoDeVenda(nova_janela)

    def abrir_produtos(self):

        from ui.tela_produtos import TelaProdutos
        nova_janela = tk.Toplevel(self.master)
        TelaProdutos(nova_janela)
    
    def abrir_dashboard(self):
        from dashboard.dash import TelaDashboard
        nova_janela = tk.Toplevel(self.master)
        TelaDashboard(nova_janela)

    def abrir_revenda(self):
        from ui.tela_revenda import TelaRevenda
        nova_janela = tk.Toplevel(self.master)
        TelaRevenda(nova_janela)