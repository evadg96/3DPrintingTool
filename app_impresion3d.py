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
        self.geometry("850x650")
        ctk.set_appearance_mode("dark")
        
        self.data = self.load_data()
        
        # Sistema de Pestañas
        self.tabview = ctk.CTkTabview(self, width=800, height=600)
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
        ctk.CTkLabel(self.tab_calc, text="Nueva Impresión", font=("Arial", 20, "bold")).pack(pady=10)
        
        ctk.CTkLabel(self.tab_calc, text="Selecciona el filamento a utilizar:").pack(pady=(5, 0))
        self.calc_fil_var = ctk.StringVar(value="Selecciona un filamento" if not self.get_filamentos_list() else self.get_filamentos_list()[0])
        self.menu_filamentos = ctk.CTkOptionMenu(self.tab_calc, variable=self.calc_fil_var, values=self.get_filamentos_list() or ["No hay filamentos"])
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
        
        ctk.CTkButton(self.tab_calc, text="Calcular Coste", command=self.calcular_coste).pack(pady=5)
        ctk.CTkButton(self.tab_calc, text="Guardar e Imprimir (Descontar Stock)", fg_color="green", command=self.guardar_impresion).pack(pady=5)

    # --- PESTAÑA: FILAMENTOS ---
    def build_filamentos(self):
        ctk.CTkLabel(self.tab_fil, text="Gestión de Stock y Rollos", font=("Arial", 18, "bold")).pack(pady=5)
        
        form_frame = ctk.CTkFrame(self.tab_fil)
        form_frame.pack(pady=5, padx=10, fill="x")
        
        self.fil_marca = ctk.CTkEntry(form_frame, placeholder_text="Marca (ej. Sunlu)")
        self.fil_marca.grid(row=0, column=0, padx=5, pady=5)
        self.fil_tipo = ctk.CTkEntry(form_frame, placeholder_text="Tipo (PLA, PETG...)")
        self.fil_tipo.grid(row=0, column=1, padx=5, pady=5)
        self.fil_color = ctk.CTkEntry(form_frame, placeholder_text="Color")
        self.fil_color.grid(row=0, column=2, padx=5, pady=5)
        
        # Selector de Acabado (Mate / Brillo)
        self.fil_acabado = ctk.CTkOptionMenu(form_frame, values=["Mate", "Brillo"])
        self.fil_acabado.grid(row=1, column=0, padx=5, pady=5)
        self.fil_acabado.set("Mate")
        
        self.fil_peso = ctk.CTkEntry(form_frame, placeholder_text="Peso total (g)")
        self.fil_peso.grid(row=1, column=1, padx=5, pady=5)
        self.fil_precio = ctk.CTkEntry(form_frame, placeholder_text="Precio (€)")
        self.fil_precio.grid(row=1, column=2, padx=5, pady=5)
        
        ctk.CTkButton(form_frame, text="Añadir Nuevo Rollo", fg_color="blue", command=self.add_filamento).grid(row=2, column=0, columnspan=3, pady=8, sticky="ew")
        
        # Barra de Búsqueda / Filtro
        search_frame = ctk.CTkFrame(self.tab_fil, fg_color="transparent")
        search_frame.pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(search_frame, text="Filtrar filamentos:").pack(side="left", padx=5)
        self.fil_search = ctk.CTkEntry(search_frame, placeholder_text="Escribe para buscar...")
        self.fil_search.pack(side="left", padx=5, fill="x", expand=True)
        self.fil_search.bind("<KeyRelease>", lambda e: self.actualizar_vista_stock())

        # Contenedor con scroll para la lista visual
        self.scroll_stock = ctk.CTkScrollableFrame(self.tab_fil, width=760, height=240)
        self.scroll_stock.pack(pady=5, padx=10, fill="both", expand=True)
        
        self.actualizar_vista_stock()

    # --- PESTAÑA: HISTORIAL ---
    def build_historial(self):
        ctk.CTkLabel(self.tab_hist, text="Historial de Impresiones", font=("Arial", 18, "bold")).pack(pady=5)
        
        self.scroll_hist = ctk.CTkScrollableFrame(self.tab_hist, width=780, height=480)
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
            tipo = self.fil_tipo.get().strip()
            if not marca or not tipo:
                return
            
            id_fil = f"{marca} {tipo} ({self.fil_color.get().strip()})"
            peso_inicial = float(self.fil_peso.get())
            
            self.data["filamentos"][id_fil] = {
                "marca": marca,
                "tipo": tipo,
                "color": self.fil_color.get().strip(),
                "acabado": self.fil_acabado.get(),
                "peso_inicial": peso_inicial,
                "restante": peso_inicial,
                "precio": float(self.fil_precio.get())
            }
            self.save_data()
            self.actualizar_vista_stock()
            self.menu_filamentos.configure(values=self.get_filamentos_list() or ["No hay filamentos"])
            
            # Limpiar campos
            self.fil_marca.delete(0, 'end')
            self.fil_tipo.delete(0, 'end')
            self.fil_color.delete(0, 'end')
            self.fil_peso.delete(0, 'end')
            self.fil_precio.delete(0, 'end')
        except ValueError:
            pass

    def eliminar_filamento(self, id_fil):
        if id_fil in self.data["filamentos"]:
            del self.data["filamentos"][id_fil]
            self.save_data()
            self.actualizar_vista_stock()
            self.menu_filamentos.configure(values=self.get_filamentos_list() or ["No hay filamentos"])

    def actualizar_vista_stock(self):
        for widget in self.scroll_stock.winfo_children():
            widget.destroy()
            
        filtro = self.fil_search.get().lower() if hasattr(self, 'fil_search') else ""
        
        for k, v in self.data["filamentos"].items():
            acabado = v.get("acabado")
            texto_busqueda = f"{v['marca']} {v['tipo']} {v['color']} {acabado}".lower()
            if filtro and filtro not in texto_busqueda:
                continue
                
            card = ctk.CTkFrame(self.scroll_stock)
            card.pack(pady=4, padx=5, fill="x", expand=True)
            
            info_text = f"[{v['tipo']} - {acabado}] {v['marca']} | Color: {v['color']} | Quedan: {v['restante']:.1f}g / {v['peso_inicial']}g | Precio: {v['precio']}€"
            lbl = ctk.CTkLabel(card, text=info_text, anchor="w", font=("Arial", 13))
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
            
            info_text = f"{h['fecha']}  |  {h['filamento']}  |  {h['gramos']}g  |  {h['tiempo']}  |  Coste: {h['coste_total']:.2f}€"
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
        self.menu_filamentos.configure(values=self.get_filamentos_list() or ["No hay filamentos"])

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
            
            self.data["filamentos"][fil_str]["restante"] -= gramos
            if self.data["filamentos"][fil_str]["restante"] < 0:
                self.data["filamentos"][fil_str]["restante"] = 0
            
            self.data["historial"].append({
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "filamento": fil_str,
                "gramos": gramos,
                "tiempo": f"{self.calc_horas.get() or 0}h {self.calc_mins.get() or 0}m",
                "coste_total": self.coste_actual
            })
            
            self.save_data()
            self.actualizar_vista_stock()
            self.actualizar_vista_historial()
            self.menu_filamentos.configure(values=self.get_filamentos_list())
            self.lbl_resultado.configure(text="¡Impresión guardada y stock descontado!")

if __name__ == "__main__":
    app = App3D()
    app.mainloop()