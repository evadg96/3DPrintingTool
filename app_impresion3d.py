import customtkinter as ctk
import json
import os
from datetime import datetime

# Crear carpeta en Documentos para evitar el bloqueo de macOS
USER_DIR = os.path.expanduser("~/Documents/Gestor3D")
os.makedirs(USER_DIR, exist_ok=True)
DATA_FILE = os.path.join(USER_DIR, "impresiones_data.json")

DEFAULT_DATA = {
    "filamentos": {},
    "historial": [],
    "clientes": {},
    "pedidos": [],
    "config": {
        "precio_kwh": 0.15,
        "consumo_watts": 65,
        "consumo_pico_watts": 350,
        "mins_preparacion": 6,
        "precio_impresora": 400,
        "horas_vida": 5000,
        "margen_beneficio": 0
    }
}

class App3D(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gestor de Impresión 3D Pro")
        self.geometry("1050x850")
        ctk.set_appearance_mode("dark")
        
        self.data = self.load_data()
        self.placas_widgets = []
        
        # Modos de edición activa
        self.editing_filamento_id = None
        self.editing_cliente_name = None
        self.editing_pedido_index = None
        self.editing_historial_index = None
        
        # Sistema de Pestañas
        self.tabview = ctk.CTkTabview(self, width=1000, height=800)
        self.tabview.pack(padx=15, pady=15, fill="both", expand=True)
        
        self.tab_calc = self.tabview.add("Calculadora")
        self.tab_fil = self.tabview.add("Filamentos")
        self.tab_hist = self.tabview.add("Impresiones")
        self.tab_pedidos = self.tabview.add("Pedidos / Clientes")
        self.tab_stats = self.tabview.add("Estadísticas")
        self.tab_conf = self.tabview.add("Configuración")
        
        self.build_calculadora()
        self.build_filamentos()
        self.build_historial()
        self.build_pedidos()
        self.build_estadisticas()
        self.build_configuracion()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    data = json.load(f)
                    if "clientes" not in data: data["clientes"] = {}
                    if "pedidos" not in data: data["pedidos"] = []
                    if "consumo_pico_watts" not in data.get("config", {}):
                        data["config"]["consumo_pico_watts"] = 350
                    if "mins_preparacion" not in data.get("config", {}):
                        data["config"]["mins_preparacion"] = 6
                    return data
            except Exception:
                return DEFAULT_DATA
        return DEFAULT_DATA

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f, indent=4)

    # --- PESTAÑA: CALCULADORA ---
    def build_calculadora(self):
        for w in self.tab_calc.winfo_children(): w.destroy()
        self.placas_widgets = []

        header = ctk.CTkFrame(self.tab_calc, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(header, text="Simulador de Proyectos y Multi-Placa", font=("Arial", 20, "bold")).pack(side="left")
        
        top_bar = ctk.CTkFrame(self.tab_calc, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=5)
        
        self.calc_nombre = ctk.CTkEntry(top_bar, placeholder_text="Nombre del proyecto / artículo (ej. Soporte PS4)", width=450)
        self.calc_nombre.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(top_bar, text="+ Añadir Otra Placa", fg_color="purple", hover_color="darkmagenta", command=self.add_placa_widget).pack(side="left")

        self.scroll_placas = ctk.CTkScrollableFrame(self.tab_calc, width=950, height=450)
        self.scroll_placas.pack(pady=10, padx=10, fill="both", expand=True)

        bottom_bar = ctk.CTkFrame(self.tab_calc)
        bottom_bar.pack(fill="x", padx=10, pady=10)

        self.lbl_resultado = ctk.CTkLabel(bottom_bar, text="Coste Total Proyecto: 0.00 €", font=("Arial", 16, "bold"))
        self.lbl_resultado.pack(side="left", padx=15, pady=10)

        btn_group = ctk.CTkFrame(bottom_bar, fg_color="transparent")
        btn_group.pack(side="right", padx=10)

        ctk.CTkButton(btn_group, text="Calcular Proyecto", fg_color="blue", command=self.calcular_coste_proyecto).pack(side="left", padx=5)
        ctk.CTkButton(btn_group, text="Guardar Proyecto (Descontar Stock)", fg_color="green", command=self.guardar_impresion).pack(side="left", padx=5)

        self.add_placa_widget()

    def add_placa_widget(self):
        num_placa = len(self.placas_widgets) + 1
        placa_frame = ctk.CTkFrame(self.scroll_placas, border_width=1, border_color="gray40")
        placa_frame.pack(fill="x", padx=5, pady=8, expand=True)

        title_bar = ctk.CTkFrame(placa_frame, fg_color="transparent")
        title_bar.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(title_bar, text=f"Placa / Bandeja #{num_placa}", font=("Arial", 14, "bold"), text_color="cyan").pack(side="left")
        
        if num_placa > 1:
            ctk.CTkButton(title_bar, text="Eliminar Placa", width=100, fg_color="red", hover_color="darkred", 
                           command=lambda p=placa_frame: self.remove_placa_widget(p)).pack(side="right")

        time_frame = ctk.CTkFrame(placa_frame, fg_color="transparent")
        time_frame.pack(fill="x", padx=10, pady=2)
        
        ctk.CTkLabel(time_frame, text="Tiempo de impresión:").pack(side="left", padx=(0, 10))
        entry_h = ctk.CTkEntry(time_frame, placeholder_text="Horas", width=80)
        entry_h.pack(side="left", padx=2)
        entry_m = ctk.CTkEntry(time_frame, placeholder_text="Mins", width=80)
        entry_m.pack(side="left", padx=2)

        fils_container = ctk.CTkFrame(placa_frame, fg_color="transparent")
        fils_container.pack(fill="x", padx=10, pady=5)

        placa_data = {
            "frame": placa_frame,
            "horas": entry_h,
            "mins": entry_m,
            "fils_container": fils_container,
            "filamentos_rows": []
        }
        
        self.placas_widgets.append(placa_data)
        
        btn_add_fil = ctk.CTkButton(placa_frame, text="+ Añadir Filamento/Color (AMS)", width=180, fg_color="gray30", 
                                    hover_color="gray40", command=lambda pd=placa_data: self.add_filamento_to_placa(pd))
        btn_add_fil.pack(anchor="w", padx=10, pady=(0, 8))

        self.add_filamento_to_placa(placa_data)

    def remove_placa_widget(self, placa_frame):
        self.placas_widgets = [p for p in self.placas_widgets if p["frame"] != placa_frame]
        placa_frame.destroy()
        for i, p in enumerate(self.placas_widgets):
            for child in p["frame"].winfo_children():
                if isinstance(child, ctk.CTkFrame):
                    for sub in child.winfo_children():
                        if isinstance(sub, ctk.CTkLabel) and "Placa / Bandeja #" in sub.cget("text"):
                            sub.configure(text=f"Placa / Bandeja #{i+1}")

    def add_filamento_to_placa(self, placa_data):
        row_frame = ctk.CTkFrame(placa_data["fils_container"], fg_color="transparent")
        row_frame.pack(fill="x", pady=2)

        lista_fils = self.get_filamentos_list()
        val_init = lista_fils[0] if lista_fils else "No hay filamentos"
        
        var_fil = ctk.StringVar(value=val_init)
        menu_fil = ctk.CTkOptionMenu(row_frame, variable=var_fil, values=lista_fils or ["No hay filamentos"], width=350)
        menu_fil.pack(side="left", padx=(0, 10))

        entry_g = ctk.CTkEntry(row_frame, placeholder_text="Gramos (g)", width=100)
        entry_g.pack(side="left", padx=5)

        row_data = {"frame": row_frame, "var": var_fil, "gramos": entry_g, "menu": menu_fil}
        placa_data["filamentos_rows"].append(row_data)

        if len(placa_data["filamentos_rows"]) > 1:
            btn_del = ctk.CTkButton(row_frame, text="X", width=30, fg_color="firebrick", 
                                    command=lambda r=row_data, pd=placa_data: self.remove_filamento_from_placa(pd, r))
            btn_del.pack(side="left", padx=5)

    def remove_filamento_from_placa(self, placa_data, row_data):
        placa_data["filamentos_rows"] = [r for r in placa_data["filamentos_rows"] if r != row_data]
        row_data["frame"].destroy()

    # --- PESTAÑA: FILAMENTOS ---
    def build_filamentos(self):
        for w in self.tab_fil.winfo_children(): w.destroy()

        ctk.CTkLabel(self.tab_fil, text="Gestión de Stock y Rollos", font=("Arial", 18, "bold")).pack(pady=5)
        
        form_frame = ctk.CTkFrame(self.tab_fil)
        form_frame.pack(pady=5, padx=10, fill="x")
        
        self.fil_marca = ctk.CTkEntry(form_frame, placeholder_text="Marca (ej. Sunlu, Bambu)*")
        self.fil_marca.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        tipos_disponibles = ["PLA", "PETG", "ABS", "TPU", "ASA", "Otro..."]
        self.fil_tipo_var = ctk.StringVar(value="PLA")
        self.menu_tipo = ctk.CTkOptionMenu(form_frame, variable=self.fil_tipo_var, values=tipos_disponibles, command=self.check_custom_tipo)
        self.menu_tipo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        colores_disponibles = ["Negro", "Blanco", "Gris", "Rojo", "Azul", "Verde", "Amarillo", "Naranja", "Rosa", "Morado", "Transparente", "Marmol", "Madera", "Plateado", "Dorado", "Otro..."]
        self.fil_color_var = ctk.StringVar(value="Negro")
        self.menu_color = ctk.CTkOptionMenu(form_frame, variable=self.fil_color_var, values=colores_disponibles, command=self.check_custom_color)
        self.menu_color.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.fil_tipo_custom = ctk.CTkEntry(form_frame, placeholder_text="Tipo específico...")
        self.fil_color_custom = ctk.CTkEntry(form_frame, placeholder_text="Color específico...")

        self.fil_acabado = ctk.CTkOptionMenu(form_frame, values=["Mate", "Brillo", "Seda / Silk", "Metálico", "Fluorescente", "Glitter"])
        self.fil_acabado.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        self.fil_acabado.set("Mate")
        
        self.fil_peso = ctk.CTkEntry(form_frame, placeholder_text="Peso total (g, ej. 1000)*")
        self.fil_peso.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        self.fil_disponible = ctk.CTkEntry(form_frame, placeholder_text="Gramos disp. (opcional)")
        self.fil_disponible.grid(row=2, column=2, padx=5, pady=5, sticky="ew")
        
        self.fil_precio = ctk.CTkEntry(form_frame, placeholder_text="Precio (€, ej. 19.99)*")
        self.fil_precio.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(2, weight=1)

        btn_box = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_box.grid(row=4, column=0, columnspan=3, pady=8, sticky="ew")

        self.btn_save_fil = ctk.CTkButton(btn_box, text="Añadir Nuevo Rollo", fg_color="green", command=self.add_filamento)
        self.btn_save_fil.pack(side="left", fill="x", expand=True, padx=2)

        self.btn_cancel_fil = ctk.CTkButton(btn_box, text="Cancelar Edición", fg_color="gray40", command=self.cancel_edit_filamento)

        self.lbl_fil_msg = ctk.CTkLabel(form_frame, text="", font=("Arial", 12))
        self.lbl_fil_msg.grid(row=5, column=0, columnspan=3, pady=(0, 5))

        search_frame = ctk.CTkFrame(self.tab_fil, fg_color="transparent")
        search_frame.pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(search_frame, text="Filtrar filamentos:").pack(side="left", padx=5)
        self.fil_search = ctk.CTkEntry(search_frame, placeholder_text="Escribe para buscar...")
        self.fil_search.pack(side="left", padx=5, fill="x", expand=True)
        self.fil_search.bind("<KeyRelease>", lambda e: self.actualizar_vista_stock())

        self.scroll_stock = ctk.CTkScrollableFrame(self.tab_fil, width=890, height=200)
        self.scroll_stock.pack(pady=5, padx=10, fill="both", expand=True)
        
        self.actualizar_vista_stock()

    def check_custom_tipo(self, choice):
        if choice == "Otro...":
            self.fil_tipo_custom.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        else:
            self.fil_tipo_custom.grid_forget()

    def check_custom_color(self, choice):
        if choice == "Otro...":
            self.fil_color_custom.grid(row=1, column=2, padx=5, pady=2, sticky="ew")
        else:
            self.fil_color_custom.grid_forget()

    def edit_filamento(self, id_fil):
        v = self.data["filamentos"][id_fil]
        self.editing_filamento_id = id_fil
        
        self.fil_marca.delete(0, 'end')
        self.fil_marca.insert(0, v['marca'])
        
        if v['tipo'] in ["PLA", "PETG", "ABS", "TPU", "ASA"]:
            self.fil_tipo_var.set(v['tipo'])
            self.fil_tipo_custom.grid_forget()
        else:
            self.fil_tipo_var.set("Otro...")
            self.fil_tipo_custom.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
            self.fil_tipo_custom.delete(0, 'end')
            self.fil_tipo_custom.insert(0, v['tipo'])

        if v['color'] in ["Negro", "Blanco", "Gris", "Rojo", "Azul", "Verde", "Amarillo", "Naranja", "Rosa", "Morado", "Transparente", "Marmol", "Madera", "Plateado", "Dorado"]:
            self.fil_color_var.set(v['color'])
            self.fil_color_custom.grid_forget()
        else:
            self.fil_color_var.set("Otro...")
            self.fil_color_custom.grid(row=1, column=2, padx=5, pady=2, sticky="ew")
            self.fil_color_custom.delete(0, 'end')
            self.fil_color_custom.insert(0, v['color'])

        self.fil_acabado.set(v.get('acabado', 'Mate'))
        
        self.fil_peso.delete(0, 'end')
        self.fil_peso.insert(0, str(v['peso_inicial']))

        self.fil_disponible.delete(0, 'end')
        self.fil_disponible.insert(0, str(v.get('restante', v['peso_inicial'])))
        
        self.fil_precio.delete(0, 'end')
        self.fil_precio.insert(0, str(v['precio']))

        self.btn_save_fil.configure(text="Guardar Cambios en Filamento", fg_color="orange")
        self.btn_cancel_fil.pack(side="right", padx=2)

    def cancel_edit_filamento(self):
        self.editing_filamento_id = None
        self.fil_marca.delete(0, 'end')
        self.fil_peso.delete(0, 'end')
        self.fil_disponible.delete(0, 'end')
        self.fil_precio.delete(0, 'end')
        self.fil_tipo_custom.delete(0, 'end')
        self.fil_color_custom.delete(0, 'end')
        self.fil_tipo_custom.grid_forget()
        self.fil_color_custom.grid_forget()
        self.fil_tipo_var.set("PLA")
        self.fil_color_var.set("Negro")
        self.fil_acabado.set("Mate")

        self.btn_save_fil.configure(text="Añadir Nuevo Rollo", fg_color="green")
        self.btn_cancel_fil.pack_forget()

    def add_filamento(self):
        marca = self.fil_marca.get().strip()
        if not marca:
            self.lbl_fil_msg.configure(text="❌ Error: Debes indicar la marca del filamento.", text_color="red")
            return

        tipo = self.fil_tipo_custom.get().strip() if self.fil_tipo_var.get() == "Otro..." else self.fil_tipo_var.get()
        color = self.fil_color_custom.get().strip() if self.fil_color_var.get() == "Otro..." else self.fil_color_var.get()

        try:
            peso_inicial = float(self.fil_peso.get().strip().replace(',', '.'))
            precio = float(self.fil_precio.get().strip().replace(',', '.'))
            if peso_inicial <= 0 or precio < 0: raise ValueError
        except ValueError:
            self.lbl_fil_msg.configure(text="❌ Error: Revisa peso total y precio.", text_color="red")
            return

        disp_str = self.fil_disponible.get().strip().replace(',', '.')
        if disp_str:
            try:
                restante = float(disp_str)
                if restante < 0: restante = 0.0
            except ValueError:
                self.lbl_fil_msg.configure(text="❌ Error: El peso disponible debe ser un número.", text_color="red")
                return
        else:
            restante = peso_inicial

        new_id_fil = f"{marca} {tipo} ({color})"
        
        if self.editing_filamento_id:
            old_id = self.editing_filamento_id
            
            # Si cambió de nombre, actualizamos en cascada el historial de impresiones
            if old_id != new_id_fil:
                del self.data["filamentos"][old_id]
                for h in self.data["historial"]:
                    if h.get("filamento") == old_id:
                        h["filamento"] = new_id_fil
                    for item in h.get("desglose_filamentos", []):
                        if item["filamento"] == old_id:
                            item["filamento"] = new_id_fil
            
            self.data["filamentos"][new_id_fil] = {
                "marca": marca, "tipo": tipo, "color": color, 
                "acabado": self.fil_acabado.get(),
                "peso_inicial": peso_inicial, 
                "restante": restante, 
                "precio": precio
            }
            self.lbl_fil_msg.configure(text="✅ ¡Filamento actualizado en cascada!", text_color="lightgreen")
            self.cancel_edit_filamento()
        else:
            self.data["filamentos"][new_id_fil] = {
                "marca": marca, "tipo": tipo, "color": color, 
                "acabado": self.fil_acabado.get(),
                "peso_inicial": peso_inicial, "restante": restante, "precio": precio
            }
            self.lbl_fil_msg.configure(text=f"✅ ¡Rollo '{new_id_fil}' añadido!", text_color="lightgreen")
            self.cancel_edit_filamento()

        self.save_data()
        self.actualizar_vista_stock()
        self.actualizar_vista_historial()
        self.actualizar_vista_estadisticas()
        self.update_all_filamentos_menus()
        self.after(3000, lambda: self.lbl_fil_msg.configure(text=""))

    def ajustar_gramos_rapido(self, id_fil, entry_widget):
        try:
            nuevo_peso = float(entry_widget.get().strip().replace(',', '.'))
            if nuevo_peso < 0: nuevo_peso = 0.0
            self.data["filamentos"][id_fil]["restante"] = nuevo_peso
            self.save_data()
            self.actualizar_vista_stock()
            self.update_all_filamentos_menus()
        except ValueError:
            pass

    # --- PESTAÑA: HISTORIAL ---
    def build_historial(self):
        for w in self.tab_hist.winfo_children(): w.destroy()
        ctk.CTkLabel(self.tab_hist, text="Historial de Impresiones y Proyectos", font=("Arial", 18, "bold")).pack(pady=5)
        
        self.scroll_hist = ctk.CTkScrollableFrame(self.tab_hist, width=910, height=520)
        self.scroll_hist.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.actualizar_vista_historial()

    # --- PESTAÑA: PEDIDOS / CLIENTES ---
    def build_pedidos(self):
        for w in self.tab_pedidos.winfo_children(): w.destroy()

        ctk.CTkLabel(self.tab_pedidos, text="Gestión de Clientes y Pedidos", font=("Arial", 18, "bold")).pack(pady=5)
        
        main_ped_frame = ctk.CTkFrame(self.tab_pedidos, fg_color="transparent")
        main_ped_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # --- BLOQUE IZQUIERDO: CLIENTES ---
        left_frame = ctk.CTkFrame(main_ped_frame, width=330)
        left_frame.pack(side="left", fill="y", padx=5, pady=5)
        
        self.lbl_cli_title = ctk.CTkLabel(left_frame, text="Nuevo Cliente", font=("Arial", 14, "bold"))
        self.lbl_cli_title.pack(pady=5)
        
        self.cli_nombre = ctk.CTkEntry(left_frame, placeholder_text="Nombre del cliente *")
        self.cli_nombre.pack(pady=4, padx=10, fill="x")
        self.cli_tel = ctk.CTkEntry(left_frame, placeholder_text="Teléfono (opcional)")
        self.cli_tel.pack(pady=4, padx=10, fill="x")
        self.cli_email = ctk.CTkEntry(left_frame, placeholder_text="Correo electrónico (opcional)")
        self.cli_email.pack(pady=4, padx=10, fill="x")
        self.cli_dir = ctk.CTkEntry(left_frame, placeholder_text="Dirección de entrega (opcional)")
        self.cli_dir.pack(pady=4, padx=10, fill="x")
        
        cli_btn_box = ctk.CTkFrame(left_frame, fg_color="transparent")
        cli_btn_box.pack(pady=8, padx=10, fill="x")

        self.btn_save_cli = ctk.CTkButton(cli_btn_box, text="Guardar Cliente", fg_color="blue", command=self.add_cliente)
        self.btn_save_cli.pack(side="left", fill="x", expand=True, padx=2)

        self.btn_cancel_cli = ctk.CTkButton(cli_btn_box, text="X", width=30, fg_color="gray40", command=self.cancel_edit_cliente)

        ctk.CTkLabel(left_frame, text="Listado de Clientes:", font=("Arial", 12, "bold")).pack(pady=(10, 5))
        self.scroll_clientes = ctk.CTkScrollableFrame(left_frame, width=290, height=200)
        self.scroll_clientes.pack(pady=5, padx=5, fill="both", expand=True)
        self.actualizar_vista_clientes()

        # --- BLOQUE DERECHO: NUEVO PEDIDO ---
        right_frame = ctk.CTkFrame(main_ped_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        self.lbl_ped_title = ctk.CTkLabel(right_frame, text="Registrar Nuevo Pedido", font=("Arial", 14, "bold"))
        self.lbl_ped_title.pack(pady=5)
        
        form_ped = ctk.CTkFrame(right_frame, fg_color="transparent")
        form_ped.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(form_ped, text="Buscar Cliente:").grid(row=0, column=0, sticky="w", pady=3)
        self.ped_cli_search = ctk.CTkEntry(form_ped, placeholder_text="Escribe nombre de cliente...")
        self.ped_cli_search.grid(row=0, column=1, sticky="ew", pady=3, padx=5)
        self.ped_cli_search.bind("<KeyRelease>", self.filtrar_clientes_para_pedido)

        ctk.CTkLabel(form_ped, text="Cliente seleccionado:").grid(row=1, column=0, sticky="w", pady=3)
        clientes_list = list(self.data["clientes"].keys())
        self.ped_cli_var = ctk.StringVar(value=clientes_list[0] if clientes_list else "Sin clientes")
        self.menu_ped_cli = ctk.CTkOptionMenu(form_ped, variable=self.ped_cli_var, values=clientes_list or ["Sin clientes"])
        self.menu_ped_cli.grid(row=1, column=1, sticky="ew", pady=3, padx=5)

        ctk.CTkLabel(form_ped, text="Tienda de Venta:").grid(row=2, column=0, sticky="w", pady=3)
        self.ped_tienda_var = ctk.StringVar(value="Wallapop")
        self.menu_ped_tienda = ctk.CTkOptionMenu(form_ped, variable=self.ped_tienda_var, values=["Wallapop", "Etsy", "Otra / Directo"])
        self.menu_ped_tienda.grid(row=2, column=1, sticky="ew", pady=3, padx=5)

        ctk.CTkLabel(form_ped, text="Impresión/Proyecto asociada:").grid(row=3, column=0, sticky="w", pady=3)
        hist_list = [f"[{h.get('fecha','')}] {h.get('nombre','Pieza')} ({h.get('coste_total',0):.2f}€)" for h in self.data["historial"]]
        self.ped_hist_var = ctk.StringVar(value=hist_list[0] if hist_list else "No hay historial")
        self.menu_ped_hist = ctk.CTkOptionMenu(form_ped, variable=self.ped_hist_var, values=hist_list or ["No hay historial"])
        self.menu_ped_hist.grid(row=3, column=1, sticky="ew", pady=3, padx=5)

        ctk.CTkLabel(form_ped, text="Nº de Seguimiento (opcional):").grid(row=4, column=0, sticky="w", pady=3)
        self.ped_seguimiento = ctk.CTkEntry(form_ped, placeholder_text="ej. PK123456789ES")
        self.ped_seguimiento.grid(row=4, column=1, sticky="ew", pady=3, padx=5)
        
        ctk.CTkLabel(form_ped, text="Precio venta producto (€):").grid(row=5, column=0, sticky="w", pady=3)
        self.ped_precio_prod = ctk.CTkEntry(form_ped, placeholder_text="0.00")
        self.ped_precio_prod.grid(row=5, column=1, sticky="ew", pady=3, padx=5)
        self.ped_precio_prod.bind("<KeyRelease>", lambda e: self.calcular_total_pedido())

        ctk.CTkLabel(form_ped, text="Gastos de Envío (€):").grid(row=6, column=0, sticky="w", pady=3)
        self.ped_envio = ctk.CTkEntry(form_ped, placeholder_text="0.00")
        self.ped_envio.insert(0, "0.00")
        self.ped_envio.grid(row=6, column=1, sticky="ew", pady=3, padx=5)
        self.ped_envio.bind("<KeyRelease>", lambda e: self.calcular_total_pedido())

        ctk.CTkLabel(form_ped, text="Total a Cobrar (€):", font=("Arial", 12, "bold")).grid(row=7, column=0, sticky="w", pady=5)
        self.lbl_ped_total = ctk.CTkLabel(form_ped, text="0.00 €", font=("Arial", 14, "bold"), text_color="lightgreen")
        self.lbl_ped_total.grid(row=7, column=1, sticky="w", pady=5, padx=5)

        form_ped.grid_columnconfigure(1, weight=1)
        
        ped_btn_box = ctk.CTkFrame(right_frame, fg_color="transparent")
        ped_btn_box.pack(pady=5)

        self.btn_save_ped = ctk.CTkButton(ped_btn_box, text="Crear Pedido", fg_color="green", command=self.add_pedido)
        self.btn_save_ped.pack(side="left", padx=5)

        self.btn_cancel_ped = ctk.CTkButton(ped_btn_box, text="Cancelar Edición", fg_color="gray40", command=self.cancel_edit_pedido)

        ctk.CTkLabel(right_frame, text="Historial de Pedidos:", font=("Arial", 12, "bold")).pack(pady=(10, 2))
        self.scroll_pedidos = ctk.CTkScrollableFrame(right_frame, width=540, height=140)
        self.scroll_pedidos.pack(pady=5, padx=5, fill="both", expand=True)
        self.actualizar_vista_pedidos()

    def edit_cliente(self, nombre):
        info = self.data["clientes"][nombre]
        self.editing_cliente_name = nombre
        
        self.cli_nombre.delete(0, 'end')
        self.cli_nombre.insert(0, nombre)
        
        self.cli_tel.delete(0, 'end')
        self.cli_tel.insert(0, info.get("telefono", ""))
        
        self.cli_email.delete(0, 'end')
        self.cli_email.insert(0, info.get("email", ""))
        
        self.cli_dir.delete(0, 'end')
        self.cli_dir.insert(0, info.get("direccion", ""))

        self.lbl_cli_title.configure(text="Editar Cliente", text_color="orange")
        self.btn_save_cli.configure(text="Guardar Cambios", fg_color="orange")
        self.btn_cancel_cli.pack(side="right", padx=2)

    def cancel_edit_cliente(self):
        self.editing_cliente_name = None
        self.cli_nombre.delete(0, 'end')
        self.cli_tel.delete(0, 'end')
        self.cli_email.delete(0, 'end')
        self.cli_dir.delete(0, 'end')
        self.lbl_cli_title.configure(text="Nuevo Cliente", text_color="white")
        self.btn_save_cli.configure(text="Guardar Cliente", fg_color="blue")
        self.btn_cancel_cli.pack_forget()

    def add_cliente(self):
        nombre = self.cli_nombre.get().strip()
        tel = self.cli_tel.get().strip()
        email = self.cli_email.get().strip()
        direccion = self.cli_dir.get().strip()
        if not nombre: return

        if self.editing_cliente_name:
            old_name = self.editing_cliente_name
            if old_name != nombre:
                del self.data["clientes"][old_name]
                # Actualización en cascada en Pedidos
                for p in self.data["pedidos"]:
                    if p.get("cliente") == old_name:
                        p["cliente"] = nombre
            self.data["clientes"][nombre] = {"telefono": tel, "email": email, "direccion": direccion}
            self.cancel_edit_cliente()
        else:
            self.data["clientes"][nombre] = {"telefono": tel, "email": email, "direccion": direccion}
            self.cancel_edit_cliente()

        self.save_data()
        self.actualizar_vista_clientes()
        self.actualizar_selectores_pedidos()
        self.actualizar_vista_pedidos()

    def edit_pedido(self, real_index):
        p = self.data["pedidos"][real_index]
        self.editing_pedido_index = real_index
        
        self.ped_cli_var.set(p.get('cliente', ''))
        self.ped_tienda_var.set(p.get('tienda', 'Wallapop'))
        self.ped_hist_var.set(p.get('impresion', ''))
        
        self.ped_seguimiento.delete(0, 'end')
        self.ped_seguimiento.insert(0, p.get('seguimiento', ''))
        
        self.ped_precio_prod.delete(0, 'end')
        self.ped_precio_prod.insert(0, str(p.get('precio_prod', 0.0)))
        
        self.ped_envio.delete(0, 'end')
        self.ped_envio.insert(0, str(p.get('envio', 0.0)))
        
        self.calcular_total_pedido()

        self.lbl_ped_title.configure(text="Editar Pedido", text_color="orange")
        self.btn_save_ped.configure(text="Guardar Cambios en Pedido", fg_color="orange")
        self.btn_cancel_ped.pack(side="right", padx=5)

    def cancel_edit_pedido(self):
        self.editing_pedido_index = None
        self.ped_seguimiento.delete(0, 'end')
        self.ped_precio_prod.delete(0, 'end')
        self.ped_envio.delete(0, 'end')
        self.ped_envio.insert(0, "0.00")
        self.lbl_ped_total.configure(text="0.00 €")
        self.lbl_ped_title.configure(text="Registrar Nuevo Pedido", text_color="white")
        self.btn_save_ped.configure(text="Crear Pedido", fg_color="green")
        self.btn_cancel_ped.pack_forget()

    def add_pedido(self):
        try:
            cliente = self.ped_cli_var.get()
            tienda = self.ped_tienda_var.get()
            impresion_str = self.ped_hist_var.get()
            seguimiento = self.ped_seguimiento.get().strip()
            precio_prod = float(self.ped_precio_prod.get().strip().replace(',', '.') or 0.0)
            envio = float(self.ped_envio.get().strip().replace(',', '.') or 0.0)
            total = precio_prod + envio
            
            if not cliente or cliente in ["Sin clientes", "Sin coincidencias"] or not impresion_str or impresion_str == "No hay historial":
                return

            ped_data = {
                "fecha": self.data["pedidos"][self.editing_pedido_index]["fecha"] if self.editing_pedido_index is not None else datetime.now().strftime("%Y-%m-%d %H:%M"),
                "cliente": cliente,
                "tienda": tienda,
                "impresion": impresion_str,
                "seguimiento": seguimiento,
                "precio_prod": precio_prod,
                "envio": envio,
                "total": total
            }

            if self.editing_pedido_index is not None:
                self.data["pedidos"][self.editing_pedido_index] = ped_data
                self.cancel_edit_pedido()
            else:
                self.data["pedidos"].append(ped_data)
                self.cancel_edit_pedido()

            self.save_data()
            self.actualizar_vista_pedidos()
            self.actualizar_vista_estadisticas()
        except ValueError:
            pass

    def filtrar_clientes_para_pedido(self, event=None):
        filtro = self.ped_cli_search.get().strip().lower()
        todos_clientes = list(self.data["clientes"].keys())
        coincidencias = [c for c in todos_clientes if filtro in c.lower()] if filtro else todos_clientes
        if coincidencias:
            self.menu_ped_cli.configure(values=coincidencias)
            self.ped_cli_var.set(coincidencias[0])
        else:
            self.menu_ped_cli.configure(values=["Sin coincidencias"])
            self.ped_cli_var.set("Sin coincidencias")

    def eliminar_cliente(self, nombre):
        if nombre in self.data["clientes"]:
            del self.data["clientes"][nombre]
            self.save_data()
            self.actualizar_vista_clientes()
            self.actualizar_selectores_pedidos()

    def actualizar_vista_clientes(self):
        for widget in self.scroll_clientes.winfo_children(): widget.destroy()
        for cli, info in self.data["clientes"].items():
            card = ctk.CTkFrame(self.scroll_clientes)
            card.pack(pady=3, padx=2, fill="x", expand=True)
            detalles = f"Tel: {info.get('telefono','-')} | Dir: {info.get('direccion','-')}"
            ctk.CTkLabel(card, text=f"{cli}\n{detalles}", anchor="w", font=("Arial", 10)).pack(side="left", padx=5, pady=5, fill="x", expand=True)
            ctk.CTkButton(card, text="✎", width=30, fg_color="orange", command=lambda c=cli: self.edit_cliente(c)).pack(side="right", padx=2)
            ctk.CTkButton(card, text="X", width=30, fg_color="red", command=lambda c=cli: self.eliminar_cliente(c)).pack(side="right", padx=2)

    def calcular_total_pedido(self):
        try:
            prod = float(self.ped_precio_prod.get().strip().replace(',', '.') or 0.0)
            envio = float(self.ped_envio.get().strip().replace(',', '.') or 0.0)
            self.lbl_ped_total.configure(text=f"{prod + envio:.2f} €")
        except ValueError:
            self.lbl_ped_total.configure(text="Error en números")

    def eliminar_pedido(self, index):
        del self.data["pedidos"][index]
        self.save_data()
        self.actualizar_vista_pedidos()
        self.actualizar_vista_estadisticas()

    def actualizar_vista_pedidos(self):
        for widget in self.scroll_pedidos.winfo_children(): widget.destroy()
        for index, p in enumerate(reversed(self.data["pedidos"])):
            real_index = len(self.data["pedidos"]) - 1 - index
            card = ctk.CTkFrame(self.scroll_pedidos)
            card.pack(pady=4, padx=5, fill="x", expand=True)
            tienda = p.get('tienda', 'Wallapop')
            track_str = f" | Track: {p.get('seguimiento')}" if p.get('seguimiento') else ""
            info = f"{p['fecha']} | [{tienda}] Cliente: {p['cliente']}{track_str} | Total: {p['total']:.2f}€ (Venta: {p['precio_prod']:.2f}€ + Envío: {p['envio']:.2f}€)\nRef: {p['impresion']}"
            ctk.CTkLabel(card, text=info, anchor="w", font=("Arial", 11)).pack(side="left", padx=10, pady=5, fill="x", expand=True)
            ctk.CTkButton(card, text="✎", width=35, fg_color="orange", command=lambda idx=real_index: self.edit_pedido(idx)).pack(side="right", padx=2)
            ctk.CTkButton(card, text="Borrar", width=55, fg_color="red", command=lambda idx=real_index: self.eliminar_pedido(idx)).pack(side="right", padx=2)

    def actualizar_selectores_pedidos(self):
        clientes_list = list(self.data["clientes"].keys())
        self.menu_ped_cli.configure(values=clientes_list or ["Sin clientes"])
        if clientes_list and self.ped_cli_var.get() not in clientes_list: self.ped_cli_var.set(clientes_list[0])

        hist_list = [f"[{h.get('fecha','')}] {h.get('nombre','Pieza')} ({h.get('coste_total',0):.2f}€)" for h in self.data["historial"]]
        self.menu_ped_hist.configure(values=hist_list or ["No hay historial"])
        if hist_list and self.ped_hist_var.get() not in hist_list: self.ped_hist_var.set(hist_list[0])

    # --- PESTAÑA: ESTADÍSTICAS ---
    def build_estadisticas(self):
        ctk.CTkLabel(self.tab_stats, text="Balance Económico y Estadísticas", font=("Arial", 20, "bold")).pack(pady=15)
        self.stats_frame = ctk.CTkFrame(self.tab_stats, fg_color="transparent")
        self.stats_frame.pack(fill="both", expand=True, padx=20, pady=10)
        ctk.CTkButton(self.tab_stats, text="Actualizar Datos", fg_color="blue", command=self.actualizar_vista_estadisticas).pack(pady=10)
        self.actualizar_vista_estadisticas()

    def actualizar_vista_estadisticas(self):
        for widget in self.stats_frame.winfo_children(): widget.destroy()
        
        ingresos_productos = 0.0
        costes_produccion = 0.0
        total_envios = 0.0
        demanda_filamentos = {}
        
        historial_map = {}
        for h in self.data["historial"]:
            key = f"[{h.get('fecha','')}] {h.get('nombre','Pieza')} ({h.get('coste_total',0):.2f}€)"
            historial_map[key] = h
            
        for p in self.data["pedidos"]:
            ingresos_productos += p.get('precio_prod', 0.0)
            total_envios += p.get('envio', 0.0)
            
            ref_impresion = p.get('impresion', '')
            if ref_impresion in historial_map:
                h_data = historial_map[ref_impresion]
                costes_produccion += h_data.get('coste_total', 0.0)
                
                desglose = h_data.get('desglose_filamentos', [])
                if desglose:
                    for item in desglose:
                        fil = item["filamento"]
                        g = item["gramos"]
                        if fil not in demanda_filamentos:
                            demanda_filamentos[fil] = {"usos": 0, "gramos": 0.0}
                        demanda_filamentos[fil]["usos"] += 1
                        demanda_filamentos[fil]["gramos"] += g
                else:
                    fil_usado = h_data.get('filamento', 'Desconocido')
                    gramos_usados = h_data.get('gramos', 0.0)
                    if fil_usado not in demanda_filamentos:
                        demanda_filamentos[fil_usado] = {"usos": 0, "gramos": 0.0}
                    demanda_filamentos[fil_usado]["usos"] += 1
                    demanda_filamentos[fil_usado]["gramos"] += gramos_usados

        beneficio_neto = ingresos_productos - costes_produccion
        margen_porcentaje = (beneficio_neto / ingresos_productos * 100) if ingresos_productos > 0 else 0.0

        filamento_top = "Ninguno registrado"
        if demanda_filamentos:
            top_key = max(demanda_filamentos, key=lambda k: demanda_filamentos[k]["gramos"])
            filamento_top = f"{top_key}\n({demanda_filamentos[top_key]['gramos']:.1f}g consumidos)"

        card_config = [
            ("Ingresos Totales (Venta Productos)", f"{ingresos_productos:.2f} €", "lightblue"),
            ("Costes Totales de Producción", f"{costes_produccion:.2f} €", "salmon"),
            ("Beneficio Neto del Negocio", f"{beneficio_neto:.2f} €", "lightgreen" if beneficio_neto >= 0 else "red"),
            ("Margen de Beneficio General", f"{margen_porcentaje:.1f} %", "orange" if margen_porcentaje < 30 else "gold"),
            ("Filamento Más Demandado", filamento_top, "cyan"),
            ("Pedidos Totales Realizados", f"{len(self.data['pedidos'])} pedidos", "purple")
        ]

        for i, (titulo, valor, color) in enumerate(card_config):
            row = i // 2
            col = i % 2
            card = ctk.CTkFrame(self.stats_frame, corner_radius=10)
            card.grid(row=row, column=col, padx=15, pady=12, sticky="nsew", ipadx=10, ipady=10)
            ctk.CTkLabel(card, text=titulo, font=("Arial", 14, "bold")).pack(pady=(10, 5))
            ctk.CTkLabel(card, text=valor, font=("Arial", 18, "bold"), text_color=color).pack(pady=(5, 10))

        self.stats_frame.grid_columnconfigure(0, weight=1)
        self.stats_frame.grid_columnconfigure(1, weight=1)

    # --- PESTAÑA: CONFIGURACIÓN ---
    def build_configuracion(self):
        for w in self.tab_conf.winfo_children(): w.destroy()
        cfg = self.data["config"]
        
        ctk.CTkLabel(self.tab_conf, text="Ajustes de Costes y Consumo", font=("Arial", 20, "bold")).pack(pady=10)
        scroll_conf = ctk.CTkScrollableFrame(self.tab_conf, width=500, height=550)
        scroll_conf.pack(pady=5, padx=10, fill="both", expand=True)

        ctk.CTkLabel(scroll_conf, text="Precio de la electricidad (€ por kWh):").pack(pady=(10, 0))
        self.cfg_kwh = ctk.CTkEntry(scroll_conf, width=300)
        self.cfg_kwh.insert(0, str(cfg["precio_kwh"]))
        self.cfg_kwh.pack(pady=(0, 10))
        
        ctk.CTkLabel(scroll_conf, text="Consumo medio sostenido (Vatios/W):").pack(pady=(10, 0))
        self.cfg_watts = ctk.CTkEntry(scroll_conf, width=300)
        self.cfg_watts.insert(0, str(cfg["consumo_watts"]))
        self.cfg_watts.pack(pady=(0, 10))

        ctk.CTkLabel(scroll_conf, text="Consumo PICO en precalentamiento (Vatios/W):").pack(pady=(10, 0))
        self.cfg_pico_watts = ctk.CTkEntry(scroll_conf, width=300)
        self.cfg_pico_watts.insert(0, str(cfg.get("consumo_pico_watts", 350)))
        self.cfg_pico_watts.pack(pady=(0, 10))

        ctk.CTkLabel(scroll_conf, text="Tiempo de precalentamiento / arranque por placa (Minutos):").pack(pady=(10, 0))
        self.cfg_mins_prep = ctk.CTkEntry(scroll_conf, width=300)
        self.cfg_mins_prep.insert(0, str(cfg.get("mins_preparacion", 6)))
        self.cfg_mins_prep.pack(pady=(0, 10))
        
        ctk.CTkLabel(scroll_conf, text="Precio de compra de la impresora (€):").pack(pady=(10, 0))
        self.cfg_imp = ctk.CTkEntry(scroll_conf, width=300)
        self.cfg_imp.insert(0, str(cfg["precio_impresora"]))
        self.cfg_imp.pack(pady=(0, 10))

        ctk.CTkLabel(scroll_conf, text="Vida útil estimada (Horas) - para amortización:").pack(pady=(10, 0))
        self.cfg_vida = ctk.CTkEntry(scroll_conf, width=300)
        self.cfg_vida.insert(0, str(cfg.get("horas_vida", 5000)))
        self.cfg_vida.pack(pady=(0, 10))

        ctk.CTkButton(scroll_conf, text="Guardar Configuración", fg_color="blue", command=self.save_config).pack(pady=20)
        self.lbl_cfg_ok = ctk.CTkLabel(scroll_conf, text="", text_color="green")
        self.lbl_cfg_ok.pack()

    # --- LÓGICA DE DATOS Y VISTAS ---
    def get_filamentos_list(self):
        return [f"{k} - {v['color']} ({v['restante']}g)" for k, v in self.data["filamentos"].items()]

    def update_all_filamentos_menus(self):
        nueva_lista = self.get_filamentos_list() or ["No hay filamentos"]
        for pd in self.placas_widgets:
            for r in pd["filamentos_rows"]:
                r["menu"].configure(values=nueva_lista)

    def eliminar_filamento(self, id_fil):
        if id_fil in self.data["filamentos"]:
            del self.data["filamentos"][id_fil]
            self.save_data()
            self.actualizar_vista_stock()
            self.update_all_filamentos_menus()

    def actualizar_vista_stock(self):
        for widget in self.scroll_stock.winfo_children(): widget.destroy()
        filtro = self.fil_search.get().lower() if hasattr(self, 'fil_search') else ""
        for k, v in self.data["filamentos"].items():
            acabado = v.get("acabado", "Mate")
            if filtro and filtro not in f"{v['marca']} {v['tipo']} {v['color']} {acabado}".lower(): continue
            card = ctk.CTkFrame(self.scroll_stock)
            card.pack(pady=4, padx=5, fill="x", expand=True)
            info_text = f"[{v['tipo']}] {v['marca']} | Color: {v['color']} ({acabado}) | Quedan: {v['restante']:.1f}g / {v['peso_inicial']}g | Precio: {v['precio']}€"
            ctk.CTkLabel(card, text=info_text, anchor="w", font=("Arial", 12)).pack(side="left", padx=10, pady=8, fill="x", expand=True)
            
            # Ajuste rápido de peso directamente desde la tarjeta
            adj_frame = ctk.CTkFrame(card, fg_color="transparent")
            adj_frame.pack(side="right", padx=5)
            
            entry_adj = ctk.CTkEntry(adj_frame, placeholder_text="Ajustar (g)", width=80)
            entry_adj.pack(side="left", padx=2)
            
            btn_adj = ctk.CTkButton(adj_frame, text="Ajustar", width=55, fg_color="gray30", hover_color="gray40", 
                                    command=lambda id_f=k, e=entry_adj: self.ajustar_gramos_rapido(id_f, e))
            btn_adj.pack(side="left", padx=2)

            ctk.CTkButton(card, text="✎", width=35, fg_color="orange", command=lambda id_f=k: self.edit_filamento(id_f)).pack(side="right", padx=2, pady=5)
            ctk.CTkButton(card, text="Borrar", width=60, fg_color="red", hover_color="darkred", command=lambda id_f=k: self.eliminar_filamento(id_f)).pack(side="right", padx=2, pady=5)

    def actualizar_vista_historial(self):
        for widget in self.scroll_hist.winfo_children(): widget.destroy()
        for index, h in enumerate(reversed(self.data["historial"])):
            real_index = len(self.data["historial"]) - 1 - index
            card = ctk.CTkFrame(self.scroll_hist)
            card.pack(pady=4, padx=5, fill="x", expand=True)
            
            nombre_articulo = f"[{h.get('nombre', 'Sin nombre')}] " if h.get('nombre') else ""
            placas_cnt = h.get('num_placas', 1)
            
            desglose = h.get('desglose_filamentos', [])
            if desglose:
                fil_summary = ", ".join([f"{item['filamento']} ({item['gramos']}g)" for item in desglose])
            else:
                fil_summary = f"{h.get('filamento','')} ({h.get('gramos',0)}g)"

            info_text = f"{h['fecha']} | {nombre_articulo} | {placas_cnt} Placa(s) | {h.get('tiempo_total','-')} | Coste: {h['coste_total']:.2f}€\nMateriales: {fil_summary}"
            ctk.CTkLabel(card, text=info_text, anchor="w", font=("Arial", 11)).pack(side="left", padx=10, pady=8, fill="x", expand=True)
            ctk.CTkButton(card, text="Borrar y devolver stock", width=150, fg_color="darkred", hover_color="firebrick", command=lambda idx=real_index: self.eliminar_historial(idx)).pack(side="right", padx=10, pady=5)

    def eliminar_historial(self, index):
        h = self.data["historial"][index]
        desglose = h.get('desglose_filamentos', [])
        if desglose:
            for item in desglose:
                fil_name = item["filamento"]
                gramos = item["gramos"]
                if fil_name in self.data["filamentos"]:
                    self.data["filamentos"][fil_name]["restante"] += gramos
                    if self.data["filamentos"][fil_name]["restante"] > self.data["filamentos"][fil_name]["peso_inicial"]:
                        self.data["filamentos"][fil_name]["restante"] = self.data["filamentos"][fil_name]["peso_inicial"]
        else:
            fil_name = h.get("filamento")
            gramos_gastados = h.get("gramos", 0)
            if fil_name in self.data["filamentos"]:
                self.data["filamentos"][fil_name]["restante"] += gramos_gastados

        del self.data["historial"][index]
        self.save_data()
        self.actualizar_vista_stock()
        self.actualizar_vista_historial()
        self.actualizar_selectores_pedidos()
        self.actualizar_vista_estadisticas()
        self.update_all_filamentos_menus()

    def save_config(self):
        try:
            self.data["config"]["precio_kwh"] = float(self.cfg_kwh.get().strip().replace(',', '.'))
            self.data["config"]["consumo_watts"] = float(self.cfg_watts.get().strip().replace(',', '.'))
            self.data["config"]["consumo_pico_watts"] = float(self.cfg_pico_watts.get().strip().replace(',', '.'))
            self.data["config"]["mins_preparacion"] = float(self.cfg_mins_prep.get().strip().replace(',', '.'))
            self.data["config"]["precio_impresora"] = float(self.cfg_imp.get().strip().replace(',', '.'))
            self.data["config"]["horas_vida"] = float(self.cfg_vida.get().strip().replace(',', '.'))
            self.save_data()
            self.lbl_cfg_ok.configure(text="¡Configuración guardada correctamente!", text_color="green")
            self.after(3000, lambda: self.lbl_cfg_ok.configure(text=""))
        except ValueError:
            self.lbl_cfg_ok.configure(text="Error: Revisa que los valores sean numéricos", text_color="red")

    # --- LÓGICA DEL CÁLCULO PROYECTO ---
    def calcular_coste_proyecto(self):
        try:
            cfg = self.data["config"]
            coste_total_proyecto = 0.0
            horas_totales_proyecto = 0.0
            desglose_filamentos_acumulado = {}

            if not self.placas_widgets:
                self.lbl_resultado.configure(text="Añade al menos una placa")
                return False

            mins_prep = cfg.get("mins_preparacion", 6)
            horas_prep = mins_prep / 60.0
            pico_watts = cfg.get("consumo_pico_watts", 350)

            for p_idx, placa in enumerate(self.placas_widgets):
                h_str = placa["horas"].get().strip().replace(',', '.')
                m_str = placa["mins"].get().strip().replace(',', '.')
                h = float(h_str or 0)
                m = float(m_str or 0)
                horas_impresion_placa = h + (m / 60)
                
                horas_placa = horas_impresion_placa + horas_prep
                horas_totales_proyecto += horas_placa

                coste_luz_pico = (pico_watts / 1000) * horas_prep * cfg["precio_kwh"]
                coste_luz_mantenimiento = (cfg["consumo_watts"] / 1000) * horas_impresion_placa * cfg["precio_kwh"]
                coste_luz = coste_luz_pico + coste_luz_mantenimiento

                coste_desgaste = (cfg["precio_impresora"] / cfg["horas_vida"]) * horas_placa
                coste_placa = coste_luz + coste_desgaste

                for f_row in placa["filamentos_rows"]:
                    fil_str = f_row["var"].get().split(" - ")[0]
                    if fil_str not in self.data["filamentos"]:
                        self.lbl_resultado.configure(text=f"Filamento no válido en Placa #{p_idx+1}")
                        return False
                    
                    g_str = f_row["gramos"].get().strip().replace(',', '.')
                    gramos = float(g_str or 0)
                    fil = self.data["filamentos"][fil_str]
                    coste_mat = (gramos / fil["peso_inicial"]) * fil["precio"]
                    coste_placa += coste_mat

                    if fil_str not in desglose_filamentos_acumulado:
                        desglose_filamentos_acumulado[fil_str] = 0.0
                    desglose_filamentos_acumulado[fil_str] += gramos

                coste_total_proyecto += coste_placa

            self.coste_proyecto_actual = coste_total_proyecto
            self.horas_totales_proyecto = horas_totales_proyecto
            self.desglose_filamentos_calculado = [
                {"filamento": k, "gramos": v} for k, v in desglose_filamentos_acumulado.items()
            ]

            mins_totales = int(round((horas_totales_proyecto % 1) * 60))
            self.lbl_resultado.configure(
                text=f"Coste Total Proyecto: {coste_total_proyecto:.2f} €\n"
                     f"({len(self.placas_widgets)} Placas | Tiempo Total incl. arranques: {int(horas_totales_proyecto)}h {mins_totales}m)"
            )
            return True

        except ValueError:
            self.lbl_resultado.configure(text="Error: Revisa que tiempos y gramos sean numéricos")
            return False

    def guardar_impresion(self):
        if self.calcular_coste_proyecto():
            nombre_articulo = self.calc_nombre.get().strip() or "Proyecto sin nombre"
            
            for item in self.desglose_filamentos_calculado:
                f_id = item["filamento"]
                g_usados = item["gramos"]
                if f_id in self.data["filamentos"]:
                    self.data["filamentos"][f_id]["restante"] -= g_usados
                    if self.data["filamentos"][f_id]["restante"] < 0:
                        self.data["filamentos"][f_id]["restante"] = 0

            mins_totales = int(round((self.horas_totales_proyecto % 1) * 60))
            
            self.data["historial"].append({
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "nombre": nombre_articulo,
                "num_placas": len(self.placas_widgets),
                "tiempo_total": f"{int(self.horas_totales_proyecto)}h {mins_totales}m",
                "coste_total": self.coste_proyecto_actual,
                "desglose_filamentos": self.desglose_filamentos_calculado
            })
            
            self.save_data()
            self.actualizar_vista_stock()
            self.actualizar_vista_historial()
            self.actualizar_selectores_pedidos()
            self.actualizar_vista_estadisticas()
            self.update_all_filamentos_menus()
            
            self.build_calculadora()
            self.lbl_resultado.configure(text="¡Proyecto guardado en el historial y stock descontado!")

if __name__ == "__main__":
    app = App3D()
    app.mainloop()