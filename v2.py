from tkinter import *
from tkinter import ttk
import mysql.connector
from mysql.connector import errorcode


class Connection():
    connection_value = False
    def __init__(self):
        try:
            self.db_connection = mysql.connector.connect(host='localhost', user='root', password='#MySQL@1357', database='empresa')
            print("Database connection made!")
            self.connection_value = True
        except mysql.connector.Error as error:
            if error.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database doesn't exist")
            elif error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("User name or password is wrong")
            else:
                print(error)


class CRUD():
    def __init__(self):
        self.conn = Connection()
        self.cursor = self.conn.db_connection.cursor()

    def get_columns(self, table_name):
        sql = f"SHOW COLUMNS FROM {table_name}"
        self.cursor.execute(sql)
        return [item[0] for item in self.cursor]

    def get_data(self, table_name):
        sql = f"SELECT * FROM {table_name}"
        self.cursor.execute(sql)
        return [item for item in self.cursor]
    
    def get_data_like(self, table_name, termo, column):
        sql = f"SELECT * FROM {table_name} WHERE {column} LIKE '%{termo}%'"
        self.cursor.execute(sql)
        return [item for item in self.cursor]
    
    def get_columns_name(self, table_name):
        sql = (f"show columns from {table_name}")
        self.cursor.execute(sql)

        colunas = []

        for item in self.cursor: 
            if item[3] != "PRI":
                colunas.append(item[0])

        col = ""
        
        for i, c in enumerate(colunas):
            if i == 0:
                col = c
            else:
                col = col + ", " + c

        return col

    def insert_data(self, values, table_name):
        columns = self.get_columns_name(table_name)

        sql = f"INSERT INTO {table_name} ({columns}) VALUES (%s, %s, %s)"
        print(sql)
        self.cursor.execute(sql, values)
        self.conn.db_connection.commit()
        print(self.cursor.rowcount, "record inserted.")

    def delete_related_data(self, id):
        sql = f"DELETE FROM vendas WHERE funcionarioMatricula = '{id}'"
        self.cursor.execute(sql)
        self.conn.db_connection.commit()
        print(self.cursor.rowcount, "related records deleted.")

    def delete_data(self, id, table_name):
        sql = f"DELETE FROM {table_name} WHERE matricula = '{id}'"
        self.cursor.execute(sql)
        self.conn.db_connection.commit()
        print(self.cursor.rowcount, "record deleted.")

    def update_data(self, set_dados, id, table_name):
        sql = (f"show columns from {table_name}")
        self.cursor.execute(sql)

        colunas = []
        primary = []

        for item in self.cursor: 
            if item[3] != "PRI":
                colunas.append(item[0])
            else:
                primary.append(item[0])

        sql = f"UPDATE {table_name} SET "
        
        for i, c in enumerate(colunas):
            if i == 0:
                sql = sql + c + f" = '{set_dados[0]}'"
            else:
                sql = sql + ", " + c + f" = '{set_dados[i]}'"

        sql = sql + f" WHERE matricula = {id}"

        # sql = f"UPDATE {table_name} SET nome = '{nome}', cidade = '{cidade}', salario = '{salario}' WHERE matricula = {id}"
        self.cursor.execute(sql)
        self.conn.db_connection.commit()
        print(self.cursor.rowcount, "record deleted.")

# column_config = [[min, max, scre], []]
class Table(Frame):
    def __init__(self, root, columns, data, column_config):
        super().__init__(root, width=900, height=500)
        self.tree_view = ttk.Treeview(self, columns=columns, show='headings')
        for index, column in enumerate(columns):
            self.tree_view.heading(column, text=column.title())
            self.tree_view.column(
                column, 
                minwidth=column_config[index][0],
                width=column_config[index][1],
                stretch=column_config[index][2]
            )
            self.tree_view.bind("<ButtonRelease-1>", self.preper_update)
        self.populate(data)
        self.tree_view.pack()
        self.grid(column=0, row=1)

    def populate(self, data):
        for i in self.tree_view.get_children():
            self.tree_view.delete(i)
        for dt in data:
            self.tree_view.insert("", "end", values=dt)

    def get_select_item(self):
        aux = self.tree_view.focus()
        return self.tree_view.item(aux)
    
    def preper_update(self, event):
        print(event)
        ety_matricula.delete(0, END)
        ety_nome.delete(0, END)
        ety_cidade.delete(0, END)
        ety_salario.delete(0, END)
        selected_item = self.get_select_item()
        if selected_item and selected_item["values"]:
            item = selected_item["values"]
            ety_matricula.insert(0, item[0])
            ety_nome.insert(0, item[1])
            ety_cidade.insert(0, item[2])
            ety_salario.insert(0, item[3])

def preset_delete(table, connect):
    selected_item = table.get_select_item()
    if selected_item and selected_item["values"]:
        item = selected_item["values"]
        connect.delete_related_data(item[0])
        connect.delete_data(item[0], "funcionario")
        table.populate(connect.get_data("funcionario"))

def preset_update(table, connect, e0, e1, e2, e3):
    if e1.get() == "" or e2.get() == "" or e3.get() == "": 
        return
    connect.update_data((e1.get(), e2.get(), e3.get()), e0.get(), "funcionario")
    table.populate(connect.get_data("funcionario"))
    e0.delete(0, END)
    e1.delete(0, END)
    e2.delete(0, END)
    e3.delete(0, END)

def preset_insert(table, connect):
    if e_nome.get() == "" or e_cidade.get() == "" or e_salario.get() == "": 
        return
    connect.insert_data((e_nome.get(), e_cidade.get(), e_salario.get()), "funcionario")
    e_nome.delete(0, END)
    e_cidade.delete(0, END)
    e_salario.delete(0, END)
    table.populate(connect.get_data("funcionario"))

def preset_select(table, connect):
    termo = ety_select.get()
    table.populate(connect.get_data_like("funcionario", termo, "nome"))

app = Tk()
app.title("FUNCIONARIOS")

connect = CRUD()

frame = Frame(app)
frame.pack()

config_column = [[50, 70, True], [50, 175, True], [50, 100, True], [50, 75, True]]
t = Table(frame, connect.get_columns("funcionario"), connect.get_data("funcionario"), config_column)

# ===========================================================================================
lblFrm_select = LabelFrame(frame, text="PESQUISA", font=("Arial", 12, "bold"))
lblFrm_select.grid(column=0, row=4, padx=20, pady=20)

ety_select = Entry(lblFrm_select, width=20)
ety_select.grid(column=0, row=0, padx=10, pady=10, ipadx=5)

btn_pesquisar = Button(lblFrm_select, text="PESQUISAR", command=lambda: preset_select(t, connect))
btn_pesquisar.grid(column=1, row=0, padx=10)

# ===========================================================================================

lblFrm_insert = LabelFrame(frame, text="INSERIR DADOS", font=("Arial", 12, "bold"))
lblFrm_insert.grid(column=0, row=0, padx=20, pady=20)

lbl_nome = Label(lblFrm_insert, text="Nome")
e_nome = Entry(lblFrm_insert)

lbl_cidade = Label(lblFrm_insert, text="Cidade")
e_cidade = Entry(lblFrm_insert)

lbl_salario = Label(lblFrm_insert, text="Salario")
e_salario = Entry(lblFrm_insert)

lbl_nome.grid(column=0, row=0, padx=10, pady=10)
e_nome.grid(column=1, row=0, padx=10, pady=10)

lbl_cidade.grid(column=2, row=0, padx=10, pady=10)
e_cidade.grid(column=3, row=0, padx=10, pady=10)

lbl_salario.grid(column=4, row=0, padx=10, pady=10)
e_salario.grid(column=5, row=0, padx=10, pady=10)

btn_insert = Button(lblFrm_insert, text="INSERT", command=lambda: preset_insert(t, connect))
btn_insert.grid(column=6, row=0, padx=10, pady=10)

# ===========================================================================================

lblFrm_Update = LabelFrame(frame, text="ATUALIZAR DADOS", font=("Arial", 12, "bold"))
lblFrm_Update.grid(column=0, row=3, padx=20, pady=20)

# lbl2_matricula = Label(frame, text="Matricula")
lbl2_nome = Label(lblFrm_Update, text="Nome")
lbl2_cidade = Label(lblFrm_Update, text="Cidade")
lbl2_salario = Label(lblFrm_Update, text="Salario")

# lbl2_matricula.grid(column=0, row=4)
lbl2_nome.grid(column=1, row=0, padx=10)
lbl2_cidade.grid(column=2, row=0, padx=10)
lbl2_salario.grid(column=3, row=0, padx=10)

ety_matricula = Entry(lblFrm_Update)
ety_nome = Entry(lblFrm_Update)
ety_cidade = Entry(lblFrm_Update)
ety_salario = Entry(lblFrm_Update)

# ety_matricula.grid(column=0, row=5)
ety_nome.grid(column=1, row=1, padx=10)
ety_cidade.grid(column=2, row=1, padx=10)
ety_salario.grid(column=3, row=1, padx=10)


btn_update = Button(lblFrm_Update, text="UPDATE", command=lambda: preset_update(t, connect, ety_matricula, ety_nome, ety_cidade, ety_salario))
btn_update.grid(column=4, row=0, rowspan=2, padx=10, pady=10)

# ===========================================================================================


btn_delete = Button(frame, text="DELETE", command=lambda: preset_delete(t, connect), 
                    background="red", fg="white", font=("Arial", 12, "bold"))
btn_delete.grid(column=0, row=5, pady=10, ipadx=100)



app.mainloop()
connect.conn.db_connection.close()
