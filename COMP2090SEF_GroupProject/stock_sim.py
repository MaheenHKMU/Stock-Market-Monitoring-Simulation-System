import tkinter as tk
from tkinter import messagebox, ttk
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import subprocess
import sys
import json
import os
import pickle

class StockApp:
    def __init__(self, master):
        self.master = master
        master.title("Stock Simulator")
        master.configure(bg='#2E3B4E')

        # Initialize session data
        self.balance = 10000
        self.portfolio = {}
        self.balance_history = [self.balance]
        self.load_data_json()

        # Configure grid weights
        master.grid_rowconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=1)
        master.grid_columnconfigure(0, weight=2)
        master.grid_columnconfigure(1, weight=2)
        master.grid_columnconfigure(2, weight=2)

        # Frame for stock monitoring on the left side
        self.left_frame = tk.Frame(master, bg='#2E3B4E')
        self.left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Stock Monitoring Section
        self.label = tk.Label(self.left_frame, text="Stock Search", font=("Helvetica", 30), bg='#2E3B4E', fg='white')
        self.label.pack(pady=10)

        self.ticker_entry = tk.Entry(self.left_frame, font=("Helvetica", 20), width=20)
        self.ticker_entry.pack(pady=10)
        self.ticker_entry.insert(0, "Enter Stock Ticker")

        self.get_price_button = tk.Button(self.left_frame, text="Get Price", command=self.get_stock_price, font=("Helvetica", 18), bg='#4CAF50', fg='white')
        self.get_price_button.pack(pady=5)

        self.launch_button = tk.Button(self.left_frame, text="Transaction", command=self.show_transaction, font=("Helvetica", 18), bg='#f44336', fg='white')
        self.launch_button.pack(pady=10)
        self.transactions = []
        # Matplotlib Figure for Stock Price Graph
        self.figure, self.ax = plt.subplots(figsize=(10, 5))
        self.canvas = FigureCanvasTkAgg(self.figure) 
        self.canvas.get_tk_widget().grid(row=0, column=1, padx=20, sticky="nsew")

        # Stock Simulator Section
        self.right_frame = tk.Frame(master, bg='#2E3B4E')
        self.right_frame.grid(row=0, column=2, padx=20, pady=20, sticky="nsew")
        self.simulator_label = tk.Label(self.right_frame, text="Stock Simulator", font=("Helvetica", 20), bg='#2E3B4E', fg='white')
        self.simulator_label.pack(pady=10)

        # Price Information
        self.price_label = tk.Label(self.right_frame, text="", font=("Helvetica", 10), bg='#2E3B4E', fg='white')
        self.price_label.pack(pady=5)

        self.open_label = tk.Label(self.right_frame, text="", font=("Helvetica", 10), bg='#2E3B4E', fg='white')
        self.open_label.pack(pady=5)

        self.close_label = tk.Label(self.right_frame, text="", font=("Helvetica", 10), bg='#2E3B4E', fg='white')
        self.close_label.pack(pady=5)

        self.volume_label = tk.Label(self.right_frame, text="", font=("Helvetica", 10), bg='#2E3B4E', fg='white')
        self.volume_label.pack(pady=5)

        self.amount_entry = tk.Entry(self.right_frame, font=("Helvetica", 10), width=30)
        self.amount_entry.pack(pady=10)
        self.amount_entry.insert(0, "Enter Amount to Buy/Sell")

        self.buy_button = tk.Button(self.right_frame, text="Buy", command=self.buy_stock, font=("Helvetica", 18), bg='#4CAF50', fg='white')
        self.buy_button.pack(pady=5)

        self.sell_button = tk.Button(self.right_frame, text="Sell", command=self.sell_stock, font=("Helvetica", 18), bg='#f44336', fg='white')
        self.sell_button.pack(pady=5)

        # Portfolio Section with Treeview
        self.portfolio_frame = tk.Frame(master, bg='#2E3B4E')
        self.portfolio_frame.grid(row=1, column=0, columnspan=2, pady=20, sticky="nsew")

        self.portfolio_label = tk.Label(self.portfolio_frame, text="Portfolio", font=("Helvetica", 30), bg='#2E3B4E', fg='white')
        self.portfolio_label.pack(pady=10)

        self.balance_label = tk.Label(self.portfolio_frame, text=f"Balance: ${self.balance:.2f}", font=("Helvetica", 20), bg='#2E3B4E', fg='white')
        self.balance_label.pack(pady=5)

        # Treeview for portfolio display
        self.tree = ttk.Treeview(self.portfolio_frame, columns=("Ticker", "Name", "Shares", "Price Bought", "Current Price", "Profit/Loss"), show='headings', height=10)
        self.tree.heading("Ticker", text="Ticker")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Shares", text="Number of Shares")
        self.tree.heading("Price Bought", text="Price Bought")
        self.tree.heading("Current Price", text="Current Price")
        self.tree.heading("Profit/Loss", text="Profit/Loss")

        for col in self.tree["columns"]:
            self.tree.column(col, anchor="center")
            self.tree.heading(col, text=col)

        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        # Frame for balance graph
        self.graph_frame = tk.Frame(master, bg='#2E3B4E')
        self.graph_frame.grid(row=1, column=2, pady=20, sticky="nsew")

        self.balance_figure, self.balance_ax = plt.subplots(figsize=(5, 5))
        self.balance_canvas = FigureCanvasTkAgg(self.balance_figure, master=self.graph_frame)
        self.balance_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Display S&P 500 information
        self.display_sp500_info()

        self.ticker_entry.delete(0, tk.END)  # Clear the entry
        self.ticker_entry.insert(0, "SPY")  # Set the ticker to S&P 500 ETF
        self.get_stock_price()  # Fetch stock price for S&P 500

        self.update_portfolio_display()  # Ensure portfolio is displayed on startup

    def display_sp500_info(self):
        sp500 = yf.Ticker("^GSPC")
        data = sp500.history(period="1d")
        if not data.empty:
            closing_price = data['Close'].iloc[-1]
            opening_price = data['Open'].iloc[-1]
            volume = data['Volume'].iloc[-1]

            sp500_info = f"S&P 500:\nClosing Price: ${closing_price:.2f}\nOpening Price: ${opening_price:.2f}\nVolume: {self.format_volume(volume)}"
            self.sp500_label = tk.Label(self.left_frame, text=sp500_info, font=("Helvetica", 14), bg='#2E3B4E', fg='white')
            self.sp500_label.pack(pady=10)

    def get_stock_price(self):
        ticker = self.ticker_entry.get().lower()
        try:
            stock = yf.Ticker(ticker)
            price_data = stock.history(period="1d")
            if not price_data.empty:
                self.current_price = price_data['Close'].iloc[-1]
                open_price = price_data['Open'].iloc[-1]
                volume = price_data['Volume'].iloc[-1]

                self.price_label.config(text=f"Current Price: ${self.current_price:.2f}")
                self.open_label.config(text=f"Opening Price: ${open_price:.2f}")
                self.close_label.config(text=f"Closing Price: ${self.current_price:.2f}")
                self.volume_label.config(text=f"Volume: {self.format_volume(volume)}")

                self.show_stock_graph(ticker)  # Show stock price graph
            else:
                messagebox.showerror("Error", "Error fetching data.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def format_volume(self, volume):
        if volume >= 1_000_000:
            return f"{volume / 1_000_000:.1f} million"
        elif volume >= 1_000:
            return f"{volume / 1_000:.0f} thousand"
        else:
            return str(volume)

    def show_stock_graph(self, ticker):
        stock = yf.Ticker(ticker)
        data = stock.history(period="1mo")  # Get the last month's data
        self.ax.clear()
        self.ax.plot(data.index, data['Close'], marker='o')
        self.ax.set_title(f"{ticker} Stock Price")
        self.ax.set_ylabel("Price ($)")
        self.ax.set_xlabel("Date")
        self.ax.grid()
        self.canvas.draw()

    def buy_stock(self):
        ticker = self.ticker_entry.get().upper()
        try:
            amount = int(self.amount_entry.get())
            if self.current_price is None:
                messagebox.showerror("Error", "Please fetch stock price first.")
                return

            total_cost = self.current_price * amount
            if total_cost > self.balance:
                messagebox.showerror("Error", "Insufficient balance.")
                return

            self.balance -= total_cost
            if ticker not in self.portfolio:
                self.portfolio[ticker] = {'shares': 0, 'price_bought': self.current_price}

            self.portfolio[ticker]['shares'] += amount
            self.portfolio[ticker]['price_bought'] = self.current_price  # Update price bought
            self.balance_label.config(text=f"Balance: ${self.balance:.2f}")
            self.balance_history.append(self.balance)
            self.update_portfolio_display()
            self.plot_balance_graph()
            messagebox.showinfo("Success", f"Bought {amount} shares of {ticker} at ${self.current_price:.2f} each.")

            self.save_data_json()  # Save data after buying
##########################################################################################
            self.transactions.append({"type": "buy", "symbol": ticker, "price": self.portfolio[ticker]['price_bought'], "quantity": amount})
            self.save_transactions()
################################################################
            ##################################################################
           # purchases_data = {"symbol": ticker, "price": self.portfolio[ticker]['price_bought'] , "quantity": amount}
           # with open("purchases.json", "a") as file:
                #file.write(json.dumps(purchases_data) + "," + "\n")

            ##############################################################################3
    

        except ValueError:
            messagebox.showerror("Error", "Invalid amount.")

    def sell_stock(self):
        ticker = self.ticker_entry.get().upper()
        try:
            amount = int(self.amount_entry.get())
            if ticker not in self.portfolio or self.portfolio[ticker]['shares'] < amount:
                messagebox.showerror("Error", "Not enough shares to sell.")
                return

            total_revenue = self.current_price * amount
            self.balance += total_revenue
            self.portfolio[ticker]['shares'] -= amount
            if self.portfolio[ticker]['shares'] == 0:
                del self.portfolio[ticker]

            self.balance_label.config(text=f"Balance: ${self.balance:.2f}")
            self.balance_history.append(self.balance)
            self.update_portfolio_display()
            self.plot_balance_graph()
            messagebox.showinfo("Success", f"Sold {amount} shares of {ticker} at ${self.current_price:.2f} each.")

            self.save_data_json()  # Save data after selling
###############################################################################################################
            self.transactions.append({"type": "sell", "symbol": ticker, "price": self.current_price, "quantity": amount})
            self.save_transactions()

            original_price = next((t["price"] for t in self.transactions if t["type"] == "buy" and t["symbol"] == ticker), None)
            if original_price is not None:
                profit_loss = self.current_price - original_price
                if profit_loss < 0:
                    profit_loss_data = {"symbol": ticker, "profit_loss": profit_loss}
                elif profit_loss > 0:
                    profit_loss_data = {"symbol": ticker, "profit_gain": profit_loss}
                elif profit_loss == 0:
                    profit_loss_data = {"symbol": ticker, "profit_loss": 0}
                with open("portfolio.json", "a") as file:
                    file.write(json.dumps(profit_loss_data) + "," + "\n")
                messagebox.showinfo("Profit/Loss", f"Profit/Loss for {ticker}: ${profit_loss:.2f}")

#########################################################################################
        #    try:
           #     with open("purchases.json", "r") as file:
         #           purchases_data = [json.loads(line.strip().rstrip(",")) for line in file if line.strip()]
        #    except FileNotFoundError:
          #           messagebox.showerror("Error", "No purchases found.")
          #           return
          #  for purchase in purchases_data:
                        # Remove the purchase if quantity becomes 0
          #      if purchase["quantity"] == 0:
          #              purchases_data.remove(purchase)
                        # Save updated purchases back to file
          #      with open("purchases.json", "w") as file:
           #             for purchase in purchases_data:
           #                 file.write(json.dumps(purchase) + ",\n")
######################################################################################
        except ValueError:
            messagebox.showerror("Error", "Invalid amount.")
    def view_trades(self):
        with open("purchases.json", "r") as file:
            json.dump(self.purchases, file, indent=4)
    def update_portfolio_display(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for ticker, data in self.portfolio.items():
            # Fetch the current price for the portfolio display
            stock = yf.Ticker(ticker)
            price_data = stock.history(period="1d")
            current_price = price_data['Close'].iloc[-1] if not price_data.empty else 0
            profit_loss = (current_price - data['price_bought']) * data['shares']
            self.tree.insert("", "end", values=(ticker, ticker, data['shares'], f"${data['price_bought']:.2f}", f"${current_price:.2f}", f"${profit_loss:.2f}"))

    def plot_balance_graph(self):
        self.balance_ax.clear()
        self.balance_ax.plot(self.balance_history, marker='o', color='blue')
        self.balance_ax.set_title("Balance Changes")
        self.balance_ax.set_ylabel("Balance ($)")
        self.balance_ax.set_xlabel("Transactions")
        self.balance_ax.grid()
        self.balance_canvas.draw()

    def save_data_json(self):
        data = {
            "portfolio": self.portfolio,
            "balance": self.balance,
            "balance_history": self.balance_history
        }
        with open("simulator_data.json", "w") as f:
            json.dump(data, f, indent=4)



    def load_data_json(self):
        if os.path.exists("simulator_data.json"):
            with open("simulator_data.json", "r") as f:
                data = json.load(f)
                self.portfolio = data.get("portfolio", {})
                self.balance = data.get("balance", 10000)
                self.balance_history = data.get("balance_history", [self.balance])
######################################################################################3
    def show_transaction(self):
        with open("transactions.json", "r") as file:
            transactions = json.load(file)
            transactions_window = tk.Toplevel(self.master)
            transactions_window.title("Transactions")
            transactions_window.geometry("400x600")
            text = tk.Text(transactions_window, wrap=tk.WORD)
            text.pack(expand=True, fill=tk.BOTH)
            text.insert(tk.END, json.dumps(transactions, indent=4))
            text.config(state=tk.DISABLED)

    def save_transactions(self):

        with open("transactions.json", "w") as file:
            json.dump(self.transactions, file, indent=4)
################################################################################33
if __name__ == "__main__":
    root = tk.Tk()
    app = StockApp(root)
    root.mainloop()