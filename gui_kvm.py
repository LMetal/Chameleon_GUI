import threading
import tkinter as tk
from tkinter import ttk
import os
from tkinter import messagebox
from concurrent.futures import ThreadPoolExecutor

from utils import OpenStackManager
utils = None

flavor_dict = {}
images_dict = {}
keypairs = []
secgroups = []
networks = []
server_dict = {}


def init_dati_kvm(root, progressbar, loading_label, loaded_label, load_error_label, init_combo_callback):
    global server_dict, flavor_dict, images_dict, keypairs, secgroups, networks

    try:
        #progress bar
        root.after(0, lambda: progressbar.grid())
        root.after(0, progressbar.start)
        root.after(0, lambda: loading_label.grid())

        #creazione thread
        with ThreadPoolExecutor() as executor:
            futures = {
                'server': executor.submit(utils.get_server),
                'flavors': executor.submit(utils.get_flavors),
                'images': executor.submit(utils.get_images),
                'keypairs': executor.submit(utils.get_keypairs),
                'secgroups': executor.submit(utils.get_secgroup),
                'networks': executor.submit(utils.get_networks)
            }
            print(futures)

            results = {}
            for name, future in futures.items():
                results[name] = future.result()

        #print(results)
        #variabili globali
        server_dict = results['server']
        flavor_dict = results['flavors']
        images_dict = results['images']
        keypairs = results['keypairs']
        secgroups = results['secgroups']
        networks = results['networks']

        root.after(0, init_combo_callback)

    except Exception as e:
        import traceback
        print("DEBUG ERRORE:", repr(e))
        traceback.print_exc()
        root.after(0, messagebox.showerror, "Errore", f"Errore nel recupero dati: {e}")
        root.after(0, lambda: load_error_label.grid())
    finally:
        # Label + progress bar remove
        root.after(0, progressbar.stop)
        root.after(0, progressbar.grid_remove)
        root.after(0, loading_label.grid_remove)
        root.after(0, lambda: loaded_label.grid())


def aggiorna_server(root, progressbar_server, loading_label_server, loaded_label_server, load_error_label_server, aggiorna_combo_callback):
    global server_dict

    #progress bar
    root.after(0, lambda: progressbar_server.grid())
    root.after(0, progressbar_server.start)
    root.after(0, lambda: loading_label_server.grid())
    loaded_label_server.grid_remove()

    try:
        with ThreadPoolExecutor() as executor:
            futures = {
                'server': executor.submit(utils.get_server),
            }

            results = {}
            for name, future in futures.items():
                results[name] = future.result()

        #print(results)
        #aggiorna dati e GUI
        server_dict = results['server']
        root.after(0, aggiorna_combo_callback)

    except Exception as e:
        root.after(0, messagebox.showerror, "Errore", f"Errore nel recupero dati: {e}")
        root.after(0, lambda: load_error_label_server.grid())
    finally:
        #rimuovi progress bar
        root.after(0, progressbar_server.stop)
        root.after(0, progressbar_server.grid_remove)
        root.after(0, loading_label_server.grid_remove)
        root.after(0, lambda: loaded_label_server.grid())


def create_kvm_tab(notebook, password):
    global utils
    utils = OpenStackManager("app-cred-KVM@TACC.sh")
    tab = ttk.Frame(notebook)
    notebook.add(tab, text="KVM@TACC")

    #top
    top_frame = tk.LabelFrame(tab, text="Avvia macchina virtuale", padx=10, pady=10, font=("Arial", 10, "bold"))
    top_frame.pack(side='top', fill='both', expand=True, padx=10, pady=10)

    #bottom
    bottom_frame = tk.LabelFrame(tab, text="Elimina macchina virtuale", padx=10, pady=10, font=("Arial", 10, "bold"))
    bottom_frame.pack(side='bottom', fill='both', expand=True, padx=10, pady=10)

    #top frame
    tk.Label(top_frame, text="Nome Istanza:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
    name = tk.Entry(top_frame)
    name.grid(row=0, column=1, sticky='w', padx=5, pady=5)

    tk.Label(top_frame, text="Seleziona Flavor:").grid(row=1, column=0)
    combo_flavor = ttk.Combobox(top_frame, state='readonly')
    combo_flavor.grid(row=1, column=1)

    tk.Label(top_frame, text="Seleziona Immagine:").grid(row=2, column=0)
    combo_image = ttk.Combobox(top_frame, state='readonly')
    combo_image.grid(row=2, column=1)

    tk.Label(top_frame, text="Seleziona Coppia di Chiavi:").grid(row=3, column=0)
    combo_key = ttk.Combobox(top_frame, state='readonly')
    combo_key.grid(row=3, column=1)

    tk.Label(top_frame, text="Seleziona Gruppo di Sicurezza:").grid(row=4, column=0)
    combo_sec = ttk.Combobox(top_frame, state='readonly')
    combo_sec.grid(row=4, column=1)

    tk.Label(top_frame, text="Seleziona Network:").grid(row=5, column=0)
    combo_net = ttk.Combobox(top_frame, state='readonly')
    combo_net.grid(row=5, column=1)

    var_ip = tk.IntVar()
    check_ip = tk.Checkbutton(top_frame, text='Associa nuovo floating IP', variable=var_ip, onvalue=1, offvalue=0)
    check_ip.grid(row=7, column=0, columnspan=2, pady=5)

    status_label = tk.Label(top_frame, text="", fg="blue")
    status_label.grid(row=8, column=0, columnspan=2)

    loading_label = tk.Label(top_frame, text="Caricamento dati in corso...", fg="blue")
    loading_label.grid(row=9, column=0, columnspan=2)
    loading_label.grid_remove()

    loaded_label = tk.Label(top_frame, text="Dati caricati con successo", fg="green")
    loaded_label.grid(row=9, column=0, columnspan=2)
    loaded_label.grid_remove()

    load_error_label = tk.Label(top_frame, text="Errore caricamento dati", fg="red")
    load_error_label.grid(row=9, column=0, columnspan=2)
    load_error_label.grid_remove()

    progressbar = ttk.Progressbar(top_frame, mode='indeterminate', length=250)
    progressbar.grid(row=10, column=0, columnspan=2, pady=5)
    progressbar.grid_remove()



    #bottom frame
    tk.Label(bottom_frame, text="Seleziona Server:").grid(row=0, column=0)
    combo_server = ttk.Combobox(bottom_frame, state='readonly')
    combo_server.grid(row=0, column=1)

    var_ip2 = tk.IntVar()
    check_ip2 = tk.Checkbutton(bottom_frame, text='Rilascia floating IP', variable=var_ip2, onvalue=1, offvalue=0)
    check_ip2.grid(row=1, column=0, columnspan=2, pady=5)

    loading_label_server = tk.Label(bottom_frame, text="Caricamento dati in corso...", fg="blue")
    loading_label_server.grid(row=3, column=0, columnspan=2)
    loading_label_server.grid_remove()

    loaded_label_server = tk.Label(bottom_frame, text="Dati caricati con successo", fg="green")
    loaded_label_server.grid(row=3, column=0, columnspan=2)
    loaded_label_server.grid_remove()

    load_error_label_server = tk.Label(bottom_frame, text="Errore caricamento dati", fg="red")
    load_error_label_server.grid(row=3, column=0, columnspan=2)
    load_error_label_server.grid_remove()

    progressbar_server = ttk.Progressbar(bottom_frame, mode='indeterminate', length=250)
    progressbar_server.grid(row=4, column=0, columnspan=2, pady=5)
    progressbar_server.grid_remove()


    def init_combo():
        combo_flavor['values'] = list(flavor_dict)
        combo_image['values'] = list(images_dict)
        combo_key['values'] = list(keypairs)
        combo_sec['values'] = list(secgroups)
        combo_server['values'] = list(server_dict)
        combo_net['values'] = list(networks)

    def aggiorna_combobox_server():
        combo_server['values'] = list(server_dict)

    def start():
        if not combo_image.get() or not combo_key.get() or not combo_flavor.get() or not combo_sec.get() or not name.get():
            messagebox.showerror("Errore", "Campi necessari non compilati")
        else:
            flavor = combo_flavor.get()
            image_id = images_dict.get(combo_image.get())
            key = combo_key.get()
            sec_group = combo_sec.get()
            network = combo_net.get()
            machine_name = name.get()
            
            status_label.config(text="Creazione macchina virtuale in corso...")
            error = utils.create_virtual_machine(flavor, image_id, key, sec_group, network, machine_name)

            #if error is not None:
            #    status_label.config(text="Errore nella creazione")
            #    return
            #print("Macchina creata")

            if var_ip.get() == 1:
                id_floating_ip, addr_floating_ip = utils.new_floating_ip(name.get())
                utils.add_floating_ip(machine_name, id_floating_ip)
                messagebox.showinfo("Macchina creata con successo", f"Accedi con:\nssh cc@{addr_floating_ip}")

            status_label.config(text="Macchina creata con successo")

            # Reset campi
            combo_flavor.set('')
            combo_image.set('')
            combo_key.set('')
            combo_sec.set('')
            combo_net.set('')
            name.delete(0, tk.END)
            var_ip.set(0)
            status_label.config(text="Pronto per una nuova creazione.")

            threading.Thread(target=lambda: aggiorna_server(
                tab.winfo_toplevel(), progressbar_server, loading_label_server,
                loaded_label_server, load_error_label_server, aggiorna_combobox_server
            )).start()

    def delete():
        server_name = combo_server.get()
        floating_delete = var_ip2.get()

        if server_name:
            try:
                utils.delete_server(server_name)
                print(server_dict)
                if floating_delete == 1 and server_dict.get(server_name)[1] is not None:
                    utils.delete_floating_ip(server_dict.get(server_name)[1])
                    messagebox.showinfo("Successo", "Server e floating IP eliminati con successo")
                else:
                    messagebox.showinfo("Successo", "Server eliminato con successo")

                combo_server.set('')
                var_ip2.set(0)
                threading.Thread(target=lambda: aggiorna_server(
                    tab.winfo_toplevel(), progressbar_server, loading_label_server,
                    loaded_label_server, load_error_label_server, aggiorna_combobox_server
                )).start()
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nell'eliminazione: {e}")
        else:
            messagebox.showerror("Errore", "Seleziona un server")

    def aggiorna_server_thread():
        threading.Thread(target=lambda: aggiorna_server(
            tab.winfo_toplevel(), progressbar_server, loading_label_server,
            loaded_label_server, load_error_label_server, aggiorna_combobox_server
        )).start()

    #bottoni
    b = tk.Button(top_frame, text="Lancia Macchina Virtuale", command=start)
    b.grid(row=6, column=0, columnspan=2, pady=15)

    btn_aggiorna_server = ttk.Button(bottom_frame, text="Ricarica", command=aggiorna_server_thread)
    btn_aggiorna_server.grid(row=0, column=2)

    b2 = tk.Button(bottom_frame, text="Elimina Macchina Virtuale", command=delete)
    b2.grid(row=2, column=0, columnspan=2, pady=15)

    #start
    threading.Thread(target=lambda: init_dati_kvm(
        tab.winfo_toplevel(), progressbar, loading_label, loaded_label, load_error_label, init_combo
    )).start()

    return tab