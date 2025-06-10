import sqlite3
from pathlib import Path
from typing import Optional

class DatabaseManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__initialized = False
        return cls._instance
    
    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True
        self.db_path = self._get_db_path()
        self._initialize_db()

    @staticmethod
    def _get_db_path() -> str:
        """Retorna o caminho absoluto para o banco de dados na pasta database"""
        return str(Path(__file__).parent / "petshop.db")

    def _initialize_db(self):
        """Inicializa o banco de dados com todas as tabelas necessárias"""
        with self.conectar() as conn:
            self._criar_tabelas(conn)

    def conectar(self) -> sqlite3.Connection:
        """Estabelece conexão com o banco de dados"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row  # Permite acesso a colunas por nome
        return conn

    def _criar_tabelas(self, conn: sqlite3.Connection):
        """Cria todas as tabelas necessárias"""
        tabelas = {
            'clientes': """
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    pet TEXT,
                    cpf TEXT UNIQUE,
                    telefone TEXT,
                    endereco TEXT,
                    data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP
                )""",
                
            'levantamento': """
                CREATE TABLE IF NOT EXISTS levantamento (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT NOT NULL,
                    valor REAL NOT NULL,
                    descricao TEXT,
                    cliente_id INTEGER,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
                )""",
                
            'pets': """
                CREATE TABLE IF NOT EXISTS pets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    dono_id INTEGER NOT NULL,
                    especie TEXT,
                    raca TEXT,
                    data_nascimento TEXT,
                    FOREIGN KEY (dono_id) REFERENCES clientes(id)
                )""",
                
            'produtos': """
                CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    preco REAL NOT NULL,
                    quantidade INTEGER NOT NULL DEFAULT 0,
                    categoria TEXT,
                    descricao TEXT,
                    codigo_barras TEXT UNIQUE,
                    data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP
                )""",
                
            'servicos': """
                CREATE TABLE IF NOT EXISTS servicos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pet_id INTEGER,
                    cliente_id INTEGER NOT NULL,
                    tipo_servico TEXT NOT NULL,
                    data TEXT NOT NULL,
                    valor REAL NOT NULL,
                    concluido INTEGER DEFAULT 0,
                    observacoes TEXT,
                    FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE SET NULL,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
                )""",
                
            'vendas': """
                CREATE TABLE IF NOT EXISTS vendas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id INTEGER,
                    data_venda TEXT NOT NULL,
                    total REAL NOT NULL,
                    forma_pagamento TEXT NOT NULL,
                    observacoes TEXT,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
                )""",
                
            'itens_venda': """
                CREATE TABLE IF NOT EXISTS itens_venda (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    venda_id INTEGER NOT NULL,
                    produto_id INTEGER NOT NULL,
                    quantidade INTEGER NOT NULL,
                    preco_unitario REAL NOT NULL,
                    subtotal REAL NOT NULL,
                    FOREIGN KEY (venda_id) REFERENCES vendas(id) ON DELETE CASCADE,
                    FOREIGN KEY (produto_id) REFERENCES produtos(id)
                )"""
        }
        
        cursor = conn.cursor()
        for nome, script in tabelas.items():
            try:
                cursor.execute(script)
                print(f"Tabela {nome} criada/verificada com sucesso")
            except sqlite3.Error as e:
                print(f"Erro ao criar tabela {nome}: {str(e)}")
        conn.commit()

    def backup(self, backup_path: Optional[str] = None) -> str:
        """Cria um backup do banco de dados"""
        backup_path = backup_path or str(Path(self.db_path).with_suffix('.bak.db'))
        with self.conectar() as src:
            with sqlite3.connect(backup_path) as dst:
                src.backup(dst)
        return backup_path