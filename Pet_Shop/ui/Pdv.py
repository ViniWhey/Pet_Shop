import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class PontoDeVenda:
    def __init__(self, master):
        self.master = master
        self.master.title("Ponto de Venda - Pet Shop")
        self.master.geometry("1000x700")
        
        # Conexão com o banco de dados
        self.conn = sqlite3.connect("petshop.db")
        self.cursor = self.conn.cursor()
        
        # Carrinho de compras
        self.carrinho = []
        
        # Widgets
        self.criar_widgets()
        self.carregar_produtos()
    
    def criar_widgets(self):
        # Frame principal
        frame_principal = ttk.Frame(self.master)
        frame_principal.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame de produtos (esquerda)
        frame_produtos = ttk.LabelFrame(frame_principal, text="Produtos Disponíveis", padding=10)
        frame_produtos.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Treeview de produtos
        cols = ("ID", "Nome", "Preço", "Estoque", "Descrição")
        self.tree_produtos = ttk.Treeview(frame_produtos, columns=cols, show="headings", height=15)
        for col in cols:
            self.tree_produtos.heading(col, text=col)
            self.tree_produtos.column(col, width=120, anchor="center")
        self.tree_produtos.pack(fill="both", expand=True)
        
        # Botão para adicionar ao carrinho
        btn_add = ttk.Button(frame_produtos, text="Adicionar ao Carrinho", command=self.adicionar_ao_carrinho)
        btn_add.pack(pady=5)
        
        # Frame do carrinho (direita)
        frame_carrinho = ttk.LabelFrame(frame_principal, text="Carrinho de Compras", padding=10)
        frame_carrinho.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Treeview do carrinho
        cols_carrinho = ("Produto", "Preço Unitário", "Quantidade", "Subtotal")
        self.tree_carrinho = ttk.Treeview(frame_carrinho, columns=cols_carrinho, show="headings", height=10)
        for col in cols_carrinho:
            self.tree_carrinho.heading(col, text=col)
            self.tree_carrinho.column(col, width=100, anchor="center")
        self.tree_carrinho.pack(fill="both", expand=True)
        
        # Label do total
        self.label_total = ttk.Label(frame_carrinho, text="Total: R$ 0.00", font=("Arial", 12, "bold"))
        self.label_total.pack(pady=10)
        
        # Botão finalizar venda
        btn_finalizar = ttk.Button(frame_carrinho, text="Finalizar Venda", style="Accent.TButton", command=self.finalizar_venda)
        btn_finalizar.pack(pady=5)
        
        # Configurar grid
        frame_principal.columnconfigure(0, weight=1)
        frame_principal.columnconfigure(1, weight=1)
        frame_principal.rowconfigure(0, weight=1)
    
    def carregar_produtos(self):
        # Limpa a treeview
        for row in self.tree_produtos.get_children():
            self.tree_produtos.delete(row)
        
        # Carrega produtos do banco
        self.cursor.execute("SELECT id, nome, preco, quantidade, descricao FROM produtos WHERE quantidade > 0")
        for row in self.cursor.fetchall():
            self.tree_produtos.insert("", "end", values=row)
    
    def adicionar_ao_carrinho(self):
        item_selecionado = self.tree_produtos.selection()
        if not item_selecionado:
            messagebox.showwarning("Aviso", "Selecione um produto.")
            return
        
        item = self.tree_produtos.item(item_selecionado)
        produto = item["values"]
        
        # Verifica estoque
        if produto[3] <= 0:
            messagebox.showwarning("Sem estoque", "Produto esgotado!")
            return
        
        # Adiciona ao carrinho (ID, Nome, Preço, Quantidade)
        self.carrinho.append({
            "id": produto[0],
            "nome": produto[1],
            "preco": produto[2],
            "quantidade": 1  # Quantidade padrão
        })
        
        self.atualizar_carrinho()
    
    def atualizar_carrinho(self):
        # Limpa o carrinho
        for row in self.tree_carrinho.get_children():
            self.tree_carrinho.delete(row)
        
        # Atualiza com os itens atuais
        total = 0
        for item in self.carrinho:
            subtotal = item["preco"] * item["quantidade"]
            self.tree_carrinho.insert("", "end", values=(
                item["nome"],
                f"R$ {item['preco']:.2f}",
                item["quantidade"],
                f"R$ {subtotal:.2f}"
            ))
            total += subtotal
        
        self.label_total.config(text=f"Total: R$ {total:.2f}")
    
    def finalizar_venda(self):
        if not self.carrinho:
            messagebox.showinfo("Carrinho vazio", "Adicione produtos antes de finalizar.")
            return
        
        # Confirmação
        if not messagebox.askyesno("Confirmar", "Finalizar venda?"):
            return
        
        data_venda = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # Registrar cada item vendido
            for item in self.carrinho:
                # Atualiza estoque
                self.cursor.execute("""
                    UPDATE produtos SET quantidade = quantidade - ?
                    WHERE id = ? AND quantidade >= ?
                """, (item["quantidade"], item["id"], item["quantidade"]))
                
                # Registra na tabela de vendas
                self.cursor.execute("""
                    INSERT INTO vendas (produto_id, nome_produto, preco_unitario, quantidade, total, data)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    item["id"],
                    item["nome"],
                    item["preco"],
                    item["quantidade"],
                    item["preco"] * item["quantidade"],
                    data_venda
                ))
            
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Venda registrada com sucesso!")
            
            # Limpa carrinho e recarrega produtos
            self.carrinho.clear()
            self.atualizar_carrinho()
            self.carregar_produtos()
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Falha ao registrar venda:\n{str(e)}")
            self.conn.rollback()

# --- Uso ---
if __name__ == "__main__":
    root = tk.Tk()
    app = PontoDeVenda(root)
    root.mainloop()