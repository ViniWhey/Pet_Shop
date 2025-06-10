# ui/tela_produtos.py
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from database.db_manager import DatabaseManager
from pathlib import Path

class TelaProdutos:
    def __init__(self, master):
        self.master = master
        self.master.title("ESTOQUE DE PRODUTOS")
        self.master.geometry("1100x600")
        self.configurar_estilos()
        self.criar_widgets()
        self.carregar_produtos()
        
    def configurar_estilos(self):
        style = ttk.Style()
        
        # Cores modernas
        style.theme_use('clam')  # Tema mais atual que o padrão
        
        # Treeview
        style.configure("Treeview", 
                    rowheight=25,
                    background="#ffffff",
                    fieldbackground="#ffffff")
        style.map("Treeview", 
                background=[('selected', '#0078d7')])  # Cor da seleção
        
        # Frame
        style.configure("TFrame", 
                    background="#f5f5f5",
                    borderwidth=2,
                    relief="groove")
        
        # Botões
        style.configure("TButton",
                    padding=6,
                    font=('Segoe UI', 9))
        style.map("TButton",
                background=[('active', '#e1e1e1')])  

    def criar_widgets(self):
        
        # Frame do formulário (FIXO no topo)
        frame_form = tk.Frame(self.master, bd=2, relief=tk.GROOVE, padx=10, pady=10)
        frame_form.pack(fill=tk.X, padx=5, pady=5)
        
        # Campos de entrada
        tk.Label(frame_form, text="codigo de barras:").grid(row=0, column=0, sticky='e')
        self.entry_codigo_barras = tk.Entry(frame_form, width=45)
        self.entry_codigo_barras.grid(row=0, column=1, padx=5)

        tk.Label(frame_form, text="Nome do Produto:").grid(row=0, column=1, sticky='e') 
        self.entry_nome = tk.Entry(frame_form, width=30)
        self.entry_nome.grid(row=0, column=2, padx=5)
        
        tk.Label(frame_form, text="Preço:").grid(row=0, column=2, sticky='e')
        self.entry_preco = tk.Entry(frame_form, width=10)
        self.entry_preco.grid(row=0, column=3, padx=5)
        
        tk.Label(frame_form, text="Quantidade:").grid(row=0, column=4, sticky='e')
        self.entry_quantidade = tk.Entry(frame_form, width=10)
        self.entry_quantidade.grid(row=0, column=5, padx=5)
        
        # Configurar expansão das colunas
        frame_form.columnconfigure(1, weight=1)
        
        #buscar produtos
        tk.Label(frame_form, text="Buscar:").grid(row=0, column=7, sticky='e')
        self.entry_busca = tk.Entry(frame_form, width=20)
        self.entry_busca.grid(row=0, column=8, padx=5)
        
        self.btn_buscar = tk.Button(frame_form, text="Buscar", command=self.buscar_produtos)
        self.btn_buscar.grid(row=0, column=9, padx=5)
        
        # Configurar expansão das colunas
        frame_form.columnconfigure(8, weight=1)  # Expande a coluna de busca
        frame_form.columnconfigure(9, weight=0)  # Não expande o botão de busca
        
        # Botão Salvar (será reconfigurado durante edição)
        self.btn_salvar = tk.Button(frame_form, text="salvar", command=self.salvar_produto)
        self.btn_salvar.grid(row=0, column=6, padx=10)    

        # (com IDs):
        self.tree = ttk.Treeview(
            self.master,
            columns=("ID", "codigo_barras", "Nome", "Preco", "Quantidade"),  # Adicionada coluna ID
            show="headings"  # Mostra os cabeçalhos
        )
        
        # Configurar largura das colunas
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        # Configurar cabeçalhos (nomes das colunas)
        self.tree.heading("ID", text="ID")
        self.tree.heading("codigo_barras", text="Código de Barras")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Preco", text="Preço")
        self.tree.heading("Quantidade", text="Quantidade")

        # Configurar largura da coluna ID (opcional)
        self.tree.column("ID", width=50, stretch=False)  # Largura fixa de 50 pixels
        self.tree.column("codigo_barras", width=75, stretch=True)  # Largura expansível
        self.tree.column("Nome", width=200, stretch=True)
        self.tree.column("Preco", width=100, stretch=False)  # Largura fixa de 100 pixels
        self.tree.column("Quantidade", width=100, stretch=False)

        self.tree.pack(fill=tk.BOTH, expand=True)

    # Botões de ação
        frame_botoes = tk.Frame(self.master)
        frame_botoes.pack(pady=5)
        
        btn_editar = tk.Button(
            frame_botoes, 
            text="Editar", 
            command=self.editar_produto,
            bg="#2196F3", fg="white"
        )
        btn_excluir = tk.Button(
            frame_botoes, 
            text="Excluir", 
            command=self.excluir_produto,
            bg="#F44336", fg="white"
        )
        btn_editar.pack(side=tk.LEFT, padx=5)
        btn_excluir.pack(side=tk.LEFT, padx=5)    

    def salvar_produto(self):
        """Salva ou atualiza um produto (adaptado para pegar valores dos campos)"""
        try:
            codigo_barras = self.entry_codigo_barras.get().strip()
            nome = self.entry_nome.get().strip()
            preco = float(self.entry_preco.get())
            quantidade = int(self.entry_quantidade.get())
            
            if not nome or preco <= 0 or quantidade < 0:
                raise ValueError("Dados inválidos")
                
            db = DatabaseManager()
            conn = db.conectar()
            cursor = conn.cursor()
            
            # Verifica se é uma edição (botão estava como "Atualizar")
            if self.btn_salvar['text'] == "Atualizar":
                item_id = self.tree.item(self.tree.selection())['values'][0]
                cursor.execute(
                    "UPDATE produtos SET codigo_barras=?, nome=?, preco=?, quantidade=? WHERE id=?",
                    (codigo_barras, nome, preco, quantidade, item_id)
                )
                msg = "Produto atualizado!"
            else:
                cursor.execute(
                    "INSERT INTO produtos (codigo_barras, nome, preco, quantidade) VALUES (?, ?, ?, ?)",
                    (codigo_barras, nome, preco, quantidade)
                )
                msg = "Produto adicionado!"
                
            conn.commit()
            messagebox.showinfo("Sucesso", msg)
            self.carregar_produtos()
            self.limpar_campos()
            
        except ValueError as ve:
            messagebox.showerror("Erro", f"Dados inválidos:\n{str(ve)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar:\n{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()  

    def atualizar_produto(self, item_id):
        if not self.validar_preco(self.entry_preco.get()):
            return

        conn = None
        try:
            db = DatabaseManager()
            conn = db.conectar()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE produtos SET nome=?, preco=?, quantidade=? WHERE id=?",
                (
                    self.entry_nome.get(),
                    float(self.entry_preco.get()),
                    int(self.entry_quantidade.get()),
                    item_id
                )
            )
            conn.commit()
            messagebox.showinfo("Sucesso", "Produto atualizado!")

            # Restaurar estado padrão
            self.btn_salvar.config(command=self.salvar_produto, text="Salvar")
            self.limpar_campos()
            self.carregar_produtos()

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao atualizar: {str(e)}")
        finally:
            if conn:
                conn.close()

    def editar_produto(self):
        try:
            selecionado = self.tree.selection()
            if not selecionado:
                messagebox.showwarning("Aviso", "Nenhum produto selecionado!")
                return

            dados = self.tree.item(selecionado)['values']
            # Preenche o formulário FIXO
            self.limpar_campos()

            self.entry_codigo_barras.insert(0, dados[1])
            self.entry_nome.insert(0, dados[2])
            self.entry_preco.insert(0, dados[3])
            self.entry_quantidade.insert(0, dados[4])
            
            # Altera o botão para "Atualizar"
            self.btn_salvar.config(
                text="Atualizar",
                command=lambda: self.atualizar_produto(dados[0])  # Passa o ID
            )

        except Exception as e:
            messagebox.showerror("Erro", f"Falha na edição: {str(e)}")
        
    def carregar_produtos(self):
        self.tree.delete(*self.tree.get_children())
        try:
            db = DatabaseManager()
            conn = db.conectar()
            cursor = conn.cursor()

            cursor.execute("SELECT id, codigo_barras, nome, preco, quantidade FROM produtos")
            produtos = cursor.fetchall()

            if not produtos:
                self.tree.insert("", tk.END, values=("Nenhum produto cadastrado", "", "", "", ""))
            else:
                for produto in produtos:
                    # Converte para tupla explícita, se necessário
                    self.tree.insert("", tk.END, values=tuple(produto))

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar produtos:\n{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()


    def validar_preco(self, preco_str):
        try:
            preco = float(preco_str)
            return preco >= 0  # Preço não pode ser negativo
        except ValueError:
            return False

    def excluir_produto(self):
        """Remove o produto selecionado"""
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um produto!")
            return
            
        if not messagebox.askyesno("Confirmar", "Excluir este produto permanentemente?"):
            return
            
        try:
            item_id = self.tree.item(selecionado)['values'][0]
            db = DatabaseManager()
            conn = db.conectar()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM produtos WHERE id=?", (item_id,))
            conn.commit()
            self.carregar_produtos()
            messagebox.showinfo("Sucesso", "Produto excluído!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao excluir:\n{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    def limpar_campos(self):
        for entry in [self.entry_codigo_barras,
                    self.entry_nome,
                    self.entry_preco,
                    self.entry_quantidade]:
            entry.delete(0, tk.END)
        self.btn_salvar.config(text="Salvar", bg="#4CAF50")

    def buscar_produtos(self):
        termo = self.entry_busca.get().strip()
        if termo:
            query = """
            SELECT id, codigo_barras, nome, preco, quantidade
            FROM produtos
            WHERE nome LIKE ? OR codigo_barras LIKE ?
            """
            params = (f'%{termo}%', f'%{termo}%')
        else:
            query = "SELECT id, codigo_barras, nome, preco, quantidade FROM produtos"
            params = ()

        caminho_db = Path(__file__).resolve().parent.parent / "database" / "petshop.db"
        conexao = sqlite3.connect(caminho_db)
        cursor = conexao.cursor()
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        conexao.close()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for linha in resultados:
            self.tree.insert("", "end", values=linha)