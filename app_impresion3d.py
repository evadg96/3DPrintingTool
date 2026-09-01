import customtkinter as ctk
import json
import os
from datetime import datetime

# Crear carpeta en Documentos para evitar el bloqueo de macOS
USER_DIR = os.path.expanduser("~/Documents/Gestor3D")
os.makedirs(USER_DIR, exist_ok=True)
DATA_FILE = os.path.join(USER_DIR, "impresiones_data.json")

# Datos por defecto
# Datos por defecto (optimizados para una impresora eficiente de última generación)
DEFAULT_DATA = {
    "filamentos": {},
    "historial": [],
    "config": {
        "precio_kwh": 0.15,
        "consumo_watts": 65, # Consumo medio típico (ej. impresoras cartesianas modernas)
        "precio_impresora": 400,
        "horas_vida": 5000,
        "margen_beneficio": 0 # % extra por si decides venderlas
    }
}

class App3D(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gestor de Impresión 3D")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")
        
        self.data = self.load_data()
        
        # Sistema de Pestañas
        self.tabview = ctk.CTkTabview(self, width=750, height=550)
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
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        return DEFAULT_DATA

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f, indent=4)

    # --- PESTAÑA: CALCULADORA ---
    def build_calculadora(self):
        ctk.CTkLabel(self.tab_calc, text="Nueva Impresión", font=("Arial", 20, "bold")).pack(pady=10)
        
        self.calc_fil_var = ctk.StringVar(value="Selecciona un filamento")
        self.menu_filamentos = ctk.CTkOptionMenu(self.tab_calc, variable=self.calc_fil_var, values=self.get_filamentos_list())
        self.menu_filamentos.pack(pady=10)
        
        row1 = ctk.CTkFrame(self.tab_calc, fg_color="transparent")
        row1.pack(pady=10)
        self.calc_horas = ctk.CTkEntry(row1, placeholder_text="Horas")
        self.calc_horas.pack(side="left", padx=5)
        self.calc_mins = ctk.CTkEntry(row1, placeholder_text="Minutos")
        self.calc_mins.pack(side="left", padx=5)
        
        self.calc_gramos = ctk.CTkEntry(self.tab_calc, placeholder_text="Peso (gramos)")
        self.calc_gramos.pack(pady=10)
        
        self.lbl_resultado = ctk.CTkLabel(self.tab_calc, text="Coste Total: 0.00 €", font=("Arial", 16))
        self.lbl_resultado.pack(pady=20)
        
        ctk.CTkButton(self.tab_calc, text="Calcular Coste", command=self.calcular_coste).pack(pady=5)
        ctk.CTkButton(self.tab_calc, text="Guardar y Descontar Stock", fg_color="green", command=self.guardar_impresion).pack(pady=5)

    # --- PESTAÑA: FILAMENTOS ---
    def build_filamentos(self):
        form_frame = ctk.CTkFrame(self.tab_fil)
        form_frame.pack(pady=10, padx=10, fill="x")
        
        self.fil_marca = ctk.CTkEntry(form_frame, placeholder_text="Marca (ej. Sunlu)")
        self.fil_marca.grid(row=0, column=0, padx=5, pady=5)
        self.fil_tipo = ctk.CTkEntry(form_frame, placeholder_text="Tipo (PLA, PETG...)")
        self.fil_tipo.grid(row=0, column=1, padx=5, pady=5)
        self.fil_color = ctk.CTkEntry(form_frame, placeholder_text="Color")
        self.fil_color.grid(row=0, column=2, padx=5, pady=5)
        self.fil_peso = ctk.CTkEntry(form_frame, placeholder_text="Peso total (g)")
        self.fil_peso.grid(row=1, column=0, padx=5, pady=5)
        self.fil_precio = ctk.CTkEntry(form_frame, placeholder_text="Precio (€)")
        self.fil_precio.grid(row=1, column=1, padx=5, pady=5)
        
        ctk.CTkButton(form_frame, text="Añadir Rollo", command=self.add_filamento).grid(row=1, column=2, padx=5, pady=5)
        
        self.txt_stock = ctk.CTkTextbox(self.tab_fil, width=700, height=300)
        self.txt_stock.pack(pady=10)
        self.actualizar_vista_stock()

    # --- PESTAÑA: HISTORIAL ---
    def build_historial(self):
        self.txt_hist = ctk.CTkTextbox(self.tab_hist, width=700, height=450)
        self.txt_hist.pack(pady=10)
        self.actualizar_vista_historial()

    # --- PESTAÑA: CONFIGURACIÓN ---
    def build_configuracion(self):
        cfg = self.data["config"]
        
        ctk.CTkLabel(self.tab_conf, text="Ajustes de Costes", font=("Arial", 20, "bold")).pack(pady=10)
        
        # Precio del kWh
        ctk.CTkLabel(self.tab_conf, text="Precio de la electricidad (€ por kWh):").pack(pady=(10, 0))
        self.cfg_kwh = ctk.CTkEntry(self.tab_conf)
        self.cfg_kwh.insert(0, str(cfg["precio_kwh"]))
        self.cfg_kwh.pack(pady=(0, 10))
        
        # Consumo de la impresora
        ctk.CTkLabel(self.tab_conf, text="Consumo medio de la impresora (Vatios/W):").pack(pady=(10, 0))
        self.cfg_watts = ctk.CTkEntry(self.tab_conf)
        self.cfg_watts.insert(0, str(cfg["consumo_watts"]))
        self.cfg_watts.pack(pady=(0, 10))
        
        # Precio de la máquina (para desgaste)
        ctk.CTkLabel(self.tab_conf, text="Precio de compra de la impresora (€):").pack(pady=(10, 0))
        self.cfg_imp = ctk.CTkEntry(self.tab_conf)
        self.cfg_imp.insert(0, str(cfg["precio_impresora"]))
        self.cfg_imp.pack(pady=(0, 10))

        # Horas de vida útil
        ctk.CTkLabel(self.tab_conf, text="Vida útil estimada (Horas) - para amortización:").pack(pady=(10, 0))
        self.cfg_vida = ctk.CTkEntry(self.tab_conf)
        self.cfg_vida.insert(0, str(cfg.get("horas_vida", 5000)))
        self.cfg_vida.pack(pady=(0, 10))

        ctk.CTkButton(self.tab_conf, text="Guardar Configuración", command=self.save_config).pack(pady=20)
        
        # Etiqueta invisible que mostrará un mensaje de éxito al guardar
        self.lbl_cfg_ok = ctk.CTkLabel(self.tab_conf, text="", text_color="green")
        self.lbl_cfg_ok.pack()

    def save_config(self):
        self.data["config"]["precio_kwh"] = float(self.cfg_kwh.get())
        self.data["config"]["consumo_watts"] = float(self.cfg_watts.get())
        self.data["config"]["precio_impresora"] = float(self.cfg_imp.get())
        self.data["config"]["horas_vida"] = float(self.cfg_vida.get())
        self.save_data()
        
        # Mostrar mensaje de éxito temporal
        self.lbl_cfg_ok.configure(text="¡Configuración guardada correctamente!")
        self.after(3000, lambda: self.lbl_cfg_ok.configure(text=""))

    # --- LÓGICA DE DATOS ---
    def get_filamentos_list(self):
        return [f"{k} - {v['color']} ({v['restante']}g)" for k, v in self.data["filamentos"].items()]

    def add_filamento(self):
        id_fil = f"{self.fil_marca.get()} {self.fil_tipo.get()}"
        self.data["filamentos"][id_fil] = {
            "marca": self.fil_marca.get(),
            "tipo": self.fil_tipo.get(),
            "color": self.fil_color.get(),
            "peso_inicial": float(self.fil_peso.get()),
            "restante": float(self.fil_peso.get()),
            "precio": float(self.fil_precio.get())
        }
        self.save_data()
        self.actualizar_vista_stock()
        self.menu_filamentos.configure(values=self.get_filamentos_list())

    def actualizar_vista_stock(self):
        self.txt_stock.delete("1.0", "end")
        for k, v in self.data["filamentos"].items():
            self.txt_stock.insert("end", f"[{v['tipo']}] {k} - {v['color']} | Quedan: {v['restante']}g de {v['peso_inicial']}g | Coste: {v['precio']}€\n")

    def actualizar_vista_historial(self):
        self.txt_hist.delete("1.0", "end")
        for h in reversed(self.data["historial"]):
            self.txt_hist.insert("end", f"{h['fecha']} | {h['filamento']} | {h['gramos']}g | {h['tiempo']} | Coste: {h['coste_total']:.2f}€\n")

    def calcular_coste(self):
        try:
            cfg = self.data["config"]
            fil_str = self.calc_fil_var.get().split(" - ")[0]
            fil = self.data["filamentos"][fil_str]
            
            horas = float(self.calc_horas.get() or 0) + (float(self.calc_mins.get() or 0) / 60)
            gramos = float(self.calc_gramos.get())
            
            coste_mat = (gramos / fil["peso_inicial"]) * fil["precio"]
            coste_luz = (cfg["consumo_watts"] / 1000) * horas * cfg["precio_kwh"]
            desgaste = (cfg["precio_impresora"] / cfg["horas_vida"]) * horas
            
            self.coste_actual = coste_mat + coste_luz + desgaste
            self.lbl_resultado.configure(text=f"Coste Total: {self.coste_actual:.2f} €\n(Material: {coste_mat:.2f}€ | Luz: {coste_luz:.2f}€ | Desgaste: {desgaste:.2f}€)")
            return True
        except Exception as e:
            self.lbl_resultado.configure(text="Error en los datos introducidos")
            return False

    def guardar_impresion(self):
        if self.calcular_coste():
            fil_str = self.calc_fil_var.get().split(" - ")[0]
            gramos = float(self.calc_gramos.get())
            
            # Restar stock
            self.data["filamentos"][fil_str]["restante"] -= gramos
            
            # Guardar historial
            self.data["historial"].append({
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "filamento": fil_str,
                "gramos": gramos,
                "tiempo": f"{self.calc_horas.get()}h {self.calc_mins.get()}m",
                "coste_total": self.coste_actual
            })
            
            self.save_data()
            self.actualizar_vista_stock()
            self.actualizar_vista_historial()
            self.menu_filamentos.configure(values=self.get_filamentos_list())
            self.lbl_resultado.configure(text="¡Guardado y stock actualizado!")

if __name__ == "__main__":
    app = App3D()
    app.mainloop()