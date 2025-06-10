# ui/tela_produtos.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.db_manager import conectar

class TelaProdutos:
    def __init__(self, master):
        self.master = master
        self.master.title("Controle de Produtos")
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
        tk.Label(frame_form, text="Nome:").grid(row=0, column=0, sticky='e')
        self.entry_nome = tk.Entry(frame_form, width=30)
        self.entry_nome.grid(row=0, column=1, padx=5)
        
        tk.Label(frame_form, text="Preço:").grid(row=0, column=2, sticky='e')
        self.entry_preco = tk.Entry(frame_form, width=10)
        self.entry_preco.grid(row=0, column=3, padx=5)
        
        tk.Label(frame_form, text="Estoque:").grid(row=0, column=4, sticky='e')
        self.entry_quantidade = tk.Entry(frame_form, width=10)
        self.entry_quantidade.grid(row=0, column=5, padx=5)
        
        # Configurar expansão das colunas
        frame_form.columnconfigure(1, weight=1)
        
        # Botão Salvar (será reconfigurado durante edição)
        self.btn_salvar = tk.Button(frame_form, text="salvar", command=self.salvar_produto)
        self.btn_salvar.grid(row=0, columnspan=6, padx=10)    

        # (com IDs):
        self.tree = ttk.Treeview(
            self.master,
            columns=("ID", "Nome", "Preco", "Estoque"),  # Adicionada coluna ID
            show="headings"  # Mostra os cabeçalhos
        )
        
        # Configurar largura das colunas
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        # Configurar cabeçalhos (nomes das colunas)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Preco", text="Preço")
        self.tree.heading("Estoque", text="Estoque")

        # Configurar largura da coluna ID (opcional)
        self.tree.column("ID", width=50, stretch=False)  # Largura fixa de 50 pixels

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
            nome = self.entry_nome.get().strip()
            preco = float(self.entry_preco.get())
            quantidade = int(self.entry_quantidade.get())
            
            if not nome or preco <= 0 or quantidade < 0:
                raise ValueError("Dados inválidos")
                
            conn = conectar()
            cursor = conn.cursor()
            
            # Verifica se é uma edição (botão estava como "Atualizar")
            if self.btn_salvar['text'] == "Atualizar":
                item_id = self.tree.item(self.tree.selection())['values'][0]
                cursor.execute(
                    "UPDATE produtos SET nome=?, preco=?, quantidade=? WHERE id=?",
                    (nome, preco, quantidade, item_id)
                )
                msg = "Produto atualizado!"
            else:
                cursor.execute(
                    "INSERT INTO produtos (nome, preco, quantidade) VALUES (?, ?, ?)",
                    (nome, preco, quantidade)
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
            conn = conectar()
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

            self.entry_nome.insert(0, dados[1])
            self.entry_preco.insert(0, dados[2])
            self.entry_quantidade.insert(0, dados[3])
            
            # Altera o botão para "Atualizar"
            self.btn_salvar.config(
                text="Atualizar",
                command=lambda: self.atualizar_produto(dados[0])  # Passa o ID
            )

        except Exception as e:
            messagebox.showerror("Erro", f"Falha na edição: {str(e)}")
        
    def carregar_produtos(self):
        """Atualiza a Treeview com os dados do banco"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM produtos")
            
            if not cursor.fetchall():
                self.tree.insert("", tk.END, values=("Nenhum produto cadastrado", "", "", ""))
            else:
                cursor.execute("SELECT * FROM produtos")
                for produto in cursor.fetchall():
                    self.tree.insert("", tk.END, values=produto)
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
            conn = conectar()
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
        """Reseta o formulário e o botão Salvar"""
        for entry in [self.entry_nome, self.entry_preco, self.entry_quantidade]:
            entry.delete(0, tk.END)
        
        self.btn_salvar.config(
            text="Salvar",
            bg="#4CAF50"  # Verde padrão
        )