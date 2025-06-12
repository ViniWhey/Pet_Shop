import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database.db_manager import DatabaseManager

class TelaServicos:
    def __init__(self, master):
        self.master = master
        self.master.title("Agendamento de Serviços")
        self.master.state('zoomed')  # Janela maximizada, igual ao PDV

        self.configurar_estilos()
        self.verificar_tabelas()
        self.criar_widgets()
        self.carregar_pets()
        self.carregar_servicos()

    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Arial', 10))
        style.configure('Accent.TButton', font=('Arial', 10, 'bold'), foreground='white', background='#4CAF50')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Total.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Treeview.Heading', font=('Arial', 11, 'bold'))
        style.configure('Treeview', font=('Arial', 10), rowheight=28)
        style.configure('TLabel', font=('Arial', 10))
        style.configure('TEntry', font=('Arial', 10))
        style.configure('TCombobox', font=('Arial', 10))
        self.bg_color = "#f5f5f5"
        self.master.configure(bg=self.bg_color)

    def verificar_tabelas(self):
        try:
            db = DatabaseManager()
            conn = db.conectar()
            cursor = conn.cursor()
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
        # Frame principal
        main_frame = ttk.Frame(self.master, padding=15)
        main_frame.pack(fill='both', expand=True)

        # Frame de agendamento
        frame_agendamento = ttk.LabelFrame(main_frame, text="Agendar Serviço", padding=15)
        frame_agendamento.pack(fill="x", padx=5, pady=(0, 15))

        # Pet
        ttk.Label(frame_agendamento, text="Pet:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.combo_pets = ttk.Combobox(frame_agendamento, width=30, state="readonly")
        self.combo_pets.grid(row=0, column=1, pady=5, sticky="ew", padx=5)

        # Tipo de Serviço
        ttk.Label(frame_agendamento, text="Serviço:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.combo_servicos = ttk.Combobox(
            frame_agendamento,
            values=["Banho", "Tosa", "Consulta", "Vacinação"],
            width=27,
            state="readonly"
        )
        self.combo_servicos.grid(row=1, column=1, pady=5, sticky="ew", padx=5)

        # Data
        ttk.Label(frame_agendamento, text="Data (DD/MM/AAAA):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_data = ttk.Entry(frame_agendamento, width=30)
        self.entry_data.grid(row=2, column=1, pady=5, sticky="ew", padx=5)
        self.entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))

        # Valor
        ttk.Label(frame_agendamento, text="Valor R$:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.entry_valor = ttk.Entry(frame_agendamento, width=30)
        self.entry_valor.grid(row=3, column=1, pady=5, sticky="ew", padx=5)

        # Botões
        btns_frame = ttk.Frame(frame_agendamento)
        btns_frame.grid(row=4, column=0, columnspan=2, pady=10)
        btn_agendar = ttk.Button(btns_frame, text="Agendar", style='Accent.TButton', command=self.agendar_servico)
        btn_agendar.pack(side='left', padx=5)
        btn_limpar = ttk.Button(btns_frame, text="Limpar", command=self.limpar_campos)
        btn_limpar.pack(side='left', padx=5)

        # Frame de listagem
        frame_lista = ttk.LabelFrame(main_frame, text="Serviços Agendados", padding=15)
        frame_lista.pack(fill="both", expand=True, padx=5, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_lista)
        scrollbar.pack(side="right", fill="y")

        # Tabela de serviços
        self.tree = ttk.Treeview(
            frame_lista,
            columns=("Pet", "Serviço", "Data", "Valor"),
            show="headings",
            yscrollcommand=scrollbar.set,
            selectmode='browse',
            height=18
        )
        self.tree.heading("Pet", text="Pet")
        self.tree.heading("Serviço", text="Serviço")
        self.tree.heading("Data", text="Data")
        self.tree.heading("Valor", text="Valor (R$)")
        self.tree.column("Pet", width=250, anchor='w')
        self.tree.column("Serviço", width=180, anchor='center')
        self.tree.column("Data", width=120, anchor='center')
        self.tree.column("Valor", width=120, anchor='center')
        self.tree.pack(fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)

        # Botão de remover serviço agendado
        btn_remover = ttk.Button(frame_lista, text="Remover Selecionado", command=self.remover_servico)
        btn_remover.pack(side='bottom', pady=8)

    def carregar_pets(self):
        try:
            db = DatabaseManager()
            conn = db.conectar()
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
        self.tree.delete(*self.tree.get_children())
        try:
            db = DatabaseManager()
            conn = db.conectar()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.id, p.nome, s.tipo_servico, s.data, s.valor
                FROM servicos s
                JOIN pets p ON s.pet_id = p.id
                ORDER BY s.data DESC
            """)
            for row in cursor.fetchall():
                valor_formatado = f"R$ {float(row[4]):.2f}".replace(".", ",")
                self.tree.insert("", "end", iid=row[0], values=(row[1], row[2], row[3], valor_formatado))
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
            db = DatabaseManager()
            conn = db.conectar()
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

    def remover_servico(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um serviço para remover.")
            return
        confirm = messagebox.askyesno("Confirmação", "Deseja remover o serviço selecionado?")
        if not confirm:
            return
        try:
            db = DatabaseManager()
            conn = db.conectar()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM servicos WHERE id = ?", (selected,))
            conn.commit()
            self.carregar_servicos()
            messagebox.showinfo("Removido", "Serviço removido com sucesso!")
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao remover serviço: {e}")
        finally:
            conn.close()

    def limpar_campos(self):
        self.combo_servicos.set('')
        self.entry_valor.delete(0, tk.END)
        self.entry_data.delete(0, tk.END)
        self.entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
        if self.pets:
            self.combo_pets.current(0)