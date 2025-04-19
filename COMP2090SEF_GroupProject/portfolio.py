import tkinter as tk
from tkinter import ttk
import datetime
from tkinter import messagebox
import yfinance as yf #type: ignore[import]
from threading import Thread
import time
import json

class StockTracker:
    def __init__(self, root):
        self.new_window = root
        self.new_window.title("Portfolio")
        self.new_window.geometry("400x600")
        try:
            with open("simulator_data.json", 'r') as file:
                self.balances = json.load(file)
                self.balance = self.balances['balance'] # Initialize balance
        except FileNotFoundError:
            messagebox.showerror("You have to SELL a stock first then your portfolio will show up")
        self.total_profit_loss = 0  # Initialize total profit/loss
        self.portfolio_text = tk.Text(self.new_window, wrap=tk.WORD)
        self.portfolio_text.pack(expand=True, fill=tk.BOTH)
        
        self.balance_label = tk.Label(self.new_window, text=f"Balance: ${self.balance:.2f}", font=("Arial", 12))
        self.balance_label.pack(pady=10)

        
        try:
         with open("portfolio.json", "r") as file:
            portfolio_data = file.readlines()
        except FileNotFoundError:
                messagebox.showerror("Error", "No portfolio data found.")
                return
        except json.JSONDecodeError:
                messagebox.showerror("Error", "Error decoding portfolio data.")
                return
            
        for line in portfolio_data:
                try:
                    data = json.loads(line.strip().rstrip(","))
                    if "profit_loss" in data:
                       self.balance += data["profit_loss"]
                       self.total_profit_loss += data["profit_loss"]
                    elif "profit_gain" in data:
                       self.balance += data["profit_gain"]
                       self.total_profit_loss += data["profit_gain"]
                     #update balance
                    self.balance_label.config(text=f"Balance: ${self.balance:.2f}")
                except json.JSONDecodeError:
                 continue
             
        self.profit_loss_label = tk.Label(self.new_window, text=f"Total Profit/Loss: ${self.total_profit_loss:.2f}", font=("Arial", 12))
        self.profit_loss_label.pack(pady=20)
        
        for line in portfolio_data:
            try:
              data = json.loads(line.strip().rstrip(","))
              if "profit_loss" in data:
                self.total_profit_loss += data["profit_loss"]
                self.portfolio_text.insert(tk.END, f"{data['symbol']} - Loss: ${data['profit_loss']:.2f}\n")
              elif "profit_gain" in data:
                self.total_profit_loss += data["profit_gain"]
                self.portfolio_text.insert(tk.END, f"{data['symbol']} - Gain: ${data['profit_gain']:.2f}\n")
            except json.JSONDecodeError:
              continue
       
       #create a frame for buttons
        self.button_frame = tk.Frame(self.new_window)
        self.button_frame.pack(pady=10)


        
       
    def save_portfolio(self):
        with open("portfolio.json", "w") as file:
            json.dump(self.portfolio, file, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = StockTracker(root)
    root.protocol("WM_DELETE_WINDOW", lambda: ( root.destroy()))
    root.mainloop()