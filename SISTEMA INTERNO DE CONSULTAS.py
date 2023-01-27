import packeges.crawler as craw
from PIL import ImageTk, Image
import tkinter as tk
from tkinter import ttk
import _thread
import sqlite3
import codecs
import os


class seacher(tk.Tk):
    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self. initialize()

    def initialize(self):
        top = self.winfo_toplevel()
        self.menu = tk.Menu(top)

        self. selected_files = []

        self.porcent = 0

        # Frames
        self.frame_help = tk.Frame()
        self.frame_query = tk.Frame()
        self.frame_database = tk.Frame()

        # Strings Var
        self.current_file_name = tk.StringVar()
        self.selected_db = tk.StringVar()
        self.time = tk.StringVar()
        self.load = tk.StringVar()
        self.nfiles = tk.StringVar()
        self.bar = tk.DoubleVar()
        self.finish = tk.StringVar()
        self.ter_name = tk.StringVar()
        self.arq_name = tk.StringVar()
        self.time_name = tk.StringVar()
        self.load_name = tk.StringVar()
        self.current_name = tk.StringVar()
        self.info = tk.StringVar()

        # Setups
        self.selected_db.set("Banco de Dados Vazio")
        self.current_file_name.set("---")
        self.time.set("---")
        self.time_name.set("---")
        self.load_name.set("---")
        self.current_name.set("---")
        self.ter_name.set(' ')
        self.nfiles.set('0')
        self.bar.set(0)

        self.num = 1

        # images address
        self.check = "./packeges/images/checked.png"
        self.cancel = "./packeges/images/cancel.png"
        self.carrossel = "./packeges/images/%d.png"%self.num

        # images
        self.img_check_open = (Image.open(self.check))
        self.img_cancel_open = (Image.open(self.cancel))
        self.img_carrossel_open = (Image.open(self.carrossel))

        # images resize
        self.img_check_resize = self.img_check_open.resize((20, 20))
        self.img_cancel_resize = self.img_cancel_open.resize((20, 20))
        self.img_carrossel_resize = self.img_carrossel_open.resize((550, 250))

        # Abas
        # Aba arquivo
        arquivo = tk.Menu(self.menu, tearoff=0)
        #arquivo.add_command(label='Salvar', command=self.save_file)
        # arquivo.add_separator()
        arquivo.add_command(label='Sair', command=top.quit)
        self.menu.add_cascade(label='Arquivo', menu=arquivo)

        # Aba database
        sistema = tk.Menu(self.menu, tearoff=0)
        sistema.add_command(label='Consultas', command=self.query)
        sistema.add_command(label='Banco de dados', command=self.database)
        self.menu.add_cascade(label='Sistema', menu=sistema)

        # Aba ajuda
        ajuda = tk.Menu(self.menu, tearoff=0)
        ajuda.add_command(label='Informações', command=self.help)
        self.menu.add_cascade(label='Ajuda', menu=ajuda)

        self.db_exist = os.path.exists('packeges/database/database.db')
        self.db_update = tk.Button(
            self.frame_database, text='Atualizar Arquivos', bd='1', command=self.threads, font="Raleway")
        self.sel_db_name = tk.Label(
            self.frame_query, textvariable=self.selected_db, font="Raleway")

        if self.db_exist:
            self.db_update.configure(state='normal')
            self.img = ImageTk.PhotoImage(self.img_check_resize)
            self.get_data()
            self.query()
        else:
            self.db_update.configure(state='disabled')
            self.sel_db_name['fg'] = 'red'
            self.img = ImageTk.PhotoImage(self.img_cancel_resize)
            self.database()

        top.config(menu=self.menu)

    def get_data(self):
        try:
            self.conn = sqlite3.connect('packeges/database/database.db')
            try:
                self.cursor = self.conn.cursor()
                self.cursor.execute('''
					SELECT file FROM dados
					''')
                self.path = self.cursor.fetchone()[0]
                self.cursor.execute('''
					SELECT idfile FROM dados
					''')
                num = self.cursor.fetchone()[0]
                self.part = [p for p in self.path.split('/')]
                self.selected_db.set('... / ' + ' / '.join(self.part[-3:]))
                self.nfiles.set(num)
                self.bar.set(100)
                self.finish.set('CONCLUÍDO')
                self.cursor.close()
                self.conn.close()
            except:
                self.selected_db.set('Banco de dados corrompido')
                self.conn.close()
        except:
            craw.db_init()

    def db_remove(self):
        try:
            os.remove('packeges/database/database.db')
            self.selected_db.set("Banco de Dados Vazio")
            self.nfiles.set(0)
            self.bar.set(0)
            self.current_file_name.set('---')
            self.finish.set('')
            self.db_update.configure(state='disabled')
            self.img = ImageTk.PhotoImage(self.img_cancel_resize)
            self.sel_db_name['fg'] = 'red'
        except:
            self.bt_search.configure(state='disabled')

    def forget_all(self):
        self.frame_help.grid_forget()
        self.frame_query.grid_forget()
        self.frame_database.grid_forget()

    def save_file(self):
        pass

    def load_info(self):
        for text in self.file_info:
            for line in text.split('\n'):
                self.lb_info.insert('end', ' '+ line +'\n')
    
    def next(self):
        if self.num < 9:
            self.num += 1
        else:
            self.num = 1
        self.carrossel = "./packeges/images/%d.png"%self.num
        self.img_carrossel_open = (Image.open(self.carrossel))
        if self.num == 9:
            self.img_carrossel_resize = self.img_carrossel_open.resize((380, 250))
            self.img_info = ImageTk.PhotoImage(self.img_carrossel_resize)
            self.photo_info = tk.Label(self.frame_help, image=self.img_info)
            self.photo_info.grid(row=2, column=0, padx=170, pady=10, sticky='w')
        else:
            self.img_carrossel_resize = self.img_carrossel_open.resize((550, 250))
            self.img_info = ImageTk.PhotoImage(self.img_carrossel_resize)
            self.photo_info = tk.Label(self.frame_help, image=self.img_info)
            self.photo_info.grid(row=2, column=0, padx=100, pady=10, sticky='w')

    def prev(self):
        if self.num > 1:
            self.num -= 1
        else:
            self.num = 9
        self.carrossel = "./packeges/images/%d.png"%self.num
        self.img_carrossel_open = (Image.open(self.carrossel))
        if self.num == 9:
            self.img_carrossel_resize = self.img_carrossel_open.resize((380, 250))
            self.img_info = ImageTk.PhotoImage(self.img_carrossel_resize)
            self.photo_info = tk.Label(self.frame_help, image=self.img_info)
            self.photo_info.grid(row=2, column=0, padx=170, pady=10, sticky='w')
        else:
            self.img_carrossel_resize = self.img_carrossel_open.resize((550, 250))
            self.img_info = ImageTk.PhotoImage(self.img_carrossel_resize)
            self.photo_info = tk.Label(self.frame_help, image=self.img_info)
            self.photo_info.grid(row=2, column=0, padx=100, pady=10, sticky='w')

    def help(self):
        # init
        self.forget_all()
        self.frame_help.grid(row=0, column=0)
        self.file_info = codecs.open('./packeges/Info.txt','r', encoding='utf-8')
        # Title
        self.hp_title = tk.Label(self.frame_help, text='INFORMAÇÕES', font="Raleway").grid(
            row=0, column=0, padx=290, pady=10, sticky='w')

        self.sb_info = tk.Scrollbar(self.frame_help, orient='vertical')
        self.sb_info.grid(row=1, column=0, padx=735, sticky="ns")
        self.lb_info = tk.Text(self.frame_help,
                                  yscrollcommand=self.sb_info.set, font="Raleway")
        self.load_info()
        self.lb_info.tag_configure("left", justify="center", )
        self.lb_info.tag_add("center", 1.0, "end")
        self.lb_info.configure(height=19)
        self.sb_info.config(command=self.lb_info.yview, width=15)
        self.lb_info.grid(row=1, column=0, padx=7, pady=5, sticky="w")
        self.lb_info['bg'] = '#f6f6f6'

        self.img_info = ImageTk.PhotoImage(self.img_carrossel_resize)
        self.photo_info = tk.Label(self.frame_help, image=self.img_info)
        if self.num == 9:
            self.photo_info.grid(row=2, column=0, padx=170, pady=10, sticky='w')
        else:
            self.photo_info.grid(row=2, column=0, padx=100, pady=10, sticky='w')
        self.bt_prev = tk.Button(self.frame_help, text='<', bd='1', command=self.prev, font="Raleway").grid(row=2, column=0, padx=50, sticky='w')
        self.bt_next = tk.Button(self.frame_help, text='>', bd='1', command=self.next, font="Raleway").grid(row=2, column=0, padx=680, sticky='w')

        app.maxsize(760, 670)
        app.minsize(760, 670)
        app.resizable(width=760, height=670)

    def database(self):
        # Init
        self.forget_all()
        self.frame_database.grid(row=0, column=0)

        # Title
        self.db_title = tk.Label(self.frame_database, text='BANCO DE DADOS', font="Raleway").grid(
            row=0, column=0, padx=290, pady=10, sticky='w')

        # DB Load
        self.db_load = tk.Button(
            self.frame_database, text='Abrir Pasta', bd='1', command=self.open_dir, font="Raleway")
        self.db_load.configure(state='normal')
        self.db_load.grid(row=1, column=0, padx=100, pady=10, sticky='w')

        # Base Label
        self.base_label = tk.Label(self.frame_database, text='Base:', font="Raleway").grid(
            row=1, column=0, padx=200, pady=10, sticky='w')
        self.db_base = tk.Label(self.frame_database, textvariable=self.selected_db, font="Raleway").grid(
            row=1, column=0, padx=250, pady=10, sticky='w')

        # DB Update
        self.db_update.grid(row=0, column=0, padx=600, pady=10, sticky='w')

        # Data
        self.db_data = tk.Label(self.frame_database, textvariable=self.nfiles, font="Raleway").grid(
            row=2, column=0, padx=260, pady=10, sticky='w')
        self.db_files = tk.Label(self.frame_database, text='Arquivos Carregados:', font="Raleway").grid(
            row=2, column=0, padx=100, pady=10, sticky='w')

        # Progress Bar
        self.pb = ttk.Progressbar(
            self.frame_database, variable=self.bar, maximum=100)
        self.pb.place(x=100, y=160, width=550, height=20)

        # Current file
        self.cf = tk.Label(self.frame_database, text='Arquivo atual:', font="Raleway").grid(
            row=3, column=0, padx=100, pady=55, sticky='w')
        self.cf_name = tk.Label(self.frame_database, textvariable=self.current_file_name, font="Raleway").grid(
            row=3, column=0, padx=210, pady=50, sticky='w')

        # Delete
        self.db_delete = tk.Button(
            self.frame_database, text='Deletar Banco', bd='1', command=self.db_remove, font="Raleway")
        #self.db_delete['fg'] = 'red'
        self.db_delete.grid(row=4, column=0, padx=625, sticky='w')

        self.finished = tk.Label(
            self.frame_database, textvariable=self.finish, font="Raleway")
        self.finished['fg'] = 'green'
        self.finished.grid(row=2, column=0, padx=550, sticky='w')

    def query(self):
        # Init
        self.forget_all()
        self.load.set('0%')
        try:
            self.alert.grid_forget()
        except:
            pass
        self.frame_query.grid(row=0, column=0)

        # title
        self.sis_title = tk.Label(self.frame_query, text='SISTEMA INTERNO DE CONSULTAS', font="Raleway").grid(
            row=0, column=0, padx=240, pady=10, sticky='w')

        # Loaded Directory Name
        self.sel_db = tk.Label(self.frame_query, text='Diretório:', font="Raleway").grid(
            row=1, column=0, padx=150, pady=10, sticky='w')
        self.sel_db_name.grid(row=1, column=0, padx=220, pady=10, sticky='w')

        # Status
        self.sts = tk.Label(self.frame_query, text='Status:', font="Raleway").grid(
            row=3, column=0, padx=550, pady=10, sticky='w')
        self.photo = tk.Label(self.frame_query, image=self.img)
        self.photo.grid(row=3, column=0, padx=605, pady=10, sticky='w')

        # Alert
        self.alert = tk.Label(
            self.frame_query, text='O termo de busca não \npode estar em branco', font="Raleway")

        # Data Entry
        self.label_entry = tk.Label(
            self.frame_query, text='Termo da busca:', font="Raleway")
        self.label_entry['fg'] = 'black'
        self.label_entry.grid(row=2, column=0, padx=150, sticky='w')
        self.data_entry = tk.Entry(self.frame_query, width=40)
        self.data_entry.grid(row=2, column=0, padx=280, sticky='w')
        self.data_entry.insert(0, "ex: José Roberto")
        self.data_entry.configure(state='disabled', font="Raleway")

        # On clicked
        self.on_click_id = self.data_entry.bind('<Button-1>', self.on_click)

        # Search Button
        self.bt_search = tk.Button(self.frame_query, text="BUSCAR", bd='1',
                                   command=lambda: self.search('<Return>'), font="Raleway")
        self.bt_search.configure(state='normal')
        self.bt_search.grid(row=3, column=0, padx=340, pady=10, sticky='w')

        # Estimate Time
        self.est_time = tk.Label(self.frame_query, text="Tempo estimado:", font="Raleway").grid(
            row=4, column=0, padx=150, pady=10, sticky="w")
        self.time_var = tk.Label(self.frame_query, textvariable=self.time, font="Raleway").grid(
            row=4, column=0, padx=285, pady=10, sticky="w")

        # Progress Number
        self.progress = tk.Label(self.frame_query, text="Andamento:", font="Raleway").grid(
            row=4, column=0, padx=470, pady=10, sticky="w")
        self.load_var = tk.Label(self.frame_query, textvariable=self.load, font="Raleway").grid(
            row=4, column=0, padx=565, pady=10, sticky="w")

    def index(self, flag):
        f = []
        for (dirpath, dirnames, filenames) in os.walk(self.path):
            f.extend(filenames)
        total = (len(f))
        if flag:
            craw.data_insert(total, self.path)
        for diretorio, subpastas, arquivos in os.walk(self.path):
            for url in arquivos:
                self.porcent += (90/total)
                u = diretorio+'/'+url
                indexada = craw.file_index(url)
                if (indexada != -2):
                    if (indexada == -1):
                        #print('Url não existe')
                        idnew_file = craw.file_insert(url)

                    elif (indexada > 0):
                        #print('Url sem palavras')
                        idnew_file = indexada

                    self.current_file_name.set(url)
                    self.bar.set(self.porcent)

                    craw.get_text(url, self.path, idnew_file)
                else:
                    #print('Url já indexada')
                    self.current_file_name.set(url)
                    self.bar.set(self.porcent)

        return total

    def update_data(self):
        flag = False
        self.db_exist = os.path.exists('packeges/database/database.db')
        if not self.db_exist:
            craw.db_init()
            flag = True

        self.img = ImageTk.PhotoImage(self.img_cancel_resize)
        self.finish.set('')
        self.nfiles.set(0)
        self.db_delete.configure(state='disabled')
        self.porcent = 0
        app.bind('<Return>', app.skip)
        self.db_update.configure(state='disabled')
        self.nfiles.set(self.index(flag))
        self.bar.set(self.porcent+10)
        self.current_file_name.set('---')
        self.finish.set('CONCLUÍDO')
        self.db_delete.configure(state='normal')
        self.db_update.configure(state='normal')
        self.img = ImageTk.PhotoImage(self.img_check_resize)
        self.photo = tk.Label(self.frame_query, image=self.img)
        self.photo.grid(row=3, column=0, padx=605, pady=10, sticky='w')
        self.sel_db_name['fg'] = 'black'
        try:
            self.bt_search.configure(state='normal')
        except:
            pass
        app.bind('<Return>', app.search)

    def open_dir(self):
        # Path Read
        self.path = tk.filedialog.askdirectory()
        # extract last name on path address
        part = [p for p in self.path.split('/')]
        self.current_file = '... / ' + ' / '.join(part[-3:])
        if self.current_file != '':
            self.selected_db.set(self.current_file)
            self.db_update.configure(state='normal')
            self.finish.set('')

    def on_click(self, event):
        self.label_entry['fg'] = 'black'
        self.alert.grid_forget()
        self.data_entry.configure(state='normal')
        self.data_entry.delete(0, 'end')
        self.bt_search.configure(state='normal')
        # make the callback only work once
        self.data_entry.unbind('<Button-1>', self.on_click_id)

    def skip(self, event):
        pass

    def search(self, event):
        flag = False
        self.porcent = 0
        research = str(self.data_entry.get())

        if ((research == 'ex: José Roberto') or (research == '')):
            self.label_entry['fg'] = 'red'
            self.alert.grid(row=3, column=0, padx=110, sticky="w")
            self.alert['fg'] = 'red'
            flag = False
        else:
            self.bt_search.configure(state='disabled')
            self.label_entry['fg'] = 'black'
            self.alert.grid_forget()
            flag = True

        if flag:
            try:
                self.selected_files, self.location, self.lines = craw.search(research)
                self.files_result = zip(self.selected_files, self.location, self.lines)
                self.sb = tk.Scrollbar(self.frame_query, orient='vertical')
                self.sb.grid(row=9, column=0, padx=735, sticky="ns")
                self.lb = tk.Text(self.frame_query,
                                  yscrollcommand=self.sb.set, font="Raleway")

                if self.selected_files != []:
                    total = len(self.selected_files)

                    if len(self.selected_files) == 1:
                        self.arq_name.set("			FOI ENCONTRADO %d ARQUIVO" % (
                            len(self.selected_files)))
                    else:
                        self.arq_name.set("			FORAM ENCONTRADOS %d ARQUIVOS" % (
                            len(self.selected_files)))

                    for arquivo, local, linha in self.files_result:
                        self.porcent += (100/total)
                        porcent = (str("%.0f" % self.porcent) + ' %')
                        app.update()
                        self.load.set(porcent)
                        self.lb.insert(
                            'end', ' ----------------------------------------------------------------------------------------------------------------------------------------------\n')
                        self.lb.insert('end', ' '+arquivo+'\n')
                        self.lb.insert('end', ' - '+local+'\n')
                        self.lb.insert('end', '   '+linha+'\n')
                        self.lb.insert('end', '\n')
                else:
                    self.arq_name.set("			NENHUM ARQUIVO FOI ENCONTRADO")

                # Term of research
                self.term = tk.Label(
                    self.frame_query, textvariable=self.ter_name, font="Raleway")
                self.term.grid(row=7, column=0, padx=5, sticky="w")

                # Files Label
                self.arq = tk.Label(
                    self.frame_query, text="Arquivos: ", font="Raleway")
                self.arq.grid(row=8, column=0, padx=5, pady=10, sticky="w")

                # Result Num Files
                self.target = tk.Label(
                    self.frame_query, textvariable=self.arq_name, font="Raleway")
                self.target.grid(row=6, column=0, padx=5, sticky="w")

                # self.load.set('100%')
                self.time_name.set('00:00:00.0')
                self.ter_name.set("			para o termo: \"" + research + "\"")
                self.lb.tag_configure("left", justify="center", )
                self.lb.tag_add("center", 1.0, "end")
                self.lb.configure(height=19)
                self.sb.config(command=self.lb.yview, width=15)
                self.lb.grid(row=9, column=0, padx=7, pady=5, sticky="w")
                self.lb['bg'] = '#f6f6f6'
                app.maxsize(760, 670)
                app.minsize(760, 670)
                app.resizable(width=760, height=670)
                self.bt_search.configure(state='normal')

            except:
                self.sel_db_name['fg'] = 'red'

    def threads(self):
        try:
            _thread.start_new_thread(self.update_data, ())
        except:
            pass


if __name__ == "__main__":
    app = seacher(None)
    app.title('Sistema interno de consultas')
    app.geometry("760x615+10+10")
    app.maxsize(760, 315)
    app.minsize(760, 315)
    app.iconbitmap(
        './packeges/icon/icon.ico')
    app.bind('<Return>', app.search)
    app.mainloop()
