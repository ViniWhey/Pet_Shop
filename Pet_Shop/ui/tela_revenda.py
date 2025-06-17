import sqlite3
from tkinter import ttk, messagebox
from database.db_manager import DatabaseManager

class TelaRevenda:
    def __init__(self, master):
        self.master = master
        self.master.title("Tela de Revenda")
        self.master.geometry("600x400")
        self.inicializar_banco()
        self.criar_widgets()
    
    def criar_widgets(self):
        """
        Cria os widgets da tela de revenda, incluindo botões e labels.
        """
        self.label = ttk.Label(self.master, text="Tela de Revenda", font=("Arial", 16))
        self.label.pack(pady=20)

        self.btn_avisar_clientes = ttk.Button(self.master, text="Avisar Clientes para Contato", command=self.avisar_clientes_para_contato)
        self.btn_avisar_clientes.pack(pady=10)
        self.btn_voltar = ttk.Button(self.master, text="Voltar", command=self.voltar)
        self.btn_voltar.pack(pady=10)

    def inicializar_banco(self):
          #Inicializa o banco de dados e cria as tabelas necessárias se não existirem.
        try:
            self.conn = DatabaseManager().conectar()
            self.cursor = self.conn.cursor()

            if not self.cursor:
                raise sqlite3.Error("Falha ao criar cursor")

        except sqlite3.Error as e:
            messagebox.showerror("Erro Fatal", f"Falha na conexão com o banco:\n{str(e)}")
            self.master.destroy()
            raise
        
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT UNIQUE NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                data_venda DATE NOT NULL,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            )
        """)
        self.conn.commit()
    
    def avisar_clientes_para_contato(self):
        # Exibe um aviso para o comerciante com a lista de clientes que fizeram compras há 30 dias.
        # Sugerindo entrar em contato para incentivar nova compra.
       
            self.cursor.execute("SELECT MAX(date(data_venda)) FROM vendas")
            ultima_data = self.cursor.fetchone()[0]

            if ultima_data:
                # Busca todos os clientes que compraram a partir da última venda
                self.cursor.execute("""
                    SELECT DISTINCT c.nome, c.cpf, v.data_venda
                    FROM vendas v
                    JOIN clientes c ON v.cliente_id = c.id
                    WHERE date(v.data_venda) = ?
                """, (ultima_data,))
                clientes = self.cursor.fetchall()

                if clientes:
                    aviso = f"Clientes que compraram na última venda ({ultima_data}):\n\n"
                    for nome, cpf, data in clientes:
                        aviso += f"{nome} (CPF: {cpf}) - Data da compra: {data}\n"
                    messagebox.showinfo("Sugestão de Contato", aviso)
                else:
                    messagebox.showinfo("Sugestão de Contato", "Nenhum cliente encontrado na última venda.")
            else:
                messagebox.showinfo("Sugestão de Contato", "Nenhuma venda registrada.")

    def voltar(self):
        # Fecha a conexão com o banco de dados e fecha a janela atual.
        self.conn.close()
        self.master.destroy()