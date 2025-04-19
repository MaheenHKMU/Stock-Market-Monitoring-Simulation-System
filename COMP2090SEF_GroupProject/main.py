import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3 as db
import pickle
import os
import home


class Portfolio:
    def __init__(self, username):
        self.username = username
        self.stock_list = {}


root = tk.Tk()
root.title("Stock Market Login Page")
root.geometry("700x600")
root.configure(bg="#1a237e") 


style = ttk.Style()
style.configure('TButton', font=('Segoe UI', 10), padding=6)
style.configure('TLabel', font=('Segoe UI', 10), padding=4)
style.configure('TEntry', padding=4)
style.configure('TLabelframe', background='#eef2f7')
style.configure('TNotebook', tabposition='n')
style.configure('TNotebook.Tab', font=('Segoe UI', 10, 'bold'))

def login_success(user):
    home.main(user)


def login_clicked(e):
    username = e[0].get()
    password = e[1].get()

    conn = db.connect('datastore.db')
    cursor = conn.cursor()
    result = cursor.execute('SELECT Password FROM Stocks WHERE Username=?', (username,)).fetchone()
    conn.close()

    if result and result[0] == password:
        messagebox.showinfo("Login Successful", f"Welcome back, {username}!")
        login_success(username)
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")


def register_clicked(e):
    username = e[0].get()
    password = e[1].get()
    confirm = e[2].get()
    

    if not all([username, password, confirm]):
        messagebox.showwarning("Missing Info", "Please fill out all fields.")
        return

    if password != confirm:
        messagebox.showerror("Error", "Passwords do not match.")
        return

    if len(username) > 15 or len(password) < 8:
        messagebox.showerror("Error", "Username must be under 15 characters and password at least 8 characters.")
        return

    

    conn = db.connect('datastore.db')
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS Stocks 
                      (Username TEXT PRIMARY KEY, Password TEXT, Balance INT, Stock_list BLOB)""")

    if cursor.execute("SELECT * FROM Stocks WHERE Username=?", (username,)).fetchone():
        messagebox.showerror("Exists", "Username already taken.")
        return

    portfolio = Portfolio(username)

    if not os.path.exists('user_data'):
        os.makedirs('user_data')

    with open(f'user_data/{username}.pkl', 'wb') as f:
        pickle.dump(portfolio, f)

    cursor.execute("INSERT INTO Stocks VALUES (?, ?, ?, ?)", (username, password, 0, f"{username}.pkl"))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", f"Account created for {username}.")


def create_form(tab, labels, button_text, callback):
    entries = []
    for idx, label_text in enumerate(labels):
        label = ttk.Label(tab, text=label_text)
        entry = ttk.Entry(tab, show="*" if 'Password' in label_text else "")
        label.grid(row=idx, column=0, pady=6, padx=5, sticky='e')
        entry.grid(row=idx, column=1, pady=6, padx=5, sticky='w')
        entries.append(entry)

    button = ttk.Button(tab, text=button_text, command=lambda: callback(entries))
    button.grid(row=len(labels), columnspan=2, pady=12)


def exit_app():
    root.destroy()



header_frame = tk.Frame(root, bg="#1a237e", pady=15)
header_frame.pack(fill='x')

tk.Label(
    header_frame,
    text="Stock Market Monitoring & Simulation System",
    font=("Segoe UI", 18, "bold"),
    bg="#1a237e",
    fg="white"
).pack(pady=2)

tk.Label(
    header_frame,
    text="Register or log in to start managing your virtual stock portfolio.",
    font=("Segoe UI", 11),
    bg="#1a237e",
    fg="white"
).pack(pady=5)


notebook = ttk.Notebook(root)
notebook.pack(pady=20, expand=True, fill='both')


login_tab = ttk.Frame(notebook)
notebook.add(login_tab, text="Login")
create_form(login_tab, ["Username", "Password"], "Login", login_clicked)


register_tab = ttk.Frame(notebook)
notebook.add(register_tab, text="Register")
create_form(register_tab, ["Username", "Password", "Confirm Password",], "Register", register_clicked)


exit_btn = ttk.Button(root, text="Exit", command=exit_app)
exit_btn.pack(pady=15)

root.mainloop()
