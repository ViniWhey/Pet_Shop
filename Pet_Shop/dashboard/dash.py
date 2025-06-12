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
        self.master.state('zoomed')

        # Cores e fontes
        self.bg_color = '#181c2f'
        self.card_bg = '#23284a'
        self.button_bg = '#4682b4'
        self.button_fg = 'white'
        self.button_font = ('Arial', 12, 'bold')
        self.title_font = ('Arial', 18, 'bold')
        self.metric_font = ('Arial', 16, 'bold')
        self.metric_fg = '#fff'

        # Frame principal
        main_frame = tk.Frame(self.master, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- TOPO: Métricas rápidas ---
        top_metrics = tk.Frame(main_frame, bg=self.bg_color)
        top_metrics.pack(fill=tk.X, pady=10, padx=20)

        self.total_vendas_label = tk.Label(top_metrics, text="Total: R$ 0.00",
                                           bg=self.card_bg, fg=self.metric_fg, font=self.metric_font, width=20)
        self.total_vendas_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.media_diaria_label = tk.Label(top_metrics, text="Média diária: R$ 0.00",
                                           bg=self.card_bg, fg=self.metric_fg, font=self.metric_font, width=20)
        self.media_diaria_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.maior_venda_label = tk.Label(top_metrics, text="Maior venda: R$ 0.00",
                                          bg=self.card_bg, fg=self.metric_fg, font=self.metric_font, width=20)
        self.maior_venda_label.pack(side=tk.LEFT, padx=10, pady=5)

        # --- CONTROLES ---
        control_frame = tk.Frame(main_frame, bg=self.bg_color)
        control_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # Período de análise
        tk.Label(control_frame, text="Período:", bg=self.bg_color, 
                font=('Arial', 10)).grid(row=0, column=0, padx=5)
        
        self.periodo_var = tk.StringVar(value="7")
        periodos = [("Último dia", "1"),
                    ("Últimos 7 dias", "7"), 
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
        
        # --- MÉTRICAS DETALHADAS ---
        metrics_frame = tk.Frame(main_frame, bg=self.bg_color)
        metrics_frame.pack(fill=tk.X, pady=10, padx=20)

        self.total_produtos_label = tk.Label(metrics_frame, text="Produtos Vendidos: 0",
                                             bg=self.card_bg, fg=self.metric_fg, font=self.metric_font, width=20)
        self.total_produtos_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.despesas_label = tk.Label(metrics_frame, text="Despesas: R$ 0.00",
                                       bg=self.card_bg, fg=self.metric_fg, font=self.metric_font, width=20)
        self.despesas_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.lucro_liquido_label = tk.Label(metrics_frame, text="Lucro Líquido: R$ 0.00",
                                            bg=self.card_bg, fg=self.metric_fg, font=self.metric_font, width=20)
        self.lucro_liquido_label.pack(side=tk.LEFT, padx=10, pady=5)

        # --- ÁREA CENTRAL: GRÁFICOS E TABELA ---
        center_frame = tk.Frame(main_frame, bg=self.bg_color)
        center_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Frame de gráficos com barra de rolagem (esquerda)
        graphs_canvas = tk.Canvas(center_frame, bg=self.bg_color, highlightthickness=0)
        graphs_scrollbar = tk.Scrollbar(center_frame, orient="vertical", command=graphs_canvas.yview)
        graphs_canvas.configure(yscrollcommand=graphs_scrollbar.set)

        # Use mais espaço para os gráficos, reduzindo o padding lateral
        graphs_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=0)
        graphs_scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        self.graphs_frame = tk.Frame(graphs_canvas, bg=self.bg_color)
        self.graphs_frame.bind(
            "<Configure>",
            lambda e: graphs_canvas.configure(
                scrollregion=graphs_canvas.bbox("all")
            )
        )
        graphs_canvas.create_window((0, 0), window=self.graphs_frame, anchor="nw", width=700)  # Ajuste a largura conforme necessário

        # Frame de tabela (direita) - ocupa menos espaço
        table_frame = tk.Frame(center_frame, bg=self.bg_color, width=350)
        table_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 0), pady=0)
        table_frame.pack_propagate(False)

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

        # Remova o botão de alternar tipo de gráfico principal
        # self.tipo_grafico = tk.StringVar(value="barras")
        # self.botao_grafico = tk.Button(
        #     self.graphs_frame,
        #     text="Mudar para Gráfico de Pizza",
        #     command=self.alternar_grafico,
        #     bg=self.button_bg,
        #     fg=self.button_fg,
        #     font=('Arial', 10, 'bold')
        # )
        # self.botao_grafico.pack(anchor="ne", pady=5, padx=5)

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
                        SELECT data_venda, total, observacoes 
                        FROM vendas 

                        WHERE date(data_venda) BETWEEN ? AND ?
                        ORDER BY data_venda DESC
                    """
                    cursor.execute(query, (data_inicio, data_fim))
                else:
                    query = "SELECT data_venda, total, observacoes FROM vendas ORDER BY data_venda DESC"
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
    
    def obter_total_produtos_vendidos(self, data_inicio, data_fim):
        """Obtém o total de produtos vendidos no período"""
        try:
            with DatabaseManager().conectar() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT SUM(iv.quantidade)
                    FROM itens_venda iv
                    JOIN vendas v ON iv.venda_id = v.id
                    WHERE v.data_venda BETWEEN ? AND ?
                """, (data_inicio, data_fim))
                resultado = cursor.fetchone()
                return resultado[0] if resultado[0] else 0
        except Exception:
            return 0

    def obter_despesas(self, data_inicio, data_fim):
        """Obtém o total de despesas no período"""
        try:
            with DatabaseManager().conectar() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT SUM(valor) FROM despesas
                    WHERE data BETWEEN ? AND ?
                """, (data_inicio, data_fim))
                resultado = cursor.fetchone()
                return float(resultado[0]) if resultado[0] else 0.0
        except Exception:
            return 0.0
    
    def atualizar_dados(self):
        """Atualiza os dados exibidos com base nos filtros selecionados"""
        # Limpa todos os gráficos do frame antes de atualizar os dados
        for widget in self.graphs_frame.winfo_children():
            widget.destroy()

        periodo = self.periodo_var.get()
        
        if periodo == "custom":
            self.custom_frame.grid(row=1, column=0, columnspan=6, pady=10)
            
            data_inicio = self.data_inicio_entry.get().strip()
            data_fim = self.data_fim_entry.get().strip()
            if not data_inicio or not data_fim:
                messagebox.showerror("Erro", "Preencha as duas datas no formato YYYY-MM-DD.")
                return
            try:
                # Aceita apenas o formato YYYY-MM-DD
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

        # Novas métricas
        total_produtos = self.obter_total_produtos_vendidos(data_inicio, data_fim)
        despesas = self.obter_despesas(data_inicio, data_fim)
        lucro_liquido = total - despesas

        self.total_produtos_label.config(text=f"Produtos Vendidos: {total_produtos}")
        self.despesas_label.config(text=f"Despesas: R$ {despesas:,.2f}")
        self.lucro_liquido_label.config(text=f"Lucro Líquido: R$ {lucro_liquido:,.2f}")
        
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
        """Atualiza os gráficos com os dados fornecidos"""
        # Limpa o frame de gráficos
        for widget in self.graphs_frame.winfo_children():
            if isinstance(widget, FigureCanvasTkAgg):
                widget.get_tk_widget().destroy()
            elif isinstance(widget, tk.Label):
                widget.destroy()

        if not dados:
            tk.Label(self.graphs_frame, text="Nenhum dado disponível para o período selecionado",
                     bg=self.bg_color, fg='white').pack(expand=True)
            return

        # --- GRÁFICO 1: BARRAS ---
        vendas_por_dia = {}
        for data, valor, _ in dados:
            if data in vendas_por_dia:
                vendas_por_dia[data] += float(valor)
            else:
                vendas_por_dia[data] = float(valor)

        datas_ordenadas = sorted(vendas_por_dia.keys())
        valores = [vendas_por_dia[data] for data in datas_ordenadas]

        # Aumente o tamanho dos gráficos
        fig1, ax1 = plt.subplots(figsize=(8, 4), dpi=100)
        ax1.bar(datas_ordenadas, valores, color='#4682b4')
        ax1.set_title(f"Vendas por Dia")
        ax1.set_xlabel("Data")
        ax1.set_ylabel("Valor (R$)")
        ax1.tick_params(axis='x', rotation=45)
        fig1.tight_layout()
        canvas1 = FigureCanvasTkAgg(fig1, master=self.graphs_frame)
        canvas1.draw()
        canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=10)

        # --- GRÁFICO 2: LINHA DE TENDÊNCIA ---
        datas_formatadas = [d.split()[0] if " " in d else d for d in datas_ordenadas]

        fig2, ax2 = plt.subplots(figsize=(8, 3), dpi=100)
        ax2.plot(datas_formatadas, valores, marker='o', color='#fbc02d')
        ax2.set_title("Tendência de Vendas")
        ax2.set_xlabel("Data")
        ax2.set_ylabel("Valor (R$)")
        ax2.tick_params(axis='x', rotation=25)
        fig2.tight_layout()
        fig2.autofmt_xdate()
        canvas2 = FigureCanvasTkAgg(fig2, master=self.graphs_frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=10)

        # --- GRÁFICO 3: BARRAS HORIZONTAIS (TOP 5 VENDAS) ---
        top5 = sorted(zip(datas_ordenadas, valores), key=lambda x: x[1], reverse=True)[:5]
        if top5:
            top_datas, top_valores = zip(*top5)
            fig3, ax3 = plt.subplots(figsize=(8, 2.5), dpi=100)
            ax3.barh(top_datas, top_valores, color='#8e24aa')
            ax3.set_title("Top 5 Dias de Venda")
            ax3.set_xlabel("Valor (R$)")
            fig3.tight_layout()
            canvas3 = FigureCanvasTkAgg(fig3, master=self.graphs_frame)
            canvas3.draw()
            canvas3.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=10)

        # --- GRÁFICO 4: PIZZA (Distribuição por Forma de Pagamento) ---
        try:
            with DatabaseManager().conectar() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT forma_pagamento, SUM(total)
                    FROM vendas
                    WHERE date(data_venda) BETWEEN ? AND ?
                    GROUP BY forma_pagamento
                """, (data_inicio, data_fim))
                resultados = cursor.fetchall()
        except Exception:
            resultados = []

        if resultados:
            labels = [row[0] if row[0] else "Desconhecido" for row in resultados]
            valores_fp = [row[1] for row in resultados]
            fig4, ax4 = plt.subplots(figsize=(8, 3.5), dpi=100)
            ax4.pie(valores_fp, labels=labels, autopct='%1.1f%%', startangle=90)
            ax4.set_title("Distribuição das Vendas por Forma de Pagamento")
            fig4.tight_layout()
            canvas4 = FigureCanvasTkAgg(fig4, master=self.graphs_frame)
            canvas4.draw()
            canvas4.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=10)

    def alternar_grafico(self):
        """Alterna entre gráfico de barras e pizza"""
        if self.tipo_grafico.get() == "barras":
            self.tipo_grafico.set("pizza")
            self.botao_grafico.config(text="Mudar para Gráfico de Barras")
        else:
            self.tipo_grafico.set("barras")
            self.botao_grafico.config(text="Mudar para Gráfico de Pizza")
        self.atualizar_dados()  # Redesenha o gráfico

    def plotar_grafico(self, dados):
        """Plota o gráfico conforme o tipo selecionado"""
        # Limpa o frame do gráfico
        for widget in self.graphs_frame.winfo_children():
            if isinstance(widget, FigureCanvasTkAgg):
                widget.get_tk_widget().destroy()

        if not dados:
            return

        datas = [row[0] for row in dados]
        valores = [float(row[1]) for row in dados]

        fig, ax = plt.subplots(figsize=(7, 4))
        if self.tipo_grafico.get() == "barras":
            ax.bar(datas, valores, color="#4682b4")
            ax.set_ylabel("Valor (R$)")
            ax.set_xlabel("Data")
            ax.set_title("Vendas por Dia")
        else:
            ax.pie(valores, labels=datas, autopct='%1.1f%%', startangle=90)
            ax.set_title("Distribuição das Vendas")

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.graphs_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)