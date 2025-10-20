import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import gui_kvm, gui_chi


def main():
    root = tk.Tk()
    root.withdraw()

    #password = simpledialog.askstring("Login", "Inserisci la password:", show="*")

    #if not password:
    #    messagebox.showerror("Errore", "Password non inserita. Uscita.")
    #    root.destroy()
    #    return

    root.deiconify()
    root.title("Chameleon Cloud GUI")
    
    root.geometry("500x600")
    root.minsize(500, 400)

    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True, padx=10, pady=10)

    #kvm
    gui_kvm.create_kvm_tab(notebook, "")

    #chi
    gui_chi.create_chi_tab(notebook, "")



    root.mainloop()


if __name__ == "__main__":
    main()