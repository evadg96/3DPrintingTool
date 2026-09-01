import customtkinter as ctk
import json
import os
from datetime import datetime

# Crear carpeta en Documentos para evitar el bloqueo de macOS
USER_DIR = os.path.expanduser("~/Documents/Gestor3D")
os.makedirs(USER_DIR, exist_ok=True)
DATA_FILE = os.path.join(USER_DIR, "impresiones_data.json")

# Datos por defecto ampliados
DEFAULT_DATA = {
    "filamentos": {},
    "historial": [],
    "clientes": {},
    "pedidos": [],
    "config": {
        "precio_kwh": 0.15,
        "consumo_watts": 65,
        "precio_impresora": 400,
        "horas_vida": 5000,
        "margen_beneficio": 0
    }
}

class App3D(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gestor de Impresión 3D Pro")
        self.geometry("1000x780")
        ctk.set_appearance_mode("dark")
        
        self.data = self.load_data()
        
        # Sistema de Pestañas (Añadida pestaña "Estadísticas")
        self.tabview = ctk.CTkTabview(self, width=950, height=710)
        self.tabview.pack(padx=20, pady=20)
        
        self.tab_calc = self.tabview.add("Calculadora")
        self.tab_fil = self.tabview.add("Filamentos")
        self.tab_hist = self.tabview.add("Historial")
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
                    return data
            except Exception:
                return DEFAULT_DATA
        return DEFAULT_DATA

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f, indent=4)

    # --- PESTAÑA: CALCULADORA ---
    def build_calculadora(self):
        ctk.CTkLabel(self.tab_calc, text="Nueva Impresión / Simulador", font=("Arial", 20, "bold")).pack(pady=10)
        
        self.calc_nombre = ctk.CTkEntry(self.tab_calc, placeholder_text="Nombre del artículo o proyecto (opcional)", width=400)
        self.calc_nombre.pack(pady=5)
        
        ctk.CTkLabel(self.tab_calc, text="Selecciona el filamento a utilizar:").pack(pady=(5, 0))
        lista_inicial = self.get_filamentos_list()
        val_inicial = lista_inicial[0] if lista_inicial else "No hay filamentos"
        
        self.calc_fil_var = ctk.StringVar(value=val_inicial)
        self.menu_filamentos = ctk.CTkOptionMenu(self.tab_calc, variable=self.calc_fil_var, values=lista_inicial or ["No hay filamentos"], width=400)
        self.menu_filamentos.pack(pady=5)
        
        row1 = ctk.CTkFrame(self.tab_calc, fg_color="transparent")
        row1.pack(pady=10)
        self.calc_horas = ctk.CTkEntry(row1, placeholder_text="Horas")
        self.calc_horas.pack(side="left", padx=5)
        self.calc_mins = ctk.CTkEntry(row1, placeholder_text="Minutos")
        self.calc_mins.pack(side="left", padx=5)
        
        self.calc_gramos = ctk.CTkEntry(self.tab_calc, placeholder_text="Peso (gramos)")
        self.calc_gramos.pack(pady=10)
        
        self.lbl_resultado = ctk.CTkLabel(self.tab_calc, text="Coste Total: 0.00 €", font=("Arial", 16, "bold"))
        self.lbl_resultado.pack(pady=15)
        
        btn_frame = ctk.CTkFrame(self.tab_calc, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(btn_frame, text="Calcular Coste", fg_color="blue", command=self.calcular_coste).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Guardar en el Historial (Descontar Stock)", fg_color="green", command=self.guardar_impresion).pack(side="left", padx=10)

    # --- PESTAÑA: FILAMENTOS ---
    def build_filamentos(self):
        ctk.CTkLabel(self.tab_fil, text="Gestión de Stock y Rollos", font=("Arial", 18, "bold")).pack(pady=5)
        
        form_frame = ctk.CTkFrame(self.tab_fil)
        form_frame.pack(pady=5, padx=10, fill="x")
        
        self.fil_marca = ctk.CTkEntry(form_frame, placeholder_text="Marca (ej. Sunlu, Bambu)")
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
        
        self.fil_peso = ctk.CTkEntry(form_frame, placeholder_text="Peso total (g, ej. 1000)")
        self.fil_peso.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        self.fil_precio = ctk.CTkEntry(form_frame, placeholder_text="Precio (€, ej. 19.99)")
        self.fil_precio.grid(row=2, column=2, padx=5, pady=5, sticky="ew")
        
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(2, weight=1)

        ctk.CTkButton(form_frame, text="Añadir Nuevo Rollo", fg_color="green", command=self.add_filamento).grid(row=3, column=0, columnspan=3, pady=8, sticky="ew")
        
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

    # --- PESTAÑA: HISTORIAL ---
    def build_historial(self):
        ctk.CTkLabel(self.tab_hist, text="Historial de Impresiones", font=("Arial", 18, "bold")).pack(pady=5)
        
        self.scroll_hist = ctk.CTkScrollableFrame(self.tab_hist, width=910, height=520)
        self.scroll_hist.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.actualizar_vista_historial()

    # --- PESTAÑA: PEDIDOS / CLIENTES ---
    def build_pedidos(self):
        ctk.CTkLabel(self.tab_pedidos, text="Gestión de Clientes y Pedidos", font=("Arial", 18, "bold")).pack(pady=5)
        
        main_ped_frame = ctk.CTkFrame(self.tab_pedidos, fg_color="transparent")
        main_ped_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # --- BLOQUE IZQUIERDO: CLIENTES (CAMPOS OPCIONALES + DIRECCIÓN) ---
        left_frame = ctk.CTkFrame(main_ped_frame, width=320)
        left_frame.pack(side="left", fill="y", padx=5, pady=5)
        
        ctk.CTkLabel(left_frame, text="Nuevo Cliente", font=("Arial", 14, "bold")).pack(pady=5)
        self.cli_nombre = ctk.CTkEntry(left_frame, placeholder_text="Nombre del cliente *")
        self.cli_nombre.pack(pady=4, padx=10, fill="x")
        self.cli_tel = ctk.CTkEntry(left_frame, placeholder_text="Teléfono (opcional)")
        self.cli_tel.pack(pady=4, padx=10, fill="x")
        self.cli_email = ctk.CTkEntry(left_frame, placeholder_text="Correo electrónico (opcional)")
        self.cli_email.pack(pady=4, padx=10, fill="x")
        self.cli_dir = ctk.CTkEntry(left_frame, placeholder_text="Dirección de entrega (opcional)")
        self.cli_dir.pack(pady=4, padx=10, fill="x")
        
        ctk.CTkButton(left_frame, text="Guardar Cliente", fg_color="blue", command=self.add_cliente).pack(pady=8, padx=10)
        
        ctk.CTkLabel(left_frame, text="Listado de Clientes:", font=("Arial", 12, "bold")).pack(pady=(10, 5))
        self.scroll_clientes = ctk.CTkScrollableFrame(left_frame, width=280, height=200)
        self.scroll_clientes.pack(pady=5, padx=5, fill="both", expand=True)
        self.actualizar_vista_clientes()

        # --- BLOQUE DERECHO: NUEVO PEDIDO ---
        right_frame = ctk.CTkFrame(main_ped_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(right_frame, text="Registrar Nuevo Pedido", font=("Arial", 14, "bold")).pack(pady=5)
        
        form_ped = ctk.CTkFrame(right_frame, fg_color="transparent")
        form_ped.pack(fill="x", padx=10, pady=5)
        
        # Selector Cliente
        ctk.CTkLabel(form_ped, text="Cliente:").grid(row=0, column=0, sticky="w", pady=3)
        clientes_list = list(self.data["clientes"].keys())
        self.ped_cli_var = ctk.StringVar(value=clientes_list[0] if clientes_list else "Sin clientes")
        self.menu_ped_cli = ctk.CTkOptionMenu(form_ped, variable=self.ped_cli_var, values=clientes_list or ["Sin clientes"])
        self.menu_ped_cli.grid(row=0, column=1, sticky="ew", pady=3, padx=5)
        
        # Selector Historial / Impresión asociada
        ctk.CTkLabel(form_ped, text="Impresión asociada:").grid(row=1, column=0, sticky="w", pady=3)
        hist_list = [f"[{h.get('fecha','')}] {h.get('nombre','Pieza')} ({h.get('coste_total',0):.2f}€)" for h in self.data["historial"]]
        self.ped_hist_var = ctk.StringVar(value=hist_list[0] if hist_list else "No hay historial")
        self.menu_ped_hist = ctk.CTkOptionMenu(form_ped, variable=self.ped_hist_var, values=hist_list or ["No hay historial"])
        self.menu_ped_hist.grid(row=1, column=1, sticky="ew", pady=3, padx=5)
        
        # Precio del producto a mano
        ctk.CTkLabel(form_ped, text="Precio Producto (€):").grid(row=2, column=0, sticky="w", pady=3)
        self.ped_precio_prod = ctk.CTkEntry(form_ped, placeholder_text="0.00")
        self.ped_precio_prod.grid(row=2, column=1, sticky="ew", pady=3, padx=5)
        self.ped_precio_prod.bind("<KeyRelease>", lambda e: self.calcular_total_pedido())

        # Gastos de envío a mano
        ctk.CTkLabel(form_ped, text="Gastos de Envío (€):").grid(row=3, column=0, sticky="w", pady=3)
        self.ped_envio = ctk.CTkEntry(form_ped, placeholder_text="0.00")
        self.ped_envio.insert(0, "0.00")
        self.ped_envio.grid(row=3, column=1, sticky="ew", pady=3, padx=5)
        self.ped_envio.bind("<KeyRelease>", lambda e: self.calcular_total_pedido())

        # Total a cobrar (Automático)
        ctk.CTkLabel(form_ped, text="Total a Cobrar (€):", font=("Arial", 12, "bold")).grid(row=4, column=0, sticky="w", pady=5)
        self.lbl_ped_total = ctk.CTkLabel(form_ped, text="0.00 €", font=("Arial", 14, "bold"), text_color="lightgreen")
        self.lbl_ped_total.grid(row=4, column=1, sticky="w", pady=5, padx=5)

        form_ped.grid_columnconfigure(1, weight=1)
        
        ctk.CTkButton(right_frame, text="Crear Pedido", fg_color="green", command=self.add_pedido).pack(pady=5)
        
        ctk.CTkLabel(right_frame, text="Historial de Pedidos:", font=("Arial", 12, "bold")).pack(pady=(10, 2))
        self.scroll_pedidos = ctk.CTkScrollableFrame(right_frame, width=540, height=140)
        self.scroll_pedidos.pack(pady=5, padx=5, fill="both", expand=True)
        self.actualizar_vista_pedidos()

    def calcular_total_pedido(self):
        try:
            prod = float(self.ped_precio_prod.get() or 0.0)
            envio = float(self.ped_envio.get() or 0.0)
            total = prod + envio
            self.lbl_ped_total.configure(text=f"{total:.2f} €")
        except ValueError:
            self.lbl_ped_total.configure(text="Error en números")

    # --- PESTAÑA: ESTADÍSTICAS ---
    def build_estadisticas(self):
        ctk.CTkLabel(self.tab_stats, text="Balance Económico y Estadísticas", font=("Arial", 20, "bold")).pack(pady=15)
        
        self.stats_frame = ctk.CTkFrame(self.tab_stats, fg_color="transparent")
        self.stats_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Botón para actualizar estadísticas manualmente (también se actualiza al entrar)
        ctk.CTkButton(self.tab_stats, text="Actualizar Datos", fg_color="blue", command=self.actualizar_vista_estadisticas).pack(pady=10)
        
        self.actualizar_vista_estadisticas()

    def actualizar_vista_estadisticas(self):
        for widget in self.stats_frame.winfo_children(): widget.destroy()
        
        # Cálculos de negocio basados en pedidos e historial
        ingresos_productos = 0.0
        costes_produccion = 0.0
        total_envios = 0.0
        
        # Mapear historial por texto o índice para cruzar costes
        historial_map = {}
        for h in self.data["historial"]:
            key = f"[{h.get('fecha','')}] {h.get('nombre','Pieza')} ({h.get('coste_total',0):.2f}€)"
            historial_map[key] = h.get('coste_total', 0.0)
            
        for p in self.data["pedidos"]:
            ingresos_productos += p.get('precio_prod', 0.0)
            total_envios += p.get('envio', 0.0)
            
            # Buscar el coste de la impresión asociada
            ref_impresion = p.get('impresion', '')
            if ref_impresion in historial_map:
                costes_produccion += historial_map[ref_impresion]

        beneficio_neto = ingresos_productos - costes_produccion
        
        # Margen de beneficio general: (Beneficio / Ingresos) * 100
        margen_porcentaje = (beneficio_neto / ingresos_productos * 100) if ingresos_productos > 0 else 0.0

        # --- TARJETAS VISUALES DE ESTADÍSTICAS ---
        card_config = [
            ("Ingresos Totales (Solo Productos)", f"{ingresos_productos:.2f} €", "lightblue"),
            ("Costes Totales de Producción", f"{costes_produccion:.2f} €", "salmon"),
            ("Beneficio Neto del Negocio", f"{beneficio_neto:.2f} €", "lightgreen" if beneficio_neto >= 0 else "red"),
            ("Margen de Beneficio General", f"{margen_porcentaje:.1f} %", "orange" if margen_porcentaje < 30 else "gold"),
            ("Total Gastos de Envío Cobrados", f"{total_envios:.2f} €", "gray"),
            ("Pedidos Totales Realizados", f"{len(self.data['pedidos'])} pedidos", "purple")
        ]

        for i, (titulo, valor, color) in enumerate(card_config):
            row = i // 2
            col = i % 2
            
            card = ctk.CTkFrame(self.stats_frame, corner_radius=10)
            card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew", ipadx=10, ipady=10)
            
            ctk.CTkLabel(card, text=titulo, font=("Arial", 14, "bold")).pack(pady=(10, 5))
            ctk.CTkLabel(card, text=valor, font=("Arial", 22, "bold"), text_color=color).pack(pady=(5, 10))

        self.stats_frame.grid_columnconfigure(0, weight=1)
        self.stats_frame.grid_columnconfigure(1, weight=1)

    # --- PESTAÑA: CONFIGURACIÓN ---
    def build_configuracion(self):
        cfg = self.data["config"]
        
        ctk.CTkLabel(self.tab_conf, text="Ajustes de Costes", font=("Arial", 20, "bold")).pack(pady=10)
        
        ctk.CTkLabel(self.tab_conf, text="Precio de la electricidad (€ por kWh):").pack(pady=(10, 0))
        self.cfg_kwh = ctk.CTkEntry(self.tab_conf)
        self.cfg_kwh.insert(0, str(cfg["precio_kwh"]))
        self.cfg_kwh.pack(pady=(0, 10))
        
        ctk.CTkLabel(self.tab_conf, text="Consumo medio de la impresora (Vatios/W):").pack(pady=(10, 0))
        self.cfg_watts = ctk.CTkEntry(self.tab_conf)
        self.cfg_watts.insert(0, str(cfg["consumo_watts"]))
        self.cfg_watts.pack(pady=(0, 10))
        
        ctk.CTkLabel(self.tab_conf, text="Precio de compra de la impresora (€):").pack(pady=(10, 0))
        self.cfg_imp = ctk.CTkEntry(self.tab_conf)
        self.cfg_imp.insert(0, str(cfg["precio_impresora"]))
        self.cfg_imp.pack(pady=(0, 10))

        ctk.CTkLabel(self.tab_conf, text="Vida útil estimada (Horas) - para amortización:").pack(pady=(10, 0))
        self.cfg_vida = ctk.CTkEntry(self.tab_conf)
        self.cfg_vida.insert(0, str(cfg.get("horas_vida", 5000)))
        self.cfg_vida.pack(pady=(0, 10))

        ctk.CTkButton(self.tab_conf, text="Guardar Configuración", command=self.save_config).pack(pady=20)
        self.lbl_cfg_ok = ctk.CTkLabel(self.tab_conf, text="", text_color="green")
        self.lbl_cfg_ok.pack()

    # --- LÓGICA DE DATOS Y VISTAS ---
    def get_filamentos_list(self):
        return [f"{k} - {v['color']} ({v['restante']}g)" for k, v in self.data["filamentos"].items()]

    def add_filamento(self):
        try:
            marca = self.fil_marca.get().strip()
            if not marca: return
            tipo = self.fil_tipo_custom.get().strip() if self.fil_tipo_var.get() == "Otro..." else self.fil_tipo_var.get()
            if not tipo: tipo = "PLA"
            color = self.fil_color_custom.get().strip() if self.fil_color_var.get() == "Otro..." else self.fil_color_var.get()
            if not color: color = "Desconocido"

            id_fil = f"{marca} {tipo} ({color})"
            peso_inicial = float(self.fil_peso.get())
            
            self.data["filamentos"][id_fil] = {
                "marca": marca, "tipo": tipo, "color": color, "acabado": self.fil_acabado.get(),
                "peso_inicial": peso_inicial, "restante": peso_inicial, "precio": float(self.fil_precio.get())
            }
            self.save_data()
            self.actualizar_vista_stock()
            
            nueva_lista = self.get_filamentos_list()
            self.menu_filamentos.configure(values=nueva_lista)
            if nueva_lista: self.calc_fil_var.set(nueva_lista[0])
            
            self.fil_marca.delete(0, 'end')
            self.fil_peso.delete(0, 'end')
            self.fil_precio.delete(0, 'end')
            self.fil_tipo_custom.delete(0, 'end')
            self.fil_color_custom.delete(0, 'end')
            self.fil_tipo_custom.grid_forget()
            self.fil_color_custom.grid_forget()
            self.fil_tipo_var.set("PLA")
            self.fil_color_var.set("Negro")
        except ValueError:
            pass

    def eliminar_filamento(self, id_fil):
        if id_fil in self.data["filamentos"]:
            del self.data["filamentos"][id_fil]
            self.save_data()
            self.actualizar_vista_stock()
            nueva_lista = self.get_filamentos_list()
            self.menu_filamentos.configure(values=nueva_lista or ["No hay filamentos"])
            if nueva_lista: self.calc_fil_var.set(nueva_lista[0])
            else: self.calc_fil_var.set("No hay filamentos")

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
            ctk.CTkButton(card, text="Borrar", width=70, fg_color="red", hover_color="darkred", command=lambda id_f=k: self.eliminar_filamento(id_f)).pack(side="right", padx=10, pady=5)

    def actualizar_vista_historial(self):
        for widget in self.scroll_hist.winfo_children(): widget.destroy()
        for index, h in enumerate(reversed(self.data["historial"])):
            real_index = len(self.data["historial"]) - 1 - index
            card = ctk.CTkFrame(self.scroll_hist)
            card.pack(pady=4, padx=5, fill="x", expand=True)
            nombre_articulo = f"[{h.get('nombre', 'Sin nombre')}] " if h.get('nombre') else ""
            info_text = f"{h['fecha']}  |  {nombre_articulo}{h['filamento']}  |  {h['gramos']}g  |  {h['tiempo']}  |  Coste: {h['coste_total']:.2f}€"
            ctk.CTkLabel(card, text=info_text, anchor="w", font=("Arial", 12)).pack(side="left", padx=10, pady=8, fill="x", expand=True)
            ctk.CTkButton(card, text="Borrar y devolver stock", width=150, fg_color="darkred", hover_color="firebrick", command=lambda idx=real_index: self.eliminar_historial(idx)).pack(side="right", padx=10, pady=5)

    def eliminar_historial(self, index):
        h = self.data["historial"][index]
        fil_name = h["filamento"]
        gramos_gastados = h["gramos"]
        if fil_name in self.data["filamentos"]:
            self.data["filamentos"][fil_name]["restante"] += gramos_gastados
            if self.data["filamentos"][fil_name]["restante"] > self.data["filamentos"][fil_name]["peso_inicial"]:
                self.data["filamentos"][fil_name]["restante"] = self.data["filamentos"][fil_name]["peso_inicial"]
        del self.data["historial"][index]
        self.save_data()
        self.actualizar_vista_stock()
        self.actualizar_vista_historial()
        self.actualizar_selectores_pedidos()
        self.actualizar_vista_estadisticas()
        self.menu_filamentos.configure(values=self.get_filamentos_list() or ["No hay filamentos"])

    # --- LÓGICA DE CLIENTES Y PEDIDOS ---
    def add_cliente(self):
        nombre = self.cli_nombre.get().strip()
        tel = self.cli_tel.get().strip()
        email = self.cli_email.get().strip()
        direccion = self.cli_dir.get().strip()
        if not nombre: return
        
        self.data["clientes"][nombre] = {
            "telefono": tel,
            "email": email,
            "direccion": direccion
        }
        self.save_data()
        
        self.cli_nombre.delete(0, 'end')
        self.cli_tel.delete(0, 'end')
        self.cli_email.delete(0, 'end')
        self.cli_dir.delete(0, 'end')
        
        self.actualizar_vista_clientes()
        self.actualizar_selectores_pedidos()

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
            ctk.CTkButton(card, text="X", width=30, fg_color="red", command=lambda c=cli: self.eliminar_cliente(c)).pack(side="right", padx=5)

    def add_pedido(self):
        try:
            cliente = self.ped_cli_var.get()
            impresion_str = self.ped_hist_var.get()
            precio_prod = float(self.ped_precio_prod.get() or 0.0)
            envio = float(self.ped_envio.get() or 0.0)
            total = precio_prod + envio
            
            if not cliente or cliente == "Sin clientes" or not impresion_str or impresion_str == "No hay historial":
                return

            self.data["pedidos"].append({
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "cliente": cliente,
                "impresion": impresion_str,
                "precio_prod": precio_prod,
                "envio": envio,
                "total": total
            })
            self.save_data()
            self.actualizar_vista_pedidos()
            self.actualizar_vista_estadisticas()
            
            self.ped_precio_prod.delete(0, 'end')
            self.ped_envio.delete(0, 'end')
            self.ped_envio.insert(0, "0.00")
            self.lbl_ped_total.configure(text="0.00 €")
        except ValueError:
            pass

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
            info = f"{p['fecha']} | Cliente: {p['cliente']} | Total: {p['total']:.2f}€ (Prod: {p['precio_prod']:.2f}€ + Envío: {p['envio']:.2f}€)\nRef: {p['impresion']}"
            ctk.CTkLabel(card, text=info, anchor="w", font=("Arial", 11)).pack(side="left", padx=10, pady=5, fill="x", expand=True)
            ctk.CTkButton(card, text="Borrar", width=60, fg_color="red", command=lambda idx=real_index: self.eliminar_pedido(idx)).pack(side="right", padx=10)

    def actualizar_selectores_pedidos(self):
        clientes_list = list(self.data["clientes"].keys())
        self.menu_ped_cli.configure(values=clientes_list or ["Sin clientes"])
        if clientes_list: self.ped_cli_var.set(clientes_list[0])
        else: self.ped_cli_var.set("Sin clientes")

        hist_list = [f"[{h.get('fecha','')}] {h.get('nombre','Pieza')} ({h.get('coste_total',0):.2f}€)" for h in self.data["historial"]]
        self.menu_ped_hist.configure(values=hist_list or ["No hay historial"])
        if hist_list: self.ped_hist_var.set(hist_list[0])
        else: self.ped_hist_var.set("No hay historial")

    def save_config(self):
        try:
            self.data["config"]["precio_kwh"] = float(self.cfg_kwh.get())
            self.data["config"]["consumo_watts"] = float(self.cfg_watts.get())
            self.data["config"]["precio_impresora"] = float(self.cfg_imp.get())
            self.data["config"]["horas_vida"] = float(self.cfg_vida.get())
            self.save_data()
            self.lbl_cfg_ok.configure(text="¡Configuración guardada correctamente!")
            self.after(3000, lambda: self.lbl_cfg_ok.configure(text=""))
        except ValueError:
            self.lbl_cfg_ok.configure(text="Error: Revisa que los valores sean numéricos", text_color="red")

    def calcular_coste(self):
        try:
            cfg = self.data["config"]
            fil_seleccionado = self.calc_fil_var.get()
            if not fil_seleccionado or fil_seleccionado == "No hay filamentos":
                self.lbl_resultado.configure(text="Selecciona un filamento válido")
                return False
            fil_str = fil_seleccionado.split(" - ")[0]
            if fil_str not in self.data["filamentos"]:
                self.lbl_resultado.configure(text="Filamento no encontrado")
                return False
            fil = self.data["filamentos"][fil_str]
            horas = float(self.calc_horas.get() or 0) + (float(self.calc_mins.get() or 0) / 60)
            gramos = float(self.calc_gramos.get())
            coste_mat = (gramos / fil["peso_inicial"]) * fil["precio"]
            coste_luz = (cfg["consumo_watts"] / 1000) * horas * cfg["precio_kwh"]
            desgaste = (cfg["precio_impresora"] / cfg["horas_vida"]) * horas
            self.coste_actual = coste_mat + coste_luz + desgaste
            self.lbl_resultado.configure(text=f"Coste Total: {self.coste_actual:.2f} €\n(Material: {coste_mat:.2f}€ | Luz: {coste_luz:.2f}€ | Desgaste: {desgaste:.2f}€)")
            return True
        except Exception:
            self.lbl_resultado.configure(text="Revisa los campos de tiempo y gramos")
            return False

    def guardar_impresion(self):
        if self.calcular_coste():
            fil_seleccionado = self.calc_fil_var.get()
            fil_str = fil_seleccionado.split(" - ")[0]
            gramos = float(self.calc_gramos.get())
            nombre_articulo = self.calc_nombre.get().strip()
            
            self.data["filamentos"][fil_str]["restante"] -= gramos
            if self.data["filamentos"][fil_str]["restante"] < 0:
                self.data["filamentos"][fil_str]["restante"] = 0
            
            self.data["historial"].append({
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "nombre": nombre_articulo,
                "filamento": fil_str,
                "gramos": gramos,
                "tiempo": f"{self.calc_horas.get() or 0}h {self.calc_mins.get() or 0}m",
                "coste_total": self.coste_actual
            })
            
            self.save_data()
            self.actualizar_vista_stock()
            self.actualizar_vista_historial()
            self.actualizar_selectores_pedidos()
            self.actualizar_vista_estadisticas()
            self.menu_filamentos.configure(values=self.get_filamentos_list())
            self.calc_nombre.delete(0, 'end')
            self.lbl_resultado.configure(text="¡Impresión guardada en el historial y stock descontado!")

if __name__ == "__main__":
    app = App3D()
    app.mainloop()