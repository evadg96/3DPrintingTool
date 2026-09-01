import customtkinter as ctk
import json
import os
from datetime import datetime

# Crear carpeta en Documentos para evitar el bloqueo de macOS
USER_DIR = os.path.expanduser("~/Documents/Gestor3D")
os.makedirs(USER_DIR, exist_ok=True)
DATA_FILE = os.path.join(USER_DIR, "impresiones_data.json")

# Datos por defecto
DEFAULT_DATA = {
    "filamentos": {},
    "historial": [],
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
        self.title("Gestor de Impresión 3D")
        self.geometry("900x720")
        ctk.set_appearance_mode("dark")
        
        self.data = self.load_data()
        
        # Sistema de Pestañas
        self.tabview = ctk.CTkTabview(self, width=850, height=660)
        self.tabview.pack(padx=20, pady=20)
        
        self.tab_calc = self.tabview.add("Calculadora")
        self.tab_fil = self.tabview.add("Filamentos")
        self.tab_hist = self.tabview.add("Historial")
        self.tab_conf = self.tabview.add("Configuración")
        
        self.build_calculadora()
        self.build_filamentos()
        self.build_historial()
        self.build_configuracion()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                return DEFAULT_DATA
        return DEFAULT_DATA

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f, indent=4)

    # --- PESTAÑA: CALCULADORA ---
    def build_calculadora(self):
        ctk.CTkLabel(self.tab_calc, text="Nueva Impresión / Simulador", font=("Arial", 20, "bold")).pack(pady=10)
        
        # Nombre del artículo (Opcional)
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
        
        # Botones separados para simular y para guardar de verdad
        btn_frame = ctk.CTkFrame(self.tab_calc, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(btn_frame, text="Calcular Coste", fg_color="blue", command=self.calcular_coste).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Guardar en el Historial (Descontar Stock)", fg_color="green", command=self.guardar_impresion).pack(side="left", padx=10)

    # --- PESTAÑA: FILAMENTOS ---
    def build_filamentos(self):
        ctk.CTkLabel(self.tab_fil, text="Gestión de Stock y Rollos", font=("Arial", 18, "bold")).pack(pady=5)
        
        form_frame = ctk.CTkFrame(self.tab_fil)
        form_frame.pack(pady=5, padx=10, fill="x")
        
        # Fila 0: Marca, Tipo unificado y Color
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

        # Fila 1: Entradas personalizadas condicionales (Tipo custom y Color custom)
        self.fil_tipo_custom = ctk.CTkEntry(form_frame, placeholder_text="Tipo específico...")
        self.fil_color_custom = ctk.CTkEntry(form_frame, placeholder_text="Color específico...")

        # Fila 2: Acabado visual extra, Peso y Precio
        self.fil_acabado = ctk.CTkOptionMenu(form_frame, values=["Mate", "Brillo", "Seda / Silk", "Metálico", "Fluorescente", "Glitter"])
        self.fil_acabado.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        self.fil_acabado.set("Mate")
        
        self.fil_peso = ctk.CTkEntry(form_frame, placeholder_text="Peso total (g, ej. 1000)")
        self.fil_peso.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        self.fil_precio = ctk.CTkEntry(form_frame, placeholder_text="Precio (€, ej. 19.99)")
        self.fil_precio.grid(row=2, column=2, padx=5, pady=5, sticky="ew")
        
        # Ajustar pesos de columnas
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(2, weight=1)

        ctk.CTkButton(form_frame, text="Añadir Nuevo Rollo", fg_color="green", command=self.add_filamento).grid(row=3, column=0, columnspan=3, pady=8, sticky="ew")
        
        # Barra de Búsqueda / Filtro
        search_frame = ctk.CTkFrame(self.tab_fil, fg_color="transparent")
        search_frame.pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(search_frame, text="Filtrar filamentos:").pack(side="left", padx=5)
        self.fil_search = ctk.CTkEntry(search_frame, placeholder_text="Escribe para buscar...")
        self.fil_search.pack(side="left", padx=5, fill="x", expand=True)
        self.fil_search.bind("<KeyRelease>", lambda e: self.actualizar_vista_stock())

        # Contenedor con scroll para la lista visual
        self.scroll_stock = ctk.CTkScrollableFrame(self.tab_fil, width=800, height=200)
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
        
        self.scroll_hist = ctk.CTkScrollableFrame(self.tab_hist, width=820, height=480)
        self.scroll_hist.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.actualizar_vista_historial()

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
            if not marca:
                return
            
            tipo = self.fil_tipo_custom.get().strip() if self.fil_tipo_var.get() == "Otro..." else self.fil_tipo_var.get()
            if not tipo: tipo = "PLA"

            color = self.fil_color_custom.get().strip() if self.fil_color_var.get() == "Otro..." else self.fil_color_var.get()
            if not color: color = "Desconocido"

            id_fil = f"{marca} {tipo} ({color})"
            
            peso_inicial = float(self.fil_peso.get())
            
            self.data["filamentos"][id_fil] = {
                "marca": marca,
                "tipo": tipo,
                "color": color,
                "acabado": self.fil_acabado.get(),
                "peso_inicial": peso_inicial,
                "restante": peso_inicial,
                "precio": float(self.fil_precio.get())
            }
            self.save_data()
            self.actualizar_vista_stock()
            
            nueva_lista = self.get_filamentos_list()
            self.menu_filamentos.configure(values=nueva_lista)
            if nueva_lista:
                self.calc_fil_var.set(nueva_lista[0])
            
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
            if nueva_lista:
                self.menu_filamentos.configure(values=nueva_lista)
                self.calc_fil_var.set(nueva_lista[0])
            else:
                self.menu_filamentos.configure(values=["No hay filamentos"])
                self.calc_fil_var.set("No hay filamentos")

    def actualizar_vista_stock(self):
        for widget in self.scroll_stock.winfo_children():
            widget.destroy()
            
        filtro = self.fil_search.get().lower() if hasattr(self, 'fil_search') else ""
        
        for k, v in self.data["filamentos"].items():
            acabado = v.get("acabado", "Mate")
            texto_busqueda = f"{v['marca']} {v['tipo']} {v['color']} {acabado}".lower()
            if filtro and filtro not in texto_busqueda:
                continue
                
            card = ctk.CTkFrame(self.scroll_stock)
            card.pack(pady=4, padx=5, fill="x", expand=True)
            
            info_text = f"[{v['tipo']}] {v['marca']} | Color: {v['color']} ({acabado}) | Quedan: {v['restante']:.1f}g / {v['peso_inicial']}g | Precio: {v['precio']}€"
            lbl = ctk.CTkLabel(card, text=info_text, anchor="w", font=("Arial", 12))
            lbl.pack(side="left", padx=10, pady=8, fill="x", expand=True)
            
            btn_del = ctk.CTkButton(card, text="Borrar", width=70, fg_color="red", hover_color="darkred",
                                    command=lambda id_f=k: self.eliminar_filamento(id_f))
            btn_del.pack(side="right", padx=10, pady=5)

    def actualizar_vista_historial(self):
        for widget in self.scroll_hist.winfo_children():
            widget.destroy()
            
        for index, h in enumerate(reversed(self.data["historial"])):
            real_index = len(self.data["historial"]) - 1 - index
            
            card = ctk.CTkFrame(self.scroll_hist)
            card.pack(pady=4, padx=5, fill="x", expand=True)
            
            nombre_articulo = f"[{h.get('nombre', 'Sin nombre')}] " if h.get('nombre') else ""
            info_text = f"{h['fecha']}  |  {nombre_articulo}{h['filamento']}  |  {h['gramos']}g  |  {h['tiempo']}  |  Coste: {h['coste_total']:.2f}€"
            lbl = ctk.CTkLabel(card, text=info_text, anchor="w", font=("Arial", 12))
            lbl.pack(side="left", padx=10, pady=8, fill="x", expand=True)
            
            btn_del = ctk.CTkButton(card, text="Borrar y devolver stock", width=150, fg_color="darkred", hover_color="firebrick",
                                    command=lambda idx=real_index: self.eliminar_historial(idx))
            btn_del.pack(side="right", padx=10, pady=5)

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
        
        nueva_lista = self.get_filamentos_list()
        self.menu_filamentos.configure(values=nueva_lista or ["No hay filamentos"])

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
        # Primero aseguramos que el cálculo es válido y está actualizado
        if self.calcular_coste():
            fil_seleccionado = self.calc_fil_var.get()
            fil_str = fil_seleccionado.split(" - ")[0]
            gramos = float(self.calc_gramos.get())
            nombre_articulo = self.calc_nombre.get().strip()
            
            # Restar stock
            self.data["filamentos"][fil_str]["restante"] -= gramos
            if self.data["filamentos"][fil_str]["restante"] < 0:
                self.data["filamentos"][fil_str]["restante"] = 0
            
            # Guardar en historial con el nombre opcional
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
            self.menu_filamentos.configure(values=self.get_filamentos_list())
            
            # Limpiar nombre tras guardar con éxito
            self.calc_nombre.delete(0, 'end')
            self.lbl_resultado.configure(text="¡Impresión guardada en el historial y stock descontado!")

if __name__ == "__main__":
    app = App3D()
    app.mainloop()