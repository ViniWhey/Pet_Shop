import sqlite3

def conectar():
    """Estabelece conexão com o banco de dados"""
    return sqlite3.connect("petshop.db")

def criar_banco():
    """Cria todas as tabelas necessárias para o sistema PetShop"""
    conn = conectar()
    cursor = conn.cursor()

    try:
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS levantamento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_produto TEXT,
            preco REAL,
            quantidade INTEGER,
            data TEXT
        )
       """)
        # Tabela de usuários (CORREÇÃO: nome da tabela em português para consistência)"""")

        
        # Tabela de clientes (CORREÇÃO: vírgula adicionada após email TEXT)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cliente (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            pet TEXT,
            endereco TEXT           
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            dono_id INTEGER NOT NULL,
            especie TEXT,
            raca TEXT,
            FOREIGN KEY (dono_id) REFERENCES clientes(id)
        )
    """)

        # Tabela de produtos (CORREÇÃO: nome da tabela em português para consistência)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL,
            quantidade INTEGER,
            descricao TEXT
        )
        """)

        # Tabela de serviços
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS servicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id INTEGER,
            tipo_servico TEXT NOT NULL,
            data TEXT NOT NULL,
            valor REAL NOT NULL,
            concluido INTEGER DEFAULT 0,
            observacoes TEXT,
            FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE SET NULL
        )
        """)

        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao criar tabelas: {e}")
    finally:
        conn.close()