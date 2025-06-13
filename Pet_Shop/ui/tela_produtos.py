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
        self.master.geometry("1120x600")
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
        self.entry_preco.grid(row=0, column=5, padx=(0,8), sticky="ew")

        tk.Label(frame_form, text="Qtd:").grid(row=0, column=6, sticky='e', padx=(0,2))
        self.entry_quantidade = tk.Entry(frame_form)
        self.entry_quantidade.grid(row=0, column=7, padx=(0,8), sticky="ew")

        self.btn_salvar = tk.Button(frame_form, text="Salvar", command=self.salvar_produto, bg="#4CAF50", fg="white")
        self.btn_salvar.grid(row=0, column=8, padx=(0,8))

        # Campo de busca à direita
        tk.Label(frame_form, text="Buscar:").grid(row=0, column=9, sticky='e', padx=(0,2))
        self.entry_busca = tk.Entry(frame_form)
        self.entry_busca.grid(row=0, column=10, padx=(0,2), sticky="ew")
        self.btn_buscar = tk.Button(frame_form, text="Buscar", command=self.buscar_produtos)
        self.btn_buscar.grid(row=0, column=11, padx=(0,2))

        # Expansão das colunas para melhor ajuste
        for i in range(12):
            frame_form.columnconfigure(i, weight=0)
        frame_form.columnconfigure(1, weight=1)   # Código de Barras
        frame_form.columnconfigure(3, weight=2)   # Nome (maior)
        frame_form.columnconfigure(5, weight=1)   # Preço
        frame_form.columnconfigure(7, weight=1)   # Qtd
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
        self.tree.heading("quantidade", text="Quantidade")
        self.tree.heading("valor_pago", text="Valor Pago")
        self.tree.column("id", width=50, stretch=False)
        self.tree.column("codigo", width=120)
        self.tree.column("nome", width=120)
        self.tree.column("preco", width=80)
        self.tree.column("quantidade", width=80)
        self.tree.column("valor_pago", width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        # Novos campos para Valor Pago
        self.valor_pago_label = tk.Label(self.master, text="Valor Pago:")
        self.valor_pago_label.place(x=650, y=10)  # ajuste as coordenadas
        self.valor_pago_entry = tk.Entry(self.master)
        self.valor_pago_entry.place(x=720, y=10)  # ajuste as coordenadas

        # Ajuste de posições e tamanhos
        self.frame_top = tk.Frame(self.master)
        self.frame_top.place(x=0, y=0, relwidth=1, height=40)

        self.codigo_label = tk.Label(self.frame_top, text="Código de Barras:")
        self.codigo_label.place(x=10, y=10, width=100)
        self.codigo_entry = tk.Entry(self.frame_top)
        self.codigo_entry.place(x=110, y=10, width=80)

        self.nome_label = tk.Label(self.frame_top, text="Nome:")
        self.nome_label.place(x=200, y=10, width=50)
        self.nome_entry = tk.Entry(self.frame_top)
        self.nome_entry.place(x=250, y=10, width=80)

        self.preco_label = tk.Label(self.frame_top, text="Preço:")
        self.preco_label.place(x=340, y=10, width=50)
        self.preco_entry = tk.Entry(self.frame_top)
        self.preco_entry.place(x=390, y=10, width=60)

        self.qtd_label = tk.Label(self.frame_top, text="Qtd:")
        self.qtd_label.place(x=460, y=10, width=40)
        self.qtd_entry = tk.Entry(self.frame_top)
        self.qtd_entry.place(x=500, y=10, width=40)

        self.valor_pago_label = tk.Label(self.frame_top, text="Valor Pago:")
        self.valor_pago_label.place(x=550, y=10, width=70)
        self.valor_pago_entry = tk.Entry(self.frame_top)
        self.valor_pago_entry.place(x=620, y=10, width=60)

        self.salvar_btn = tk.Button(self.frame_top, text="Salvar", command=self.salvar_produto)
        self.salvar_btn.place(x=690, y=10, width=60, height=25)

        self.limpar_valores_pagos_btn = tk.Button(self.frame_top, text="Limpar Valores Pagos", command=self.limpar_valores_pagos)
        self.limpar_valores_pagos_btn.place(x=760, y=10, width=130, height=25)

        self.buscar_label = tk.Label(self.frame_top, text="Buscar:")
        self.buscar_label.place(x=900, y=10, width=50)
        self.buscar_entry = tk.Entry(self.frame_top)
        self.buscar_entry.place(x=950, y=10, width=80)
        self.buscar_btn = tk.Button(self.frame_top, text="Buscar", command=self.buscar_produtos)
        self.buscar_btn.place(x=1040, y=10, width=60, height=25)

        # Crie o frame de botões centralizado na parte inferior
        self.frame_botoes = tk.Frame(self.master)
        self.frame_botoes.pack(side=tk.BOTTOM, pady=10)

        # Botão Editar (azul)
        self.editar_btn = tk.Button(
            self.frame_botoes, text="Editar", bg="#2196F3", fg="white", width=10, command=self.editar_produto
        )
        self.editar_btn.pack(side=tk.LEFT, padx=10)

        # Botão Excluir (vermelho)
        self.excluir_btn = tk.Button(
            self.frame_botoes, text="Excluir", bg="#F44336", fg="white", width=10, command=self.excluir_produto
        )
        self.excluir_btn.pack(side=tk.LEFT, padx=10)

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
                    # Formata o preço com duas casas decimais
                    id_, codigo_barras, nome, preco, quantidade = produto
                    preco_formatado = f"{preco:.2f}"
                    self.tree.insert("", tk.END, values=(id_, codigo_barras, nome, preco_formatado, quantidade))

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
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um produto para excluir.")
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
                    self.entry_quantidade]:
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
            id_, codigo_barras, nome, preco, quantidade = linha
            preco_formatado = f"{preco:.2f}"
            valor_pago = self.valor_pago_entry.get() if self.valor_pago_entry.get() else ""
            self.tree.insert("", "end", values=(id_, codigo_barras, nome, preco_formatado, quantidade, valor_pago))

    def limpar_valores_pagos(self):
        for item in self.tree.get_children():
            valores = list(self.tree.item(item, "values"))
            # Garante que a lista tem 6 elementos (ID, codigo, nome, preco, quantidade, valor_pago)
            while len(valores) < 6:
                valores.append("")
            valores[5] = ""  # índice da coluna "Valor Pago"
            self.tree.item(item, values=valores)