import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database.db_manager import conectar

class TelaServicos:
    def __init__(self, master):
        self.master = master
        self.master.title("Agendamento de Serviços")
        self.master.geometry("900x600")
        
        self.criar_widgets()
        self.carregar_pets()
        self.carregar_servicos()

    def criar_widgets(self):
        # Frame de agendamento
        frame_agendamento = tk.LabelFrame(self.master, text="Agendar Serviço", padx=10, pady=10)
        frame_agendamento.pack(padx=10, pady=5, fill="x")

        # Dropdown de Pets
        tk.Label(frame_agendamento, text="Pet:").grid(row=0, column=0, sticky="e")
        self.combo_pets = ttk.Combobox(frame_agendamento, width=30)
        self.combo_pets.grid(row=0, column=1, pady=5)

        # Tipo de Serviço
        tk.Label(frame_agendamento, text="Serviço:").grid(row=1, column=0, sticky="e")
        self.combo_servicos = ttk.Combobox(frame_agendamento, values=["Banho", "Tosa", "Consulta", "Vacinação"], width=27)
        self.combo_servicos.grid(row=1, column=1, pady=5)

        # Data
        tk.Label(frame_agendamento, text="Data (DD/MM/AAAA):").grid(row=2, column=0, sticky="e")
        self.entry_data = tk.Entry(frame_agendamento, width=30)
        self.entry_data.grid(row=2, column=1, pady=5)
        self.entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))

        # Valor
        tk.Label(frame_agendamento, text="Valor R$:").grid(row=3, column=0, sticky="e")
        self.entry_valor = tk.Entry(frame_agendamento, width=30)
        self.entry_valor.grid(row=3, column=1, pady=5)

        # Botões
        btn_agendar = tk.Button(frame_agendamento, text="Agendar", command=self.agendar_servico)
        btn_agendar.grid(row=4, columnspan=2, pady=10)

        # Frame de listagem
        frame_lista = tk.LabelFrame(self.master, text="Serviços Agendados", padx=10, pady=10)
        frame_lista.pack(padx=10, pady=5, fill="both", expand=True)

        # Tabela de serviços
        self.tree = ttk.Treeview(frame_lista, columns=("Pet", "Serviço", "Data", "Valor"), show="headings")
        self.tree.heading("Pet", text="Pet")
        self.tree.heading("Serviço", text="Serviço")
        self.tree.heading("Data", text="Data")
        self.tree.heading("Valor", text="Valor (R$)")
        self.tree.pack(fill="both", expand=True)

    def carregar_pets(self):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.nome, c.nome 
            FROM pets p
            JOIN clientes c ON p.dono_id = c.id
        """)
        self.pets = cursor.fetchall()
        self.combo_pets["values"] = [f"{p[1]} (Dono: {p[2]})" for p in self.pets]
        conn.close()

    def carregar_servicos(self):
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.nome, s.tipo_servico, s.data, s.valor
                FROM servicos s
                JOIN pets p ON s.pet_id = p.id
                ORDER BY s.data DESC
            """)
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
        except sqlite3.OperationalError as e:
            messagebox.showerror("Erro", f"Tabela não encontrada: {e}\nExecute db_manager.py primeiro!")
        finally:
            conn.close()

    def agendar_servico(self):
        pet_selecionado = self.combo_pets.get()
        servico = self.combo_servicos.get()
        data = self.entry_data.get()
        valor = self.entry_valor.get()

        if not all([pet_selecionado, servico, data, valor]):
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return

        try:
            pet_id = self.pets[self.combo_pets.current()][0]
            valor_float = float(valor.replace(",", "."))
        except (ValueError, IndexError):
            messagebox.showerror("Erro", "Valor inválido ou pet não selecionado!")
            return

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO servicos (pet_id, tipo_servico, data, valor) VALUES (?, ?, ?, ?)",
            (pet_id, servico, data, valor_float)
        )
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Sucesso", "Serviço agendado!")
        self.limpar_campos()
        self.carregar_servicos()

    def limpar_campos(self):
        self.entry_valor.delete(0, tk.END)