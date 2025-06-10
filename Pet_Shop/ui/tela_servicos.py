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
        
        self.verificar_tabelas()  # Verifica se tabelas existem
        self.criar_widgets()
        self.carregar_pets()
        self.carregar_servicos()

    def verificar_tabelas(self):
        try:
            conn = conectar()
            cursor = conn.cursor()
            
            # Verifica e cria tabelas se não existirem
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    dono_id INTEGER NOT NULL,
                    FOREIGN KEY (dono_id) REFERENCES clientes(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS servicos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pet_id INTEGER NOT NULL,
                    tipo_servico TEXT NOT NULL,
                    data TEXT NOT NULL,
                    valor REAL NOT NULL,
                    FOREIGN KEY (pet_id) REFERENCES pets(id)
                )
            """)
            
            conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Erro no Banco de Dados", f"Erro ao verificar tabelas: {e}")
        finally:
            conn.close()

    def criar_widgets(self):
        # Frame de agendamento
        frame_agendamento = tk.LabelFrame(self.master, text="Agendar Serviço", padx=10, pady=10)
        frame_agendamento.pack(padx=10, pady=5, fill="x")

        # Dropdown de Pets
        tk.Label(frame_agendamento, text="Pet:").grid(row=0, column=0, sticky="e")
        self.combo_pets = ttk.Combobox(frame_agendamento, width=30, state="readonly")
        self.combo_pets.grid(row=0, column=1, pady=5, sticky="ew")

        # Tipo de Serviço
        tk.Label(frame_agendamento, text="Serviço:").grid(row=1, column=0, sticky="e")
        self.combo_servicos = ttk.Combobox(
            frame_agendamento, 
            values=["Banho", "Tosa", "Consulta", "Vacinação"], 
            width=27,
            state="readonly"
        )
        self.combo_servicos.grid(row=1, column=1, pady=5, sticky="ew")

        # Data
        tk.Label(frame_agendamento, text="Data (DD/MM/AAAA):").grid(row=2, column=0, sticky="e")
        self.entry_data = tk.Entry(frame_agendamento, width=30)
        self.entry_data.grid(row=2, column=1, pady=5, sticky="ew")
        self.entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))

        # Valor
        tk.Label(frame_agendamento, text="Valor R$:").grid(row=3, column=0, sticky="e")
        self.entry_valor = tk.Entry(frame_agendamento, width=30)
        self.entry_valor.grid(row=3, column=1, pady=5, sticky="ew")

        # Botões
        btn_agendar = tk.Button(frame_agendamento, text="Agendar", command=self.agendar_servico)
        btn_agendar.grid(row=4, columnspan=2, pady=10)

        # Frame de listagem
        frame_lista = tk.LabelFrame(self.master, text="Serviços Agendados", padx=10, pady=10)
        frame_lista.pack(padx=10, pady=5, fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_lista)
        scrollbar.pack(side="right", fill="y")

        # Tabela de serviços
        self.tree = ttk.Treeview(
            frame_lista,
            columns=("Pet", "Serviço", "Data", "Valor"),
            show="headings",
            yscrollcommand=scrollbar.set
        )
        
        # Configurar colunas
        self.tree.heading("Pet", text="Pet")
        self.tree.heading("Serviço", text="Serviço")
        self.tree.heading("Data", text="Data")
        self.tree.heading("Valor", text="Valor (R$)")
        
        self.tree.column("Pet", width=200)
        self.tree.column("Serviço", width=150)
        self.tree.column("Data", width=100)
        self.tree.column("Valor", width=100)
        
        self.tree.pack(fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)

    def carregar_pets(self):
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, p.nome, c.nome 
                FROM pets p
                JOIN clientes c ON p.dono_id = c.id
                ORDER BY p.nome
            """)
            self.pets = cursor.fetchall()
            self.combo_pets["values"] = [f"{p[1]} (Dono: {p[2]})" for p in self.pets]
            
            if self.pets:
                self.combo_pets.current(0)
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar pets: {e}")
        finally:
            conn.close()

    def carregar_servicos(self):
        self.tree.delete(*self.tree.get_children())  # Limpa a tabela antes de recarregar
        
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
                valor_formatado = f"R$ {float(row[3]):.2f}".replace(".", ",")
                self.tree.insert("", "end", values=(row[0], row[1], row[2], valor_formatado))
                
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao carregar serviços: {e}")
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
            # Validar data
            datetime.strptime(data, "%d/%m/%Y")
            
            # Validar valor
            valor_float = float(valor.replace(",", "."))
            if valor_float <= 0:
                raise ValueError("Valor deve ser positivo")
                
            # Obter ID do pet
            pet_id = self.pets[self.combo_pets.current()][0]
            
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO servicos (pet_id, tipo_servico, data, valor) VALUES (?, ?, ?, ?)",
                (pet_id, servico, data, valor_float)
            )
            conn.commit()
            
            messagebox.showinfo("Sucesso", "Serviço agendado com sucesso!")
            self.limpar_campos()
            self.carregar_servicos()
            
        except ValueError as e:
            messagebox.showerror("Erro", f"Dados inválidos: {e}")
        except sqlite3.Error as e:
            messagebox.showerror("Erro no Banco de Dados", f"Erro ao agendar serviço: {e}")
        finally:
            conn.close()

    def limpar_campos(self):
        self.combo_servicos.set('')
        self.entry_valor.delete(0, tk.END)
        if self.pets:  # Mantém o pet selecionado se houver
            self.combo_pets.current(0)