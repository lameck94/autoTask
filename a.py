import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Function to load data from an Excel file
def load_data():
    file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx"), ("Excel Files", "*.xls")])
    if not file_path:
        return  # User canceled file selection
    
    try:
        xls = pd.ExcelFile(file_path)
        sheet_name = "Sheet1" if "Sheet1" in xls.sheet_names else xls.sheet_names[1]  # Use first sheet if "Sheet1" is not found
        df = pd.read_excel(xls, sheet_name=sheet_name)
        
        if df.shape[0] < 4 or df.shape[1] < 21:
            messagebox.showerror("Error", "Invalid file format. Please select a valid data file.")
            return
        
        df_clean = df.iloc[3:, [13, 17, 18, 19, 20]].dropna()
        df_clean.columns = ["M/TSR Name", "0 Days Customers", "0-3 Days Customers", "0-5 Days Customers", "0-7 Days Customers"]
        
        for col in ["0 Days Customers", "0-3 Days Customers", "0-5 Days Customers", "0-7 Days Customers"]:
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
        
        df_grouped = df_clean.groupby("M/TSR Name").sum().reset_index()
        
        populate_tree(df_grouped)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load data: {e}")

def populate_tree(df):
    for row in tree.get_children():
        tree.delete(row)
    for _, row in df.iterrows():
        tree.insert("", tk.END, values=(row["M/TSR Name"], row["0 Days Customers"], row["0-3 Days Customers"], row["0-5 Days Customers"], row["0-7 Days Customers"]))

# Create main application window
root = tk.Tk()
root.title("Customer Summary")

# Create treeview to display data
tree = ttk.Treeview(root, columns=("M/TSR Name", "0 Days Customers", "0-3 Days Customers", "0-5 Days Customers", "0-7 Days Customers"), show="headings")
tree.heading("M/TSR Name", text="M/TSR Name")
tree.heading("0 Days Customers", text="0 Days Customers")
tree.heading("0-3 Days Customers", text="0-3 Days Customers")
tree.heading("0-5 Days Customers", text="0-5 Days Customers")
tree.heading("0-7 Days Customers", text="0-7 Days Customers")
tree.pack(fill=tk.BOTH, expand=True)

# Add Load File button
btn_load = tk.Button(root, text="Load File", command=load_data)
btn_load.pack()

# Run the application
root.mainloop()
