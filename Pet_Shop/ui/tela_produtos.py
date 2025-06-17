# ui/tela_produtos.py
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from database.db_manager import DatabaseManager
from pathlib import Path

class TelaProdutos:
    def __init__(self, master):
        self.master = master  # Salva o master
        self.master.title("ESTOQUE DE PRODUTOS")
        self.master.state("zoomed")  # Inicia maximizado
        self.configurar_estilos()
        self.criar_widgets()
        self.conn = DatabaseManager().conectar()  # Conecta ao banco de dados
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
        frame_form = tk.Frame(self.master, bd=2, relief=tk.GROOVE, padx=10, pady=5)
        frame_form.pack(fill=tk.X, padx=5, pady=5)

        # Linha única para todos os campos
        tk.Label(frame_form, text="Código de Barras:").grid(row=0, column=0, sticky='e', padx=(0,2))
        self.entry_codigo_barras = tk.Entry(frame_form)
        self.entry_codigo_barras.grid(row=0, column=1, padx=(0,8), sticky="ew")

        tk.Label(frame_form, text="Nome:").grid(row=0, column=2, sticky='e', padx=(0,2))
        self.entry_nome = tk.Entry(frame_form)
        self.entry_nome.grid(row=0, column=3, padx=(0,8), sticky="ew")

        tk.Label(frame_form, text="Preço:").grid(row=0, column=4, sticky='e', padx=(0,2))
        self.entry_preco = tk.Entry(frame_form)
        self.entry_preco.grid(row=0, column=5, padx=(0,5), sticky="ew")

        tk.Label(frame_form, text="Qtd:").grid(row=0, column=6, sticky='e', padx=(0,2))
        self.entry_quantidade = tk.Entry(frame_form)
        self.entry_quantidade.grid(row=0, column=7, padx=(0,5), sticky="ew")

        tk.Label(frame_form, text="Valor Pago:").grid(row=0, column=8, sticky='e', padx=(0,2))
        self.valor_pago_entry = tk.Entry(frame_form)
        self.valor_pago_entry.grid(row=0, column=9, padx=(0,5), sticky="ew")
        # Botão Salvar/Atualizar

        self.btn_salvar = tk.Button(frame_form, text="Salvar(F2)", command=self.salvar_produto, bg="#4CAF50", fg="white")
        self.btn_salvar.grid(row=0, column=10, padx=(10), sticky="ew")

        # Expansão das colunas para melhor ajuste
        for i in range(13):
            frame_form.columnconfigure(i, weight=0)
        frame_form.columnconfigure(1, weight=1)   # Código de Barras
        frame_form.columnconfigure(3, weight=2)   # Nome (maior)
        frame_form.columnconfigure(5, weight=1)   # Preço
        frame_form.columnconfigure(7, weight=1)   # Qtdw
        frame_form.columnconfigure(9, weight=1)   # Valor Pago
        frame_form.columnconfigure(10, weight=1)   # Botão Salvar
        frame_form.columnconfigure(10, weight=1)  # Buscar

        # Treeview (Tabela de produtos)
        self.tree = ttk.Treeview(
            self.master,
            columns=("id", "codigo", "nome", "preco", "quantidade", "valor_pago"),
            show="headings"
        )
        self.tree.heading("id", text="ID")
        self.tree.heading("codigo", text="Código de Barras")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("preco", text="Preço")
        self.tree.heading("quantidade", text="Qtd")
        self.tree.heading("valor_pago", text="Valor Pago")
        
        self.tree.column("id", width=50, stretch=False)
        self.tree.column("codigo", width=120, stretch=False)
        self.tree.column("nome", width=150)
        self.tree.column("preco", width=100, stretch=False)
        self.tree.column("quantidade", width=50, stretch=False)
        self.tree.column("valor_pago", width=100, stretch=False)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Configura a tag para cor de fundo vermelha clara (baixo estoque)
        self.tree.tag_configure("baixo_estoque", background="#f78f8f")

        # Botão Limpar Valores Pagos
        frame_botoes = tk.Frame(self.master, bd=2, relief=tk.GROOVE, padx=10, pady=5)
        frame_botoes.pack(fill=tk.X, padx=5, pady=(0, 5))
        self.frame_botoes = frame_botoes
        
        # Campo de busca
        tk.Label(frame_botoes, text="Buscar:").pack(side=tk.LEFT, padx=(0,2))
        self.entry_busca = tk.Entry(frame_botoes)
        self.entry_busca.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        self.btn_buscar = tk.Button(frame_botoes, text="Buscar", command=self.buscar_produtos)
        self.btn_buscar.pack(side=tk.LEFT, padx=(0,5))
        
        # Botão Editar (azul)
        self.editar_btn = tk.Button(
            self.frame_botoes, text="Editar(F3)", bg="#2196F3", fg="white", width=10, command=self.editar_produto
        )
        self.editar_btn.pack(side=tk.LEFT, padx=10)

        # Botão Excluir (vermelho)
        self.excluir_btn = tk.Button(
            self.frame_botoes, text="Excluir(Delete)", bg="#F81B0C", fg="white", width=10, command=self.excluir_produto
        )
        self.excluir_btn.pack(side=tk.LEFT, padx=10)

        self.master.bind('<F2>', lambda e: self.salvar_produto())
        self.master.bind('<F3>', lambda e: self.editar_produto())
        self.master.bind('<Delete>', lambda e: self.excluir_produto())
        self.master.bind('<Return>', lambda e: self.atualizar_produto(item_id=self.get_selected_item_id()))

    def get_selected_item_id(self):
        """Retorna o ID do item selecionado na Treeview, ou None se nada estiver selecionado."""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            return item['values'][0]


    def salvar_produto(self):
        try:
            codigo_barras = self.entry_codigo_barras.get().strip()
            nome = self.entry_nome.get().strip()
            preco_input = self.entry_preco.get().strip()
            quantidade_input = self.entry_quantidade.get().strip()
            valor_pago_input = self.valor_pago_entry.get().strip()

            preco_str = preco_input.replace(',', '.')
            valor_pago_str = valor_pago_input.replace(',', '.')

            if not codigo_barras or not nome or not preco_input or not quantidade_input or not valor_pago_input:
                messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
                return

            try:
                preco = float(preco_str)
                valor_pago = float(valor_pago_str)
            except ValueError:
                messagebox.showerror("Erro", "Preço e Valor Pago devem ser números válidos.")
                return

            quantidade = int(quantidade_input) if quantidade_input.isdigit() else 0

            db = DatabaseManager()
            conn = db.conectar()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO produtos (codigo_barras, nome, preco, quantidade, valor_pago) VALUES (?, ?, ?, ?, ?)",
                (codigo_barras, nome, preco, quantidade, valor_pago)
            )
            conn.commit()
            messagebox.showinfo("Sucesso", "Produto adicionado!")
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
        try:
            codigo_barras = self.entry_codigo_barras.get().strip()
            nome = self.entry_nome.get().strip()
            preco_input = self.entry_preco.get().strip()
            quantidade_input = self.entry_quantidade.get().strip()
            valor_pago_input = self.valor_pago_entry.get().strip()

            preco_str = preco_input.replace(',', '.')
            valor_pago_str = valor_pago_input.replace(',', '.')

            if not codigo_barras or not nome or not preco_input or not quantidade_input or not valor_pago_input:
                messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
                return

            try:
                preco = float(preco_str)
                valor_pago = float(valor_pago_str)
            except ValueError:
                messagebox.showerror("Erro", "Preço e Valor Pago devem ser números válidos.")
                return

            quantidade = int(quantidade_input) if quantidade_input.isdigit() else 0

            db = DatabaseManager()
            conn = db.conectar()
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE produtos SET codigo_barras=?, nome=?, preco=?, quantidade=?, valor_pago=? WHERE id=?",
                (codigo_barras, nome, preco, quantidade, valor_pago, item_id)
            )
            conn.commit()
            messagebox.showinfo("Sucesso", "Produto atualizado!")
            self.carregar_produtos()
            self.limpar_campos()

        except ValueError as ve:
            messagebox.showerror("Erro", f"Dados inválidos:\n{str(ve)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao atualizar:\n{str(e)}")
        finally:
            if 'conn' in locals():
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
            self.valor_pago_entry.insert(0, dados[5] if dados[5] is not None else "")

            # Altera o botão para "Atualizar"
            self.btn_salvar.config(
                text="Atualizar(Enter)",
                bg="#2196F3",  # Azul para atualizar
                fg="white",
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
            cursor.execute("SELECT id, codigo_barras, nome, preco, quantidade, valor_pago FROM produtos")
            produtos = cursor.fetchall()

            if not produtos:
                self.tree.insert("", tk.END, values=("Nenhum produto cadastrado", "", "", "", ""))
            else:
                for produto in produtos:
                    # Formata o preço com duas casas decimais
                    id_, codigo_barras, nome, preco, quantidade, valor_pago = produto
                    preco_formatado = f"{preco:.2f}"
                    pago_formatado = f"{valor_pago:.2f}" if valor_pago is not None else "0.00"
                    self.tree.insert("", tk.END, values=(id_, codigo_barras, nome, preco_formatado, quantidade, pago_formatado))

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar produtos:\n{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
        self.aviso_estoque()  # Destaca produtos com estoque baixo

    def validar_preco(self, preco_str):
        try:
            preco = float(preco_str)
            return preco >= 0  # Preço não pode ser negativo
        except ValueError:
            return False

    def excluir_produto(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um produto para excluir.")
            return
        
        if not messagebox.askyesno("Confirmação", "Você tem certeza que deseja excluir este produto?"):
            return
        
        item = self.tree.item(selected[0])
        produto_id = item['values'][0]  # Supondo que o ID seja o primeiro valor
        try:
            self.conn.execute("DELETE FROM ITENS_VENDA WHERE produto_id = ?", (produto_id,))
            self.conn.execute("DELETE FROM produtos WHERE id = ?", (produto_id,)) 
            self.conn.commit()
            self.tree.delete(selected[0])
            messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Falha ao excluir:\n{str(e)}")

    def limpar_campos(self):
        for entry in [self.entry_codigo_barras,
                    self.entry_nome,
                    self.entry_preco,
                    self.entry_quantidade,
                    self.valor_pago_entry]:
            entry.delete(0, tk.END)
        self.btn_salvar.config(text="Salvar", bg="#4CAF50")

    def buscar_produtos(self):
        termo = self.entry_busca.get().strip()
        if termo:
            query = """
            SELECT id, codigo_barras, nome, preco, quantidade, valor_pago
            FROM produtos
            WHERE nome LIKE ? OR codigo_barras LIKE ?
            """
            params = (f'%{termo}%', f'%{termo}%')
        else:
            query = "SELECT id, codigo_barras, nome, preco, quantidade, valor_pago FROM produtos"
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
            # Formata o preço com duas casas decimais
            id_, codigo_barras, nome, preco, quantidade, valor_pago = linha
            preco_formatado = f"{preco:.2f}"
            pago_formatado = f"{valor_pago:.2f}" if valor_pago is not None else "0.00"
            # Aplica tag vermelha se quantidade <= 5
            tags = ("baixo_estoque",) if isinstance(quantidade, int) and quantidade <= 5 else ()
            self.tree.insert("", "end", values=(id_, codigo_barras, nome, preco_formatado, quantidade, pago_formatado), tags=tags)

    def limpar_valores_pagos(self):
        for item in self.tree.get_children():
            valores = list(self.tree.item(item, "values"))
            # Garante que a lista tem 6 elementos (ID, codigo, nome, preco, quantidade, valor_pago)
            while len(valores) < 6:
                valores.append("")
            valores[5] = ""  # índice da coluna "Valor Pago"
            self.tree.item(item, values=valores)

    def aviso_estoque(self):
        """Destaca em vermelho as linhas com estoque abaixo de 5 unidades"""
        # Remove tags antigas
        for item in self.tree.get_children():
            self.tree.item(item, tags=())

        for item in self.tree.get_children():
            valores = self.tree.item(item, "values")
            if len(valores) < 5:
                continue
            try:
                if str(valores[4]).isdigit():
                    quantidade = int(valores[4])
                    if quantidade <= 5:
                        self.tree.item(item, tags=("baixo_estoque",))
            except (ValueError, IndexError):
                continue