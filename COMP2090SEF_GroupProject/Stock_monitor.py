import tkinter as tk
from tkinter import ttk, messagebox, END
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import yfinance as yf
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class StockMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(" Stock Monitoring System")
        self.root.geometry("1000x700")
        self.symbols = ["AAPL", "GOOGL", "AMZN", "MSFT"]
        
        # Configure custom styles
        self.style = tb.Style()
        self.style.configure("TButton", font=('Helvetica', 10))
        self.style.configure("Header.TLabel", font=('Helvetica', 16, 'bold'))
        self.style.configure("Accent.TFrame", background=self.style.colors.primary)

        self.setup_ui()

    def setup_ui(self):
        # Header section
        header_frame = tb.Frame(self.root, style="Accent.TFrame")
        header_frame.pack(fill="x", pady=(0, 15))
        tb.Label(
            header_frame,
            text="STOCK MONITOR",
            font=('Helvetica', 20, 'bold'),
            bootstyle=(INVERSE, PRIMARY)
        ).pack(pady=15)

        # Symbol input section
        input_frame = tb.Frame(self.root)
        input_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.symbol_entry = tb.Entry(
            input_frame,
            width=25,
            bootstyle=PRIMARY,
            foreground="#a0a0a0"
        )
        self.symbol_entry.insert(0, "Enter stock symbol...")
        self.symbol_entry.bind("<FocusIn>", lambda e: self.symbol_entry.delete(0, END))
        self.symbol_entry.pack(side="left", padx=5)

        tb.Button(
            input_frame,
            text="➕ Add Symbol",
            command=self.add_symbol,
            bootstyle=(SUCCESS, OUTLINE),
            width=15
        ).pack(side="left", padx=5)

        # Price list section
        self.tree = tb.Treeview(
            self.root,
            columns=("Price",),
            show="headings",
            bootstyle=PRIMARY,
            height=5
        )
        self.tree.heading("Price", text="REALTIME PRICES (USD)", )
        self.tree.column("Price", width=250)
        self.tree.pack(pady=10, fill="x", padx=15)
        
        self.update_prices()

        # Chart controls section
        chart_controls = tb.Frame(self.root)
        chart_controls.pack(pady=15, padx=15, fill="x")

        tb.Label(
            chart_controls,
            text="Chart Symbol:",
            font=('Helvetica', 10, 'bold')
        ).pack(side="left", padx=5)

        self.selected_symbol = tk.StringVar()
        self.symbol_dropdown = tb.Combobox(
            chart_controls,
            textvariable=self.selected_symbol,
            values=self.symbols,
            bootstyle=PRIMARY,
            width=15
        )
        self.symbol_dropdown.current(0)
        self.symbol_dropdown.pack(side="left", padx=5)

        tb.Button(
            chart_controls,
            text="Show Chart",
            command=self.plot_chart,
            bootstyle=(INFO, OUTLINE),
            width=15
        ).pack(side="left", padx=5)

        # Chart container
        self.chart_frame = tb.Frame(
            self.root,
            bootstyle=PRIMARY,
            padding=10,
            relief=tk.GROOVE
        )
        self.chart_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def add_symbol(self):
        new_symbol = self.symbol_entry.get().strip().upper()
        if new_symbol and new_symbol not in self.symbols:
            self.symbols.append(new_symbol)
            self.symbol_dropdown["values"] = self.symbols
            self.update_prices()
            messagebox.showinfo("Success", f"{new_symbol} added successfully!")
        else:
            messagebox.showerror("Error", "Invalid or duplicate symbol!")

    def update_prices(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for idx, symbol in enumerate(self.symbols):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            try:
                ticker = yf.Ticker(symbol)
                price = ticker.fast_info.last_price
                self.tree.insert("", "end", values=(f"{symbol}: ${price:.2f}",), tags=(tag,))
            except:
                self.tree.insert("", "end", values=(f"{symbol}: Error fetching price",), tags=(tag,))

    def plot_chart(self):
        symbol = self.selected_symbol.get()
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        try:
            # Add chart header
            tb.Label(
                self.chart_frame,
                text=f"{symbol} - 30 DAY PRICE HISTORY",
                font=('Helvetica', 12, 'bold'),
                anchor=tk.CENTER
            ).pack(pady=(0, 10), fill="x")

            # Plot data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1mo")
            
            if not hist.empty:
                fig, ax = plt.subplots(figsize=(8, 4))
                fig.patch.set_facecolor(self.style.colors.bg)
                ax.set_facecolor(self.style.colors.bg)
                
                # Style the plot
                ax.tick_params(colors=self.style.colors.fg)
                ax.title.set_color(self.style.colors.primary)
                ax.spines['bottom'].set_color(self.style.colors.fg)
                ax.spines['left'].set_color(self.style.colors.fg)

                ax.plot(hist.index, hist["Close"], 
                       label="Closing Price", 
                       color=self.style.colors.success,
                       linewidth=2)
                
                ax.set_title(f"{symbol} Price Movement", pad=20)
                ax.set_xlabel("Date", color=self.style.colors.fg, labelpad=10)
                ax.set_ylabel("Price (USD)", color=self.style.colors.fg, labelpad=10)
                ax.legend()

                # Embed in Tkinter
                canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True)
            else:
                messagebox.showwarning("No Data", f"No historical data for {symbol}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate chart: {str(e)}")

if __name__ == "__main__":
    root = tb.Window(themename="superhero")
    app = StockMonitorApp(root)
    root.mainloop()
