#from sqlite3 import Error
import pdfplumber
from packeges.database.database import init
import pandas as pd
import sqlite3
import codecs
import nltk
import re
import os

def data_insert(fileid, file):
    #part = [p for p in file.split('/')]
    conn = sqlite3.connect(
        'packeges/database/database.db', isolation_level=None)
    cursor = conn.cursor()
    countId = cursor.execute("SELECT COUNT(*) FROM dados").fetchone()[0]+1
    cursor.execute(
        '''INSERT INTO dados (idfile, file) VALUES (?,?)''', (fileid, file,))
    cursor.close()
    conn.close()


def word_separate(text):
    stop = nltk.corpus.stopwords.words('portuguese')
    splitter = re.compile('\\W+')
    lista_linhas = []
    lista = [p for p in splitter.split(text) if p != '']
    for p in lista:
        if p.lower() not in stop:
            if len(p) > 1:
                lista_linhas.append(p)
                # lista_linhas.append(p.lower())
    return lista_linhas


def file_index(url):
    retorno = -1
    conn = sqlite3.connect('packeges/database/database.db')
    cursorUrl = conn.cursor()
    rowcount_urls = cursorUrl.execute(
        "SELECT COUNT(url) FROM urls WHERE url = ?", (url,)).fetchone()[0]
    cursorUrl.execute('''
		SELECT idurl FROM urls WHERE url = ?
	''', (url,))
    if (rowcount_urls > 0):
        #print("url cadastrada")
        idurl = cursorUrl.fetchone()[0]
        cursorPalavra = conn.cursor()
        rowcount_palavras = cursorPalavra.execute(
            "SELECT COUNT(idurl) FROM palavra_localizacao WHERE idurl = ?", (idurl,)).fetchone()[0]
        cursorPalavra.execute('''
			SELECT idurl FROM palavra_localizacao WHERE idurl = ?
			''', (idurl,))

        if (rowcount_palavras > 0):
            #print("Url com palavras")
            retorno = -2  # existe a página com palavras cadastradas
        else:
            #print("Url sem palavras")
            retorno = idurl  # existe a página cadastrada mas sem palavras

        cursorPalavra.close()
    # else:
        #print("url não cadastrada")

    cursorUrl.close()
    conn.close()

    return retorno


def file_insert(url):
    conn = sqlite3.connect(
        'packeges/database/database.db', isolation_level=None)
    cursorArq = conn.cursor()
    countId = (cursorArq.execute("SELECT COUNT(*) FROM urls").fetchone()[0])+1
    cursorArq.execute(
        '''INSERT INTO urls (idurl, url) VALUES (?,?)''', (countId, url,))
    idarquivo = cursorArq.lastrowid
    cursorArq.close()
    conn.close()

    return idarquivo


def word_index(word):
    retorno = -1  # não existe a palavra no índice
    conn = sqlite3.connect('packeges/database/database.db')
    cursorWord = conn.cursor()
    rowcount_word = cursorWord.execute(
        "SELECT COUNT(palavra) FROM palavras WHERE palavra = ?", (word,)).fetchone()[0]
    cursorWord.execute('''
		SELECT idpalavra FROM palavras WHERE palavra = ?
		''', (word,))

    if rowcount_word > 0:
        # print('sim')
        retorno = cursorWord.fetchone()[0]
    # else:
        # print('não')

    cursorWord.close()
    conn.close()

    return retorno


def word_insert(word):
    conn = sqlite3.connect(
        'packeges/database/database.db', isolation_level=None)
    cursorWord = conn.cursor()
    countId = cursorWord.execute(
        "SELECT COUNT(*) FROM palavras").fetchone()[0]+1
    cursorWord.execute('''
		INSERT INTO palavras (idpalavra, palavra) VALUES (?,?)
		''', (countId, word,))
    idpalavra = cursorWord.lastrowid
    cursorWord.close()
    conn.close()

    return idpalavra

def wordLocation_insert(idurl, idword, localization, npage, line):
    conn = sqlite3.connect(
        'packeges/database/database.db', isolation_level=None)
    cursorWl = conn.cursor()
    countId = cursorWl.execute(
        "SELECT COUNT(*) FROM palavra_localizacao").fetchone()[0]+1
    cursorWl.execute('''
		INSERT INTO palavra_localizacao (idpalavra_localizacao, idurl, idpalavra, localizacao, locpalavra, linhas) VALUES (?,?,?,?,?,?)
		''', (countId, idurl, idword, localization, npage, line,))
    idpalavra_localizacao = cursorWl.lastrowid
    cursorWl.close()
    conn.close()

    return idpalavra_localizacao

def remove_all():
    conn = sqlite3.connect(
        'packeges/database/database.db', isolation_level=None)
    cursor = conn.cursor()
    cursor.execute('''DELETE FROM palavra_localizacao''')
    cursor.execute('''DELETE FROM palavras''')
    cursor.execute('''DELETE FROM urls''')
    cursor.execute('''DELETE FROM dados''')
    cursor.close()
    conn.close()

def location(palavras, npage, idnew_file, line):
    for i in range(len(palavras)):
        palavra = palavras[i]
        idpalavra = word_index(palavra)

        if (idpalavra == -1):
            idpalavra = word_insert(palavra)

        wordLocation_insert(idnew_file, idpalavra, i, npage, line)

def get_text(arquivo, diretorio, idnew_file):

    def txt_read(arquivo, diretorio, idnew_file):
        lineCount = 0
        # Atribui o arquivo atual como fileIN
        fileIN = codecs.open(os.path.join(
            os.path.realpath(diretorio), arquivo), encoding='utf-8')
        # Loop que percorre todo o arquivo
        for txt in fileIN:
            lineCount += 1
            for line in txt.split('\n'):
                npage = 'Linha: ' + str(lineCount)
                palavras = word_separate(line)
                location(palavras, npage, idnew_file, line)

        #return text

    def pdf_read(arquivo, diretorio, idnew_file):
        # Atribui o arquivo atual como fileIN
        fileIN = (os.path.join(os.path.realpath(diretorio), arquivo))
        # Loop que percorre todo o arquivo
        with pdfplumber.open(fileIN) as pdf:
            for page in pdf.pages:
                txt = page.extract_text()
                texto = [p for p in txt.split('\n') if p != None]
                npage = 'Página: ' + (str(page)[-2])
                for line in texto:
                    palavras = word_separate(line)
                    location(palavras, npage, idnew_file, line)

        #return palavras

    def xlsx_read(arquivo, diretorio, idnew_file):
        texto = ''
        line = ''
        # Atribui o arquivo atual como fileIN
        fileIN = open(os.path.join(os.path.realpath(diretorio), arquivo))
        df = pd.read_excel(fileIN.name, dtype=str, engine='openpyxl')
        #colls = (df.columns.values)
        for rows in df.index:
            for word in df.iloc[rows]:
                texto += str(word) + ' '
                line += str(word) + '    |   '
            npage = 'Linha: ' + str(rows+2)
            palavras = word_separate(texto)
            location(palavras, npage, idnew_file, line)
            line = ''
        
        #return text

    if(arquivo.endswith(".txt")):
        txt_read(arquivo, diretorio, idnew_file)

    elif(arquivo.endswith(".pdf")):
        pdf_read(arquivo, diretorio, idnew_file)

    elif(arquivo.endswith(".xlsx")):
        xlsx_read(arquivo, diretorio, idnew_file)



def search(words):

    def get_wordId(word):
        retorno = -1
        conn = sqlite3.connect('packeges/database/database.db')
        cursor = conn.cursor()
        rowcount_word = cursor.execute(
            "SELECT COUNT(idpalavra) FROM palavras WHERE palavra = ?", (word,)).fetchone()[0]
        cursor.execute('''
			SELECT idpalavra FROM palavras WHERE palavra = ?
			''', (word,))
        if rowcount_word > 0:
            retorno = cursor.fetchone()[0]

        cursor.close()
        conn.close()
        return retorno

    def get_wordLoc(idurl, idpalavra):
        conn = sqlite3.connect('packeges/database/database.db')
        cursor = conn.cursor()
        cursor.execute('''
			SELECT locpalavra FROM palavra_localizacao WHERE (idurl, idpalavra) = (?,?)
			''', (idurl, idpalavra,))
        
        retorno = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()

        return retorno
    
    def get_lines(idurl, idpalavra):
        conn = sqlite3.connect('packeges/database/database.db')
        cursor = conn.cursor()
        cursor.execute('''
			SELECT linhas FROM palavra_localizacao WHERE (idurl, idpalavra) = (?,?)
			''', (idurl, idpalavra,))
        
        retorno = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()

        return retorno
    
    def word_search(word):
        file_list = []
        idpalavra = get_wordId(word)
        conn = sqlite3.connect('packeges/database/database.db')
        cursor = conn.cursor()
        cursor.execute('''
			SELECT urls.url FROM palavra_localizacao plc INNER JOIN urls ON plc.idurl = urls.idurl WHERE plc.idpalavra = ?
			''', (idpalavra,))
        arquivos = set()
        for url in cursor:
            # print(url[0])
            arquivos.add(url[0])
        n = len(arquivos)
        #print('Arquivos encontrados: ' + str(n))
        for url in arquivos:
            # print(url)
            file_list.append(url)
        cursor.close()
        conn.close()

        return n, file_list

    def words_search(words):
        listaCampos = 'p1.idurl'
        listaTabelas = ''
        listaClausulas = ''
        palavrasId = []
        palavras = words.split(' ')
        nTabelas = 1
        for palavra in palavras:
            idpalavra = get_wordId(palavra)
            if idpalavra > 0:
                palavrasId.append(idpalavra)
                if nTabelas > 1:
                    listaTabelas += (', ')
                    listaClausulas += (' and ')
                    listaClausulas += ('p%d.idurl = p%d.idurl and ' %
                                       (nTabelas-1, nTabelas))
                listaCampos += (', p%d.localizacao' % nTabelas)
                listaTabelas += (' palavra_localizacao p%d' % nTabelas)
                listaClausulas += ('p%d.idpalavra = %d' %
                                   (nTabelas, idpalavra))

                nTabelas += 1

        #final_search = (''' SELECT ? FROM ? WHERE ? ''',(listaCampos, listaTabelas, listaClausulas,))

        conn = sqlite3.connect('packeges/database/database.db')
        cursor = conn.cursor()
        try:
            cursor.execute(''' SELECT %s FROM %s WHERE %s ''' %
                           (listaCampos, listaTabelas, listaClausulas))
            linhas = [linha for linha in cursor]
            
            cursor.close()
            conn.close()

            return linhas, palavrasId

        except:
            cursor.close()
            conn.close()

            return [], []

    def getUrl(idurl):
        conn = sqlite3.connect('packeges/database/database.db')
        cursor = conn.cursor()
        rowcount = cursor.execute(
            "SELECT COUNT(url) FROM urls WHERE idurl = ?", (idurl,)).fetchone()[0]
        cursor.execute('''
			SELECT url FROM urls WHERE idurl = ?
			''', (idurl,))
        if rowcount > 0:
            retorno = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        return retorno

    def distance_score(linhas):
        if len(linhas) > 0:
            if len(linhas[0]) <= 2:
                return dict([(linha[0], 1.0) for linha in linhas])

            distancias = dict([(linha[0], 1000000) for linha in linhas])
            for linha in linhas:
                dist = sum([abs(linha[i] - linha[i-1])
                           for i in range(2, len(linha))])
                if dist < distancias[linha[0]]:
                    distancias[linha[0]] = dist

            return distancias
        else:
            return []

    file_list = []
    locpalavras = []
    lines = []
    lin_lin = ''
    loc_loc = ''
    loc = ''
    locAux = ''
    lin = ''
    linAux = ''
    count = 0
    linhas, palavrasId = words_search(words)
    scores = distance_score(linhas)
    if scores != []:
        scoresOrdenado = sorted([(score, url)
                                for (url, score) in scores.items()], reverse=0)
        for (score, idurl) in scoresOrdenado:
            for idpalavra in palavrasId:
                loc = get_wordLoc(idurl, idpalavra)
                lin = get_lines(idurl, idpalavra)
                if count <= len(palavrasId):
                    flag = True
                if locAux != loc:
                    locAux = loc
                    if flag:
                        if count == 0:
                            loc_loc = loc
                        else:
                            loc_loc += ' e ' + loc
                    #else:
                        #locpalavras.append(loc)

                if linAux != lin:
                    linAux = lin
                    if flag:
                        if count == 0:
                           lin_lin = lin
                        else:
                            lin_lin += '\n   ' + lin
                    #else:
                        #lines.append(lin)
                
                count += 1
            
            locAux = ''
            linAux = ''
            count = 0

            locpalavras.append(loc_loc)
            lines.append(lin_lin)
            file_list.append(getUrl(idurl))
            #print('%f\t%s'%(score, getUrl(idurl)))
        #print(file_list, locpalavras, lines)
        return file_list, locpalavras, lines
    else:
        return file_list, locpalavras, lines

    #file_list = []
    #n, file_list = word_search(word)


def db_init():
    init()

#f_idx = file_index('teste')
# print(f_idx)
#f_ist = file_insert('test')
# print(f_ist)
#w_idx = word_index('amor')
# print(w_idx)
#w_ist = word_insert('love')
# print(w_ist)
#wl_ist = wordLocation_insert(1,2,50)
# print(wl_ist)

#search('Valter Nilo')

# remove_all()
