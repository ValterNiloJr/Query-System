import sqlite3
import os.path


def init():

	DB_exist = os.path.exists('packeges/database/database.db')

	if not DB_exist:
		conn = sqlite3.connect('packeges/database/database.db')
		cursor = conn.cursor()

		command = '''
		CREATE TABLE IF NOT EXISTS dados (
				idfile int AUTO_INCREMENT NOT NULL,
				file varchar(1000) NOT NULL,
				constraint pk_dados_idfile PRIMARY KEY (idfile)
			);'''
		cursor.execute(command)

		command = '''
			CREATE TABLE IF NOT EXISTS urls (
				idurl int AUTO_INCREMENT NOT NULL,
				url varchar(1000) NOT NULL,
				constraint pk_urls_idurl PRIMARY KEY (idurl)
			);'''
		cursor.execute(command)

		command = '''
			CREATE INDEX IF NOT EXISTS idx_urls_url on urls (url); '''
		cursor.execute(command)

		command = '''
			CREATE TABLE IF NOT EXISTS palavras (
				idpalavra int AUTO_INCREMENT NOT NULL,
				palavra varchar(200) NOT NULL,
				constraint pk_palavras_palavra PRIMARY KEY (idpalavra)
			);'''
		cursor.execute(command)

		command = '''
			CREATE INDEX IF NOT EXISTS idx_palavras_palavra on palavras (palavra)'''
		cursor.execute(command)

		command = '''
			CREATE TABLE IF NOT EXISTS palavra_localizacao (
				idpalavra_localizacao int AUTO_INCREMENT NOT NULL,
				idurl int NOT NULL,
				idpalavra int NOT NULL,
				localizacao int,
				locpalavra varchar(200),
				linhas varchar(500),
				constraint pk_idlinha_localizacao PRIMARY KEY (idpalavra_localizacao),
				constraint fk_linha_localizacao_idurl FOREIGN KEY (idurl) references urls (idurl),
				constraint fk_linha_localizacao_idpalavra FOREIGN KEY (idpalavra) references linhas (idpalavra) 
			); '''
		cursor.execute(command)

		command = '''
			CREATE INDEX IF NOT EXISTS idx_palavra_localizacao_idlinha on palavra_localizacao (idpalavra);'''
		cursor.execute(command)

		#cursor.execute('''ALTER TABLE urls AUTO_INCREMENT = 1;''')
		#cursor.execute('''ALTER TABLE palavras AUTO_INCREMENT = 1;''')
		#cursor.execute('''ALTER TABLE palavra_localizacao AUTO_INCREMENT = 1;''')

		cursor.close()
		conn.close()

	else:
		pass
		#print("Banco de dados já existente")