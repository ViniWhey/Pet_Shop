import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database.db_manager import DatabaseManager  # Supondo que db_manager.py esteja no diretório database

class TelaDashboard:
    def __init__(self, master):
        self.master = master
        self.master.title("Dashboard do Pet Shop - Análise de Vendas")
        self.master.geometry("1200x800")
        self.master.state('zoomed')  # Maximiza a janela
        
        # Configurações de cores e fontes
        self.bg_color = '#f0f8ff'  # Azul claro
        self.button_bg = '#4682b4'  # Azul aço
        self.button_fg = 'white'
        self.button_font = ('Arial', 12, 'bold')
        self.title_font = ('Arial', 18, 'bold')
        
        # Frame principal
        main_frame = tk.Frame(self.master, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_frame = tk.Frame(main_frame, bg=self.bg_color)
        title_frame.pack(fill=tk.X, pady=10)
        
        title_label = tk.Label(title_frame, text="Dashboard de Vendas - Pet Shop", 
                             bg=self.bg_color, font=self.title_font)
        title_label.pack(side=tk.LEFT, padx=20)
        
        # Frame de controles
        control_frame = tk.Frame(main_frame, bg=self.bg_color)
        control_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # Período de análise
        tk.Label(control_frame, text="Período:", bg=self.bg_color, 
                font=('Arial', 10)).grid(row=0, column=0, padx=5)
        
        self.periodo_var = tk.StringVar(value="7")
        periodos = [("Últimos 7 dias", "7"), 
                   ("Últimos 15 dias", "15"), 
                   ("Últimos 30 dias", "30"),
                   ("Personalizado", "custom")]
        
        for i, (text, value) in enumerate(periodos):
            rb = tk.Radiobutton(control_frame, text=text, variable=self.periodo_var, 
                              value=value, bg=self.bg_color, command=self.atualizar_dados)
            rb.grid(row=0, column=i+1, padx=5)
        
        # Frame para datas personalizadas (inicialmente oculto)
        self.custom_frame = tk.Frame(control_frame, bg=self.bg_color)
        
        tk.Label(self.custom_frame, text="De:", bg=self.bg_color).grid(row=0, column=0, padx=5)
        self.data_inicio_entry = tk.Entry(self.custom_frame, width=12)
        self.data_inicio_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(self.custom_frame, text="Até:", bg=self.bg_color).grid(row=0, column=2, padx=5)
        self.data_fim_entry = tk.Entry(self.custom_frame, width=12)
        self.data_fim_entry.grid(row=0, column=3, padx=5)
        
        tk.Button(self.custom_frame, text="Aplicar", command=self.atualizar_dados,
                 bg=self.button_bg, fg=self.button_fg).grid(row=0, column=4, padx=5)
        
        # Botão de atualização
        tk.Button(control_frame, text="Atualizar Dados", command=self.atualizar_dados,
                 bg=self.button_bg, fg=self.button_fg, font=self.button_font).grid(row=0, column=6, padx=20)
        
        # Frame para métricas
        metrics_frame = tk.Frame(main_frame, bg=self.bg_color)
        metrics_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # Métricas (serão atualizadas)
        self.total_vendas_label = tk.Label(metrics_frame, text="Total: R$ 0.00", 
                                         bg=self.bg_color, font=('Arial', 14, 'bold'))
        self.total_vendas_label.pack(side=tk.LEFT, padx=20)
        
        self.media_diaria_label = tk.Label(metrics_frame, text="Média diária: R$ 0.00", 
                                          bg=self.bg_color, font=('Arial', 14, 'bold'))
        self.media_diaria_label.pack(side=tk.LEFT, padx=20)
        
        self.maior_venda_label = tk.Label(metrics_frame, text="Maior venda: R$ 0.00", 
                                        bg=self.bg_color, font=('Arial', 14, 'bold'))
        self.maior_venda_label.pack(side=tk.LEFT, padx=20)
        
        # Frame para gráficos e tabela
        data_frame = tk.Frame(main_frame, bg=self.bg_color)
        data_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Gráfico (esquerda)
        self.graph_frame = tk.Frame(data_frame, bg='white')
        self.graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Tabela (direita)
        table_frame = tk.Frame(data_frame, bg=self.bg_color)
        table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5)
        
        # Treeview para mostrar os dados
        self.tree = ttk.Treeview(table_frame, columns=('Data', 'Valor', 'Descrição'), show='headings')
        self.tree.heading('Data', text='Data')
        self.tree.heading('Valor', text='Valor (R$)')
        self.tree.heading('Descrição', text='Descrição')
        self.tree.column('Data', width=100)
        self.tree.column('Valor', width=100)
        self.tree.column('Descrição', width=200)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Inicializa o banco de dados e carrega os dados
        self.conectar_banco_dados()
        self.atualizar_dados()
        
        # Configura datas padrão
        hoje = datetime.now().strftime('%Y-%m-%d')
        self.data_fim_entry.insert(0, hoje)
        semana_passada = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        self.data_inicio_entry.insert(0, semana_passada)
    
    def conectar_banco_dados(self):
        """Conecta ao banco de dados SQLite"""
        try:
            self.conn = sqlite3.connect('petshop.db')

        except sqlite3.Error as e:
            messagebox.showerror("Erro de Banco de Dados", f"Não foi possível conectar ao banco de dados:\n{str(e)}")
            self.master.destroy()
        
        self.conn.commit()
    
    def obter_dados_vendas(self, data_inicio=None, data_fim=None):
        """Obtém os dados de vendas do banco de dados para o período especificado"""
        try:
            with DatabaseManager().conectar() as conn:
                cursor = conn.cursor()
                
                if data_inicio and data_fim:
                    query = """
                        SELECT data, valor, descricao 
                        FROM levantamento 
                        WHERE data BETWEEN ? AND ?
                        ORDER BY data DESC
                    """
                    cursor.execute(query, (data_inicio, data_fim))
                else:
                    query = "SELECT data, valor, descricao FROM levantamento ORDER BY data DESC"
                    cursor.execute(query)
                
                return cursor.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Falha ao carregar dados:\n{str(e)}", parent=self.master)
            return []
    
    def calcular_metricas(self, dados):
        """Calcula métricas com base nos dados"""
        if not dados:
            return 0.0, 0.0, 0.0
        
        valores = [float(row[1]) for row in dados]
        total = sum(valores)
        media = total / len(valores) if valores else 0
        maior = max(valores) if valores else 0
        
        return total, media, maior
    
    def atualizar_dados(self):
        """Atualiza os dados exibidos com base nos filtros selecionados"""
        periodo = self.periodo_var.get()
        
        if periodo == "custom":
            self.custom_frame.grid(row=1, column=0, columnspan=6, pady=10)
            
            try:
                data_inicio = self.data_inicio_entry.get()
                data_fim = self.data_fim_entry.get()
                
                # Valida as datas
                datetime.strptime(data_inicio, '%Y-%m-%d')
                datetime.strptime(data_fim, '%Y-%m-%d')
                
                dados = self.obter_dados_vendas(data_inicio, data_fim)
            except ValueError:
                messagebox.showerror("Erro", "Formato de data inválido. Use YYYY-MM-DD.")
                return
        else:
            self.custom_frame.grid_forget()
            dias = int(periodo)
            data_fim = datetime.now().strftime('%Y-%m-%d')
            data_inicio = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d')
            dados = self.obter_dados_vendas(data_inicio, data_fim)
        
        # Atualiza a tabela
        self.atualizar_tabela(dados)
        
        # Calcula e exibe as métricas
        total, media, maior = self.calcular_metricas(dados)
        self.total_vendas_label.config(text=f"Total: R$ {total:,.2f}")
        self.media_diaria_label.config(text=f"Média diária: R$ {media:,.2f}")
        self.maior_venda_label.config(text=f"Maior venda: R$ {maior:,.2f}")
        
        # Atualiza o gráfico
        self.atualizar_grafico(dados, data_inicio, data_fim)
    
    def atualizar_tabela(self, dados):
        """Atualiza a tabela com os dados fornecidos"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for row in dados:
            valor_formatado = f"R$ {float(row[1]):,.2f}"
            self.tree.insert('', 'end', values=(row[0], valor_formatado, row[2]))
    
    def atualizar_grafico(self, dados, data_inicio, data_fim):
        """Atualiza o gráfico com os dados fornecidos"""
        # Limpa o frame do gráfico
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        
        if not dados:
            tk.Label(self.graph_frame, text="Nenhum dado disponível para o período selecionado", 
                    bg='white').pack(expand=True)
            return
        
        # Processa os dados para o gráfico
        vendas_por_dia = {}
        for data, valor, _ in dados:
            if data in vendas_por_dia:
                vendas_por_dia[data] += float(valor)
            else:
                vendas_por_dia[data] = float(valor)
        
        # Ordena as datas
        datas_ordenadas = sorted(vendas_por_dia.keys())
        valores = [vendas_por_dia[data] for data in datas_ordenadas]
        
        # Cria a figura do matplotlib
        fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
        
        # Gráfico de barras
        ax.bar(datas_ordenadas, valores, color='#4682b4')
        ax.set_title(f"Vendas por Dia ({data_inicio} a {data_fim})")
        ax.set_xlabel("Data")
        ax.set_ylabel("Valor (R$)")
        ax.tick_params(axis='x', rotation=45)
        
        # Formata o eixo Y para mostrar valores em R$
        ax.yaxis.set_major_formatter('R${x:,.0f}')
        
        # Ajusta o layout
        fig.tight_layout()
        
        # Converte a figura para um widget Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)