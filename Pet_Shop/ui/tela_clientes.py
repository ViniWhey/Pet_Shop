import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from database.db_manager import conectar

class TelaClientes:
    def __init__(self, master):
        self.master = master
        self.master.title("PetShop - Gerenciamento de Clientes")
        self.master.geometry("1000x700")
        self.master.resizable(False, False)
        
        # Configuração de estilo
        self.style = ttk.Style()
        self.style.configure('Treeview', rowheight=25)
        self.style.configure('TButton', font=('Arial', 10))
        
        self.cor_principal = '#3a7ff6'
        self.cor_sucesso = '#4CAF50'
        self.cor_perigo = '#f44336'
        
        self.criar_widgets()
        self.carregar_clientes()

    def criar_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Frame de formulário
        frame_form = ttk.LabelFrame(main_frame, text=" Cadastrar/Editar Cliente ")
        frame_form.pack(fill='x', padx=5, pady=5, ipadx=5, ipady=5)

        # Labels e Entries
        campos = [
            ("Nome*:", 'nome'),
            ("Telefone:", 'telefone'),
            ("Pet:", 'pet'),
            ("Endereço:", 'endereco')
        ]
        
        self.entries = {}
        for i, (label, name) in enumerate(campos):
            ttk.Label(frame_form, text=label).grid(row=i, column=0, sticky='e', padx=5, pady=5)
            entry = ttk.Entry(frame_form, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky='ew')
            self.entries[name] = entry

        # Frame de botões do formulário
        frame_botoes_form = ttk.Frame(frame_form)
        frame_botoes_form.grid(row=len(campos), column=0, columnspan=2, pady=10)
        
        ttk.Button(frame_botoes_form, text="Salvar", command=self.salvar_cliente,
                  style='TButton').pack(side='left', padx=5)
        ttk.Button(frame_botoes_form, text="Limpar", command=self.limpar_campos,
                  style='TButton').pack(side='left', padx=5)

        # Frame da lista de clientes
        frame_lista = ttk.LabelFrame(main_frame, text=" Lista de Clientes ")
        frame_lista.pack(fill='both', expand=True, padx=5, pady=5)

        # Treeview com scrollbar
        scroll_y = ttk.Scrollbar(frame_lista)
        scroll_y.pack(side='right', fill='y')

        self.tree = ttk.Treeview(frame_lista, columns=('ID', 'Nome', 'Telefone', 'Pet', 'Endereço'),
                                show='headings', yscrollcommand=scroll_y.set,
                                selectmode='browse')
        
        # Configurar colunas
        colunas = [
            ('ID', 50, 'center'),
            ('Nome', 200, 'w'),
            ('Telefone', 120, 'center'),
            ('Pet', 150, 'w'),
            ('Endereço', 300, 'w')
        ]
        
        for col, width, anchor in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=anchor)

        self.tree.pack(fill='both', expand=True)
        scroll_y.config(command=self.tree.yview)
        
        # Bind duplo clique para edição
        self.tree.bind('<Double-1>', self.editar_cliente)

        # Frame de botões de ação
        frame_botoes_acao = ttk.Frame(main_frame)
        frame_botoes_acao.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(frame_botoes_acao, text="Editar", command=self.editar_cliente,
                  style='TButton').pack(side='left', padx=5)
        ttk.Button(frame_botoes_acao, text="Excluir", command=self.excluir_cliente,
                  style='TButton').pack(side='left', padx=5)
        ttk.Button(frame_botoes_acao, text="Voltar", command=self.master.destroy,
                  style='TButton').pack(side='right', padx=5)

    def carregar_clientes(self):
        """Carrega todos os clientes do banco de dados na treeview"""
        conn = conectar()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nome, telefone, pet, endereco FROM cliente ORDER BY nome""")
            
            # Limpar treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # Preencher com novos dados
            for row in cursor.fetchall():
                self.tree.insert('', 'end', values=row)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar clientes:\n{str(e)}", parent=self.master)
        finally:
            conn.close()

    def validar_campos(self):
        """Valida se os campos obrigatórios foram preenchidos"""
        if not self.entries['nome'].get().strip():
            messagebox.showwarning("Aviso", "O campo Nome é obrigatório!", parent=self.master)
            self.entries['nome'].focus()
            return False
        return True

    def salvar_cliente(self):
        """Salva cliente com pet em ambas as tabelas (clientes e pets)"""
        if not self.validar_campos():
            return

        # Verifica campos mínimos necessários
        campos_necessarios = ['nome', 'telefone', 'pet']
        for campo in campos_necessarios:
            if campo not in self.entries:
                messagebox.showerror("Erro", f"Campo '{campo}' não encontrado!", parent=self.master)
                return

        dados = {
            'nome': self.entries['nome'].get().strip(),
            'telefone': self.entries['telefone'].get().strip(),
            'pet': self.entries['pet'].get().strip(),
            'endereco': self.entries.get('endereco', '').get().strip() if 'endereco' in self.entries else ''
        }

        conn = conectar()
        try:
            cursor = conn.cursor()
            conn.execute("BEGIN TRANSACTION")

            # 1. Insere na tabela clientes (com campo pet simples)
            cursor.execute("""
                INSERT INTO cliente (nome, telefone, pet, endereco)
                VALUES (?, ?, ?, ?)
            """, (dados['nome'], dados['telefone'], dados['pet'], dados['endereco']))

            cliente_id = cursor.lastrowid

            # 2. Insere na tabela pets (com estrutura completa)
            cursor.execute("""
                INSERT INTO pets (nome, dono_id)
                VALUES (?, ?)
            """, (dados['pet'], cliente_id))

            conn.commit()
            messagebox.showinfo("Sucesso", "Cliente e pet salvos com sucesso!", parent=self.master)
            self.limpar_campos()
            self.carregar_clientes()

        except sqlite3.Error as e:
            conn.rollback()
            messagebox.showerror("Erro", f"Falha ao salvar:\n{str(e)}", parent=self.master)
        finally:
            conn.close()

    def editar_cliente(self, event=None):
        """Abre janela para edição do cliente selecionado"""
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente para editar", parent=self.master)
            return
            
        item = self.tree.item(selecionado[0])
        cliente_id = item['values'][0]
        
        # Criar janela de edição
        janela_edicao = tk.Toplevel(self.master)
        janela_edicao.title(f"Editar Cliente ID: {cliente_id}")
        janela_edicao.transient(self.master)
        janela_edicao.grab_set()
        
        # Frame principal
        frame_edicao = ttk.Frame(janela_edicao, padding=10)
        frame_edicao.pack(fill='both', expand=True)
        
        # Campos de edição
        campos_edicao = {}
        for i, (label, name) in enumerate([
            ("Nome*:", 'nome'),
            ("Telefone:", 'telefone'),
            ("Pet:", 'pet'),
            ("Endereço:", 'endereco')
        ]):
            ttk.Label(frame_edicao, text=label).grid(row=i, column=0, sticky='e', padx=5, pady=5)
            entry = ttk.Entry(frame_edicao, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky='ew')
            entry.insert(0, item['values'][i+1])  # +1 para pular o ID
            campos_edicao[name] = entry

        # Botões
        frame_botoes = ttk.Frame(frame_edicao)
        frame_botoes.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(frame_botoes, text="Salvar", 
                 command=lambda: self.salvar_edicao(cliente_id, campos_edicao, janela_edicao),
                 style='TButton').pack(side='left', padx=5)
        ttk.Button(frame_botoes, text="Cancelar", 
                 command=janela_edicao.destroy,
                 style='TButton').pack(side='right', padx=5)

    def salvar_edicao(self, cliente_id, campos, janela):
        """Salva as alterações do cliente editado"""
        dados = {name: entry.get().strip() for name, entry in campos.items()}
        
        if not dados['nome']:
            messagebox.showwarning("Aviso", "O campo Nome é obrigatório!", parent=janela)
            return
            
        conn = conectar()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE cliente 
                SET nome = ?, telefone = ?, pet = ?, endereco = ?
                WHERE id = ?
            """, (dados['nome'], dados['telefone'], dados['pet'], dados['endereco'], cliente_id))
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Cliente atualizado com sucesso!", parent=janela)
            self.carregar_clientes()
            janela.destroy()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao atualizar cliente:\n{str(e)}", parent=janela)
        finally:
            conn.close()

    def excluir_cliente(self):
        """Exclui o cliente selecionado"""
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente para excluir", parent=self.master)
            return
            
        item = self.tree.item(selecionado[0])
        cliente_id, nome = item['values'][0], item['values'][1]
        
        if messagebox.askyesno("Confirmar", f"Excluir o cliente {nome}?", parent=self.master):
            conn = conectar()
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM cliente WHERE id = ?", (cliente_id,))
                conn.commit()
                messagebox.showinfo("Sucesso", "Cliente excluído com sucesso!", parent=self.master)
                self.carregar_clientes()
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao excluir cliente:\n{str(e)}", parent=self.master)
            finally:
                conn.close()

    def limpar_campos(self):
        """Limpa todos os campos do formulário"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)