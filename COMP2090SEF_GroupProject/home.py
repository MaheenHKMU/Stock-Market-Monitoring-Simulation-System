from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3 as db
import portfolio
import subprocess
import sys
import webbrowser
from bs4 import BeautifulSoup
import requests

help_font = ('Segoe UI', 11)



def logout(root):
    root.destroy()


def show_help(title, text):
    help_window = tk.Toplevel()
    help_window.title(title)
    help_window.configure(bg='white')
    tk.Label(help_window, text=text, fg='black', bg='white', font=help_font,
             justify=LEFT, wraplength=500).pack(padx=15, pady=20)
    tk.Button(help_window, text='OK', bg='#00695c', fg='white', font=('Segoe UI', 10, 'bold'),
              activebackground='#004d40', command=help_window.destroy).pack(pady=10)


def help_buy():
    show_help("How to Buy a Stock?", """
To buy a stock in the Stock Simulator:

1. Go to the Stock Simulator screen (from the main menu).
2. Enter the stock symbol in the "Stock Search" box.
   - Example: AAPL, MSFT, TSLA
3. Click "Get Price" to load the latest stock information.
4. Enter the amount you want to invest (number of shares).
5. Click the "Buy" button.

* Make sure you have enough balance to cover the cost.
* The price shown is fetched live and may change.
""")


def help_sell():
    show_help("How to Sell a Stock?", """
To sell a stock from your portfolio:

1. Go to the "Stock Simulator" screen.
2. Enter the stock symbol you own (e.g., AAPL, MSFT).
3. Click "Get Price" to load current stock details.
4. Enter the number of shares you want to sell.
5. Click the "Sell" button to complete the transaction.

* Make sure you own enough shares of the stock.
* The sale amount will be added back to your account balance.
""")


def help_query():
    show_help("How to Monitor Stocks", """
The Stock Monitoring tool allows you to:

1. Enter the stock symbol in the input field.
   Example: AAPL, GOOGL, AMZN
2. Click “Add Symbol” to add it to the list.
   - You can add multiple symbols.
   - Prices update automatically when added.
3. Use the dropdown to select a stock.
4. Click “Show Chart” to view its 30-day price movement.

 Notes:
- Make sure the symbol is valid (e.g., listed on NASDAQ).
- Prices and chart data are retrieved live using Yahoo Finance.
- The chart displays daily closing prices for the last 30 days.

Use this tool to track stocks before making simulated trades.
""")


def help_portfolio():
    show_help("How to Check Your Purchases and Transactions?", """
The “View Your Portfolio” page lets you track all the stocks you’ve bought and sold.

Here’s what you can do:

 View your current holdings:
- Ticker (stock symbol)
- Company name
- Number of shares owned
- Purchase price
- Current market price
- Profit or loss on each stock

 Track your transaction history:
- Your balance is updated after every buy/sell
- The “Balance” label shows your available funds

 Tip:
- If no stocks appear, try buying one through the Stock Simulator first.
""")


def launch_other_app():
    subprocess.Popen([sys.executable, 'stock_sim.py'])


def Stock_monitor():
    subprocess.Popen([sys.executable, 'Stock_monitor.py'])

def View_portfolio():
    subprocess.Popen([sys.executable, 'portfolio.py'])



def main(user):
    root = tk.Tk()
    root.title("Stock Market Monitoring & Simulation System")
    root.geometry("1000x620")
    root.configure(bg="#eef2f3")

   
    header_frame = tk.Frame(root, bg="#1a237e", pady=15)
    header_frame.pack(fill='x')
    tk.Label(header_frame, text=f"Welcome, {user} !",
             font=("Segoe UI", 18, "bold"), bg="#1a237e", fg="white").pack(pady=2)
    tk.Label(header_frame,
             text="Manage your portfolio, monitor stocks, and simulate trades.",
             font=("Segoe UI", 11), bg="#1a237e", fg="white").pack(pady=5)

   
    menu_frame = tk.Frame(root, bg="#dfe6e9", pady=8)
    menu_frame.pack(fill='x')

    def create_menu_button(text, command):
        return tk.Button(
            menu_frame, text=text, command=command,
            font=("Segoe UI", 10, "bold"), bg="#ffffff", fg="#2d3436",
            activebackground="#74b9ff", activeforeground="black",
            relief="flat", padx=10, pady=5, bd=1, highlightthickness=1,
            highlightbackground="#b2bec3"
        )

    create_menu_button("How to Buy?", help_buy).pack(side="left", padx=10)
    create_menu_button("How to Sell?", help_sell).pack(side="left", padx=10)
    create_menu_button("How to Monitor Stocks?", help_query).pack(side="left", padx=10)
    create_menu_button("How to Check My Purchases and Transactions?", help_portfolio).pack(side="left", padx=10)

   
    side_panel_left = tk.Frame(root, width=100, bg="#eef2f3")
    side_panel_left.pack(side='left', fill='y')

    side_panel_right = tk.Frame(root, width=100, bg="#eef2f3")
    side_panel_right.pack(side='right', fill='y')

    
    main_frame = tk.Frame(root, bg="white", padx=40, pady=30, relief='ridge', bd=2)
    main_frame.pack(expand=True)

    def create_button(text, color, hover_color, command):
        btn = tk.Button(main_frame, text=text, bg=color, fg='black',
                        font=('Segoe UI', 12, 'bold'), relief='flat',
                        activebackground=hover_color, activeforeground='black',
                        width=30, height=2, bd=1, highlightthickness=1,
                        highlightbackground="#b0bec5", command=command)
        btn.pack(pady=12)
        return btn

    create_button("Stock Simulator", "#ffe0b2", "#ffcc80", launch_other_app)
    create_button("Stock Monitoring", "#c8e6c9", "#a5d6a7", Stock_monitor)
    create_button("View Your Portfolio", "#b3e5fc", "#81d4fa", View_portfolio)
    create_button("Logout", "#ef9a9a", "#e57373", lambda: logout(root))

    root.mainloop()



if __name__ == "__main__":
    main("DemoUser")
