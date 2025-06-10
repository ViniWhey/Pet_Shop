import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database.db_manager import DatabaseManager
from datetime import datetime
from tkinter import simpledialog

class PontoDeVenda:
    def __init__(self, master):
        self.master = master
        self.master.title("PetShop PDV - Sistema de Vendas")
        self.master.geometry("1400x800")

        # 1. Primeiro: Inicialize a conexão com o banco
        self.conn = None
        self.cursor = None
        self.inicializar_banco()
        self.corrigir_estoque_nulo()

        # 2. Segundo: Configure os estilos
        self.configurar_estilos()
        
        # 3. Terceiro: Inicialize variáveis
        self.carrinho = []
        self.cliente_atual = None
        
        # 4. Quarto: Crie os widgets
        self.criar_widgets()
        
        # 5. Por último: Carregue os dados
        self.carregar_produtos()
        self.carregar_clientes()

    def inicializar_banco(self):
        """Método robusto para conexão com o banco"""
        try:
            self.conn = DatabaseManager().conectar()
            self.cursor = self.conn.cursor()

            if not self.cursor:
                raise sqlite3.Error("Falha ao criar cursor")

        except sqlite3.Error as e:
            messagebox.showerror("Erro Fatal", f"Falha na conexão com o banco:\n{str(e)}")
            self.master.destroy()
            raise

    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Arial', 10))
        style.configure('Accent.TButton', font=('Arial', 10, 'bold'), foreground='white', background='#4CAF50')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Total.TLabel', font=('Arial', 14, 'bold'))

    def criar_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Frame superior (cliente e busca)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill='x', pady=(0, 10))
        
        # Info cliente
        self.cliente_frame = ttk.LabelFrame(top_frame, text="Cliente", padding=10)
        self.cliente_frame.pack(side='left', fill='x', expand=True)
        
        self.lbl_cliente = ttk.Label(self.cliente_frame, text="Nenhum cliente selecionado")
        self.lbl_cliente.pack(side='left')
        
        btn_selecionar = ttk.Button(self.cliente_frame, text="Selecionar", command=self.selecionar_cliente)
        btn_selecionar.pack(side='left', padx=5)
        
        btn_novo = ttk.Button(self.cliente_frame, text="Novo Cliente", command=self.cadastrar_cliente)
        btn_novo.pack(side='left')
        
        # Busca de produtos
        busca_frame = ttk.LabelFrame(top_frame, text="Buscar Produto", padding=10)
        busca_frame.pack(side='right', fill='x')
        
        self.entry_busca = ttk.Entry(busca_frame, width=30)
        self.entry_busca.pack(side='left')
        self.entry_busca.bind('<Return>', lambda e: self.buscar_produtos())
        
        btn_buscar = ttk.Button(busca_frame, text="Buscar", command=self.buscar_produtos)
        btn_buscar.pack(side='left', padx=5)
        
        # Frame central (produtos e carrinho)
        center_frame = ttk.Frame(main_frame)
        center_frame.pack(fill='both', expand=True)
        
        # Frame de produtos
        produtos_frame = ttk.LabelFrame(center_frame, text="Produtos/Serviços", padding=10)
        produtos_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
        
        # Treeview de produtos
        cols = ("Código", "Nome", "Preço", "Estoque")
        self.tree_produtos = ttk.Treeview(
            produtos_frame, 
            columns=cols, 
            show="headings",
            selectmode='browse',
            height=20
        )
        
        for col in cols:
            self.tree_produtos.heading(col, text=col)
            self.tree_produtos.column(col, width=80, anchor='center')
        
        self.tree_produtos.column("Nome", width=300, anchor='w')
        
        scroll_prod = ttk.Scrollbar(produtos_frame, orient='vertical', command=self.tree_produtos.yview)
        self.tree_produtos.configure(yscrollcommand=scroll_prod.set)
        
        self.tree_produtos.pack(side='left', fill='both', expand=True)
        scroll_prod.pack(side='right', fill='y')
                
        # Frame do carrinho
        carrinho_frame = ttk.LabelFrame(center_frame, text="Carrinho", padding=10)
        carrinho_frame.grid(row=0, column=1, sticky='nsew', padx=(5, 0))
        
        # Treeview do carrinho
        cols_carrinho = ("Produto", "Preço", "Qtd", "Subtotal")
        self.tree_carrinho = ttk.Treeview(
            carrinho_frame,
            columns=cols_carrinho,
            show="headings",
            height=15
        )
        
        for col in cols_carrinho:
            self.tree_carrinho.heading(col, text=col)
            self.tree_carrinho.column(col, width=100, anchor='center')
        
        self.tree_carrinho.column("Produto", width=200, anchor='w')
        
        scroll_carrinho = ttk.Scrollbar(carrinho_frame, orient='vertical', command=self.tree_carrinho.yview)
        self.tree_carrinho.configure(yscrollcommand=scroll_carrinho.set)
        
        self.tree_carrinho.pack(side='top', fill='both', expand=True)
        scroll_carrinho.pack(side='right', fill='y')
        
        # Frame de controle do carrinho
        carrinho_btns_frame = ttk.Frame(carrinho_frame)
        carrinho_btns_frame.pack(fill='x', pady=(5, 0))
        
        btn_remover = ttk.Button(carrinho_btns_frame, text="Remover (Del)", command=self.remover_item)
        btn_remover.pack(side='left', padx=2)
        
        btn_add = ttk.Button(carrinho_btns_frame, text="Add(F2)", command=self.adicionar_ao_carrinho)
        btn_add.pack(side='left', padx=2)
        
        btn_info = ttk.Button(carrinho_btns_frame, text="Detalhes(F3)", command=self.mostrar_detalhes)
        btn_info.pack(side='left', padx=2)

        btn_alterar_qtd = ttk.Button(carrinho_btns_frame, text="Alterar Qtd (F4)", command=self.alterar_quantidade)
        btn_alterar_qtd.pack(side='left', padx=2)
        
        btn_limpar = ttk.Button(carrinho_btns_frame, text="Limpar Carrinho", command=self.limpar_carrinho)
        btn_limpar.pack(side='left', padx=2)

        # Frame do total
        total_frame = ttk.Frame(carrinho_frame)
        total_frame.pack(fill='x', pady=10)
        
        ttk.Label(total_frame, text="Total:", font=('Arial', 12)).pack(side='left')
        self.lbl_total = ttk.Label(total_frame, text="R$ 0.00", font=('Arial', 14, 'bold'))
        self.lbl_total.pack(side='left', padx=10)
        
        # Frame inferior (pagamento)
        bottom_frame = ttk.LabelFrame(main_frame, text="Finalizar Venda", padding=10)
        bottom_frame.pack(fill='x', pady=(10, 0))
        
        # Forma de pagamento
        ttk.Label(bottom_frame, text="Pagamento:").grid(row=0, column=0, sticky='e')
        self.pagamento_var = tk.StringVar()
        self.combo_pagamento = ttk.Combobox(
            bottom_frame,
            textvariable=self.pagamento_var,
            values=["Dinheiro", "Cartão Débito", "Cartão Crédito", "PIX", "Transferência"],
            state='readonly',
            width=15
        )
        self.combo_pagamento.current(0)
        self.combo_pagamento.grid(row=0, column=1, sticky='w', padx=5)
        
        # Observações
        ttk.Label(bottom_frame, text="Observações:").grid(row=0, column=2, sticky='e', padx=(10, 0))
        self.entry_obs = ttk.Entry(bottom_frame, width=40)
        self.entry_obs.grid(row=0, column=3, sticky='we', padx=5)
        
        # Botão finalizar
        btn_finalizar = ttk.Button(
            bottom_frame, 
            text="Finalizar Venda (F5)", 
            style='Accent.TButton',
            command=self.finalizar_venda
        )
        btn_finalizar.grid(row=0, column=4, padx=(20, 0))
        
        # Configurar grid
        center_frame.columnconfigure(0, weight=1)
        center_frame.columnconfigure(1, weight=1)
        center_frame.rowconfigure(0, weight=1)
        
        # Atalhos do teclado
        self.master.bind('<F2>', lambda e: self.adicionar_ao_carrinho())
        self.master.bind('<F3>', lambda e: self.mostrar_detalhes())
        self.master.bind('<F4>', lambda e: self.alterar_quantidade())
        self.master.bind('<F5>', lambda e: self.finalizar_venda())
        self.master.bind('<Delete>', lambda e: self.remover_item())
    
    def carregar_produtos(self, filtro=None):
        try:
            self.tree_produtos.delete(*self.tree_produtos.get_children())
            
            # Adicione a coluna descricao na consulta
            query = """SELECT id, nome, preco, 
                    COALESCE(quantidade, 0) as quantidade, 
                    categoria,
                    descricao 
                    FROM produtos"""
            params = ()
            
            if filtro:
                query += " WHERE (nome LIKE ? OR categoria LIKE ?)"
                params = (f'%{filtro}%', f'%{filtro}%')
            
            self.cursor.execute(query, params)
            
            for row in self.cursor.fetchall():
                # Garante que todos os valores estão corretos
                row = list(row)
                row[2] = float(row[2])  # preco
                row[3] = int(row[3])    # quantidade
                # Se descricao for None, substitui por string vazia
                if row[5] is None:
                    row[5] = ""
                self.tree_produtos.insert('', 'end', values=row[:5])  # Mostra apenas as 5 primeiras colunas
                
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Falha ao carregar produtos:\n{str(e)}")
    
    def carregar_clientes(self):
        self.cursor.execute("SELECT id, nome, cpf FROM clientes ORDER BY nome")
        self.clientes = self.cursor.fetchall()
    
    def buscar_produtos(self):
        termo = self.entry_busca.get().strip()
        self.carregar_produtos(termo if termo else None)
    
    def selecionar_cliente(self):
        if not hasattr(self, 'clientes'):
            self.carregar_clientes()
        
        top = tk.Toplevel(self.master)
        top.title("Selecionar Cliente")
        top.geometry("600x400")
        
        frame = ttk.Frame(top)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Treeview de clientes
        cols = ("ID", "Nome", "CPF")
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        tree.column("Nome", width=250)
        
        scroll = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')
        
        # Preencher com clientes
        for cliente in self.clientes:
            tree.insert('', 'end', values=cliente)
        
        def on_select():
            selected = tree.focus()
            if selected:
                cliente = tree.item(selected)['values']
                self.cliente_atual = {
                    'id': cliente[0],
                    'nome': cliente[1],
                    'cpf': cliente[2]
                }
                self.lbl_cliente.config(text=f"{cliente[1]} (CPF: {cliente[2]})")
                top.destroy()
        
        btn_frame = ttk.Frame(top)
        btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(btn_frame, text="Selecionar", command=on_select).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=top.destroy).pack(side='left')
        
        tree.bind('<Double-1>', lambda e: on_select())
    
    def cadastrar_cliente(self):
        top = tk.Toplevel(self.master)
        top.title("Novo Cliente")
        top.geometry("400x300")
        
        campos = [
            ("Nome:", True),
            ("pet:", False),
            ("CPF:", False),
            ("Telefone:", False),
            ("Endereço:", False)
        ]
        
        entries = {}
        
        for i, (label, obrigatorio) in enumerate(campos):
            ttk.Label(top, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            entry = ttk.Entry(top)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky='we')
            entries[label[:-1].lower()] = entry
        
        def salvar():
            dados = {}
            for campo, entry in entries.items():
                dados[campo] = entry.get().strip()
            
            if not dados['nome']:
                messagebox.showwarning("Aviso", "Nome é obrigatório!", parent=top)
                return
            
            try:
                self.cursor.execute("""
                    INSERT INTO clientes (nome, pet, cpf, telefone, endereco)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    dados['nome'],
                    dados.get('pet', ''),
                    dados.get('cpf'),
                    dados.get('telefone'),
                    dados.get('endereço')
                ))
                
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!", parent=top)
                self.carregar_clientes()
                top.destroy()
                
                # Seleciona o novo cliente automaticamente
                cliente_id = self.cursor.lastrowid
                self.cursor.execute("SELECT nome, cpf FROM clientes WHERE id = ?", (cliente_id,))
                nome, cpf = self.cursor.fetchone()
                self.cliente_atual = {'id': cliente_id, 'nome': nome, 'cpf': cpf}
                self.lbl_cliente.config(text=f"{nome} (CPF: {cpf})")
                
            except sqlite3.IntegrityError:
                messagebox.showerror("Erro", "CPF já cadastrado!", parent=top)
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao cadastrar:\n{str(e)}", parent=top)
        
        btn_frame = ttk.Frame(top)
        btn_frame.grid(row=len(campos)+1, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Salvar", command=salvar).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=top.destroy).pack(side='left')
        
        top.columnconfigure(1, weight=1)
    
    def adicionar_ao_carrinho(self):
        selected = self.tree_produtos.focus()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um produto para adicionar ao carrinho.")
            return

        produto = self.tree_produtos.item(selected)['values']

        try:
            if not all(produto[:4]):  # Corrigido para os 4 primeiros campos
                raise ValueError("Produto com dados incompletos.")

            produto_id = int(produto[0])
            nome = str(produto[1])  # Corrigido
            preco = float(produto[2])  # Corrigido
            estoque = int(produto[3]) if produto[3] not in (None, '', 'None') else 0  # Corrigido

            # Já no carrinho? Verifica se ainda há estoque para adicionar mais
            for item in self.carrinho:
                if item['id'] == produto_id:
                    if item['quantidade'] + 1 > estoque:
                        messagebox.showwarning(
                            "Estoque insuficiente",
                            f"Não há estoque suficiente para adicionar mais unidades de '{nome}'."
                        )
                        return
                    if self.alterar_quantidade_item(item, incremento=1):
                        self.atualizar_carrinho()
                    return

            # Verifica se há estoque suficiente para adicionar o produto novo
            if estoque <= 0:
                messagebox.showwarning("Estoque insuficiente", f"O produto '{nome}' está sem estoque.")
                return

            novo_item = {
                'id': produto_id,
                'nome': nome,
                'preco': preco,
                'quantidade': 1,
                'estoque': estoque
            }

            self.carrinho.append(novo_item)
            self.atualizar_carrinho()

        except (ValueError, TypeError) as e:
            messagebox.showerror("Erro", f"Dados do produto inválidos: {str(e)}")


    def corrigir_estoque_nulo(self):
        """Corrige registros com estoque nulo no banco de dados"""
        try:
            self.cursor.execute("UPDATE produtos SET quantidade = 0 WHERE quantidade IS NULL")
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showwarning("Aviso", f"Não foi possível corrigir estoques nulos: {str(e)}")        
    
    def alterar_quantidade_item(self, item, incremento=None, nova_quantidade=None):
        """Função auxiliar para alterar quantidade de um item com tratamento robusto"""
        try:
            # Conversão segura dos valores
            estoque = int(item.get('estoque', 0))
            quantidade_atual = int(item.get('quantidade', 0))
            
            if nova_quantidade is not None:
                nova_quantidade = int(nova_quantidade)
                if nova_quantidade <= 0:
                    return False
                
                if estoque > 0 and nova_quantidade > estoque:
                    messagebox.showwarning("Estoque", f"Quantidade indisponível! Máximo: {estoque}")
                    return False
                
                item['quantidade'] = nova_quantidade
                return True
            
            elif incremento is not None:
                incremento = int(incremento)
                nova_qtd = quantidade_atual + incremento
                
                if nova_qtd <= 0:
                    return False
                    
                if estoque > 0 and nova_qtd > estoque:
                    messagebox.showwarning("Estoque", f"Quantidade indisponível! Máximo: {estoque}")
                    return False
                    
                item['quantidade'] = nova_qtd
                return True
            
            return False
        
        except (ValueError, TypeError) as e:
            messagebox.showerror("Erro", f"Valor inválido na quantidade: {str(e)}")
            return False

    def alterar_quantidade(self):
        """Função principal para alterar quantidade via diálogo com tratamento completo"""
        selected = self.tree_carrinho.focus()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um item do carrinho para alterar a quantidade.")
            return
        
        try:
            index = self.tree_carrinho.index(selected)
            item = self.carrinho[index]
            
            # Garantir tipos corretos
            estoque = int(item.get('estoque', 0))
            quantidade_atual = int(item.get('quantidade', 1))
            
            nova_qtd = simpledialog.askinteger(
                "Alterar Quantidade",
                f"Nova quantidade para {item.get('nome', 'Produto')}:",
                parent=self.master,
                minvalue=1,
                maxvalue=estoque if estoque > 0 else None,
                initialvalue=quantidade_atual
            )
            
            if nova_qtd is not None and nova_qtd != quantidade_atual:
                if self.alterar_quantidade_item(item, nova_quantidade=nova_qtd):
                    self.atualizar_carrinho()
        
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao alterar quantidade: {str(e)}")

    def remover_item(self):
        selected = self.tree_carrinho.focus()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um item para remover.")
            return
        
        index = self.tree_carrinho.index(selected)
        self.carrinho.pop(index)
        self.atualizar_carrinho()
    
    def limpar_carrinho(self):
        if not self.carrinho:
            return
            
        if messagebox.askyesno("Confirmar", "Deseja limpar todo o carrinho?"):
            self.carrinho.clear()
            self.atualizar_carrinho()
    
    def atualizar_carrinho(self):
        self.tree_carrinho.delete(*self.tree_carrinho.get_children())
        total = 0.0
        
        for item in self.carrinho:
            try:
                # Conversão segura de valores
                preco = float(item.get('preco', 0))
                quantidade = int(item.get('quantidade', 0))
                subtotal = preco * quantidade
                total += subtotal
                
                self.tree_carrinho.insert('', 'end', values=(
                    item.get('nome', ''),
                    f"R$ {preco:.2f}",
                    quantidade,
                    f"R$ {subtotal:.2f}"
                ))
            except (ValueError, TypeError) as e:
                messagebox.showerror("Erro", f"Item inválido no carrinho: {str(e)}")
                continue
        
        self.lbl_total.config(text=f"R$ {total:.2f}")
        
    def mostrar_detalhes(self):
        selected = self.tree_produtos.focus()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um produto para ver os detalhes.")
            return
        
        produto = self.tree_produtos.item(selected)['values']
        produto_id = produto[0]
        
        try:
            # Busca todas as informações do produto, incluindo descrição
            self.cursor.execute("""
                SELECT id, nome, preco, COALESCE(quantidade, 0), 
                    categoria, COALESCE(descricao, 'Sem descrição cadastrada') 
                FROM produtos WHERE id = ?
            """, (produto_id,))
            
            produto_completo = self.cursor.fetchone()
            
            if produto_completo:
                messagebox.showinfo(
                    "Detalhes do Produto",
                    f"ID: {produto_completo[0]}\n"
                    f"Nome: {produto_completo[1]}\n"
                    f"Preço: R$ {float(produto_completo[2]):.2f}\n"
                    f"Estoque: {int(produto_completo[3])}\n"
                    f"Categoria: {produto_completo[4]}\n\n"
                    f"Descrição:\n{produto_completo[5]}",
                    parent=self.master
                )
            else:
                messagebox.showerror("Erro", "Produto não encontrado no banco de dados.")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao obter detalhes:\n{str(e)}")
    
    def finalizar_venda(self):
        if not self.carrinho:
            messagebox.showwarning("Aviso", "O carrinho está vazio.")
            return
        
        if not self.combo_pagamento.get():
            messagebox.showwarning("Aviso", "Selecione uma forma de pagamento.")
            return
        
        total = sum(item['preco'] * item['quantidade'] for item in self.carrinho)
        
        # Confirmação
        resumo = "\n".join(
            f"{item['nome']} - {item['quantidade']} x R$ {item['preco']:.2f} = R$ {item['preco'] * item['quantidade']:.2f}"
            for item in self.carrinho
        )
        
        msg = (
            f"Cliente: {self.cliente_atual['nome'] if self.cliente_atual else 'Não informado'}\n"
            f"Total: R$ {total:.2f}\n"
            f"Pagamento: {self.combo_pagamento.get()}\n\n"
            "Itens:\n" + resumo + "\n\n"
            "Confirmar venda?"
        )
        
        if not messagebox.askyesno("Confirmar Venda", msg, parent=self.master):
            return
        
        try:
            data_venda = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cliente_id = self.cliente_atual['id'] if self.cliente_atual else None
            
            # Registrar venda
            self.cursor.execute("""
                INSERT INTO vendas (
                    cliente_id, 
                    data_venda, 
                    total, 
                    forma_pagamento, 
                    observacoes
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                cliente_id,
                data_venda,
                total,
                self.combo_pagamento.get(),
                self.entry_obs.get().strip()
            ))
            
            venda_id = self.cursor.lastrowid
            
            # Registrar itens
            for item in self.carrinho:
                self.cursor.execute("""
                    INSERT INTO itens_venda (
                        venda_id,
                        produto_id,
                        quantidade,
                        preco_unitario,
                        subtotal
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    venda_id,
                    item['id'],
                    item['quantidade'],
                    item['preco'],
                    item['preco'] * item['quantidade']
                ))
                
                # Atualizar estoque
                self.cursor.execute("""
                    UPDATE produtos 
                    SET quantidade = quantidade - ?
                    WHERE id = ?
                """, (item['quantidade'], item['id']))
            
            self.conn.commit()
            
            # Emitir recibo (opcional)
            self.emitir_recibo(venda_id)
            
            messagebox.showinfo(
                "Sucesso", 
                f"Venda registrada com sucesso!\nNúmero: {venda_id}",
                parent=self.master
            )
            
            # Limpar para nova venda
            self.carrinho.clear()
            self.atualizar_carrinho()
            self.carregar_produtos()
            self.entry_obs.delete(0, 'end')
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror(
                "Erro", 
                f"Falha ao registrar venda:\n{str(e)}", 
                parent=self.master
            )
    
    def emitir_recibo(self, venda_id):
        """Gera um recibo simples da venda"""
        try:
            self.cursor.execute("""
                SELECT v.data_venda, v.total, v.forma_pagamento, 
                       c.nome as cliente_nome, c.cpf as cliente_cpf
                FROM vendas v
                LEFT JOIN clientes c ON v.cliente_id = c.id
                WHERE v.id = ?
            """, (venda_id,))
            venda = self.cursor.fetchone()
            
            self.cursor.execute("""
                SELECT p.nome, iv.quantidade, iv.preco_unitario, iv.subtotal
                FROM itens_venda iv
                JOIN produtos p ON iv.produto_id = p.id
                WHERE iv.venda_id = ?
                ORDER BY iv.id
            """, (venda_id,))
            itens = self.cursor.fetchall()
            
            # Criar janela de recibo
            recibo_win = tk.Toplevel(self.master)
            recibo_win.title(f"Recibo #{venda_id}")
            recibo_win.geometry("400x600")
            
            frame = ttk.Frame(recibo_win)
            frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Cabeçalho
            ttk.Label(
                frame, 
                text="Pet Shop - Recibo de Venda", 
                font=('Arial', 14, 'bold')
            ).pack(pady=(0, 10))
            
            ttk.Label(
                frame, 
                text=f"Nº {venda_id} - {datetime.strptime(venda[0], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M')}"
            ).pack()
            
            # Cliente
            ttk.Label(frame, text="-"*50).pack(pady=5)
            ttk.Label(frame, text="CLIENTE:", font=('Arial', 10, 'bold')).pack(anchor='w')
            
            if venda[3]:  # Nome do cliente
                ttk.Label(frame, text=f"{venda[3]}", font=('Arial', 10)).pack(anchor='w')
                if venda[4]:  # CPF
                    ttk.Label(frame, text=f"CPF: {venda[4]}").pack(anchor='w')
            else:
                ttk.Label(frame, text="Consumidor não identificado").pack(anchor='w')
            
            # Itens
            ttk.Label(frame, text="-"*50).pack(pady=5)
            ttk.Label(frame, text="ITENS:", font=('Arial', 10, 'bold')).pack(anchor='w')
            
            for item in itens:
                ttk.Label(
                    frame, 
                    text=f"{item[0]} - {item[1]} x R$ {item[2]:.2f} = R$ {item[3]:.2f}",
                    anchor='w'
                ).pack(fill='x')
            
            # Total
            ttk.Label(frame, text="-"*50).pack(pady=5)
            ttk.Label(
                frame, 
                text=f"TOTAL: R$ {venda[1]:.2f}", 
                font=('Arial', 12, 'bold')
            ).pack(anchor='e')
            
            ttk.Label(
                frame, 
                text=f"Pagamento: {venda[2]}",
                font=('Arial', 10)
            ).pack(anchor='e', pady=(0, 20))
            
            # Botão imprimir/fechar
            btn_frame = ttk.Frame(frame)
            btn_frame.pack(fill='x', pady=10)
            
            ttk.Button(
                btn_frame, 
                text="Imprimir", 
                command=lambda: self.imprimir_recibo(recibo_win, venda_id)
            ).pack(side='left', padx=5)
            
            ttk.Button(
                btn_frame, 
                text="Fechar", 
                command=recibo_win.destroy
            ).pack(side='left')
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar recibo:\n{str(e)}", parent=self.master)
    
    def imprimir_recibo(self, janela, venda_id):
        """Implementação básica para impressão (pode ser expandida)"""
        messagebox.showinfo(
            "Imprimir", 
            f"Recibo #{venda_id} enviado para impressora\n"
            "(Implemente a lógica de impressão conforme necessário)",
            parent=janela
        )