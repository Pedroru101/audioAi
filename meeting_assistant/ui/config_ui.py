# ui/config_ui.py (versión con selector de proveedor API)

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sounddevice as sd
import requests
import threading
import os

class ConfigUI:
    # ... (__init__ y otras funciones iniciales sin cambios)
    def __init__(self, root, config_manager, on_close):
        self.root = root
        self.config_manager = config_manager
        self.on_close = on_close
        self.config = self.config_manager.get_config()

        self.root.title("Configuración Avanzada")
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.geometry("700x750")

        self.llm_provider_var = tk.StringVar(value=self.config.get("llm_provider", "local"))
        self.save_path_var = tk.StringVar(value=self.config.get("save_path", ""))
        # Novedad: Variable para el proveedor de API
        self.api_provider_var = tk.StringVar(value=self.config.get("api_provider", "openai"))

        notebook = ttk.Notebook(self.root)
        notebook.pack(pady=10, padx=10, fill="both", expand=True)

        tab_ia = ttk.Frame(notebook)
        tab_audio_files = ttk.Frame(notebook)
        tab_history = ttk.Frame(notebook)

        notebook.add(tab_ia, text='IA y Prompts')
        notebook.add(tab_audio_files, text='Audio y Archivos')
        notebook.add(tab_history, text='Historial')

        self._create_ia_settings(tab_ia)
        self._create_audio_file_settings(tab_audio_files)
        self._create_history_settings(tab_history)
        
        self._create_action_buttons(self.root)
        self._on_provider_change()

    def _create_ia_settings(self, parent):
        # ... (frame de LLM y radio buttons sin cambios)
        parent.columnconfigure(0, weight=1)
        llm_frame = ttk.LabelFrame(parent, text="Modelo de Lenguaje (LLM)", padding="10")
        llm_frame.pack(fill="x", expand=True, pady=5, padx=5)
        
        ttk.Radiobutton(llm_frame, text="Local (Ollama)", variable=self.llm_provider_var, value="local", command=self._on_provider_change).pack(anchor="w")
        ttk.Radiobutton(llm_frame, text="API Remota", variable=self.llm_provider_var, value="api", command=self._on_provider_change).pack(anchor="w")

        # --- Frame Local (Ollama) ---
        self.local_frame = ttk.Frame(llm_frame, padding="5")
        # ... (código del frame local sin cambios)
        self.local_frame.pack(fill="x", expand=True, padx=20)
        ollama_conn_frame = ttk.Frame(self.local_frame)
        ollama_conn_frame.pack(fill="x", expand=True, pady=(0, 10))
        ollama_conn_frame.columnconfigure(1, weight=1)
        ollama_conn_frame.columnconfigure(3, weight=1)
        ttk.Label(ollama_conn_frame, text="Host:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.ollama_host_entry = ttk.Entry(ollama_conn_frame)
        self.ollama_host_entry.grid(row=0, column=1, sticky="ew")
        self.ollama_host_entry.insert(0, self.config.get("ollama_host", "http://localhost"))
        ttk.Label(ollama_conn_frame, text="Puerto:").grid(row=0, column=2, sticky="w", padx=(10, 5))
        self.ollama_port_entry = ttk.Entry(ollama_conn_frame, width=10)
        self.ollama_port_entry.grid(row=0, column=3, sticky="w")
        self.ollama_port_entry.insert(0, self.config.get("ollama_port", "11434"))
        ollama_model_frame = ttk.Frame(self.local_frame)
        ollama_model_frame.pack(fill="x", expand=True)
        ollama_model_frame.columnconfigure(0, weight=1)
        ttk.Label(ollama_model_frame, text="Modelo Local:").pack(anchor="w")
        self.local_model_combo = ttk.Combobox(ollama_model_frame, state="readonly")
        self.local_model_combo.pack(side="left", fill="x", expand=True, pady=(0, 5))
        self.local_model_combo.set("Haz clic en 'Probar Conexión' ->")
        ttk.Button(ollama_model_frame, text="Probar Conexión", command=self._detect_ollama_models_thread).pack(side="left", padx=5)

        # --- Frame API ---
        self.api_frame = ttk.Frame(llm_frame, padding="5")
        
        # Novedad: Selector de Proveedor API
        ttk.Label(self.api_frame, text="Proveedor de API:").pack(anchor="w")
        self.api_provider_combo = ttk.Combobox(self.api_frame, textvariable=self.api_provider_var, values=["openai", "openrouter"], state="readonly")
        self.api_provider_combo.pack(fill="x", expand=True, pady=(0, 10))
        
        api_key_frame = ttk.Frame(self.api_frame)
        api_key_frame.pack(fill="x", expand=True)
        api_key_frame.columnconfigure(0, weight=1)
        
        ttk.Label(api_key_frame, text="API Key:").pack(anchor="w")
        self.api_key_entry = ttk.Entry(api_key_frame, width=50, show="*")
        self.api_key_entry.pack(side="left", fill="x", expand=True)
        self.api_key_entry.insert(0, self.config.get("api_key", ""))
        ttk.Button(api_key_frame, text="Probar Conexión", command=self._test_api_connection_thread).pack(side="left", padx=5)

        ttk.Label(self.api_frame, text="Modelo API Disponible:").pack(anchor="w", pady=(10,0))
        self.api_model_combo = ttk.Combobox(self.api_frame, state="disabled")
        self.api_model_combo.pack(fill="x", expand=True)
        self.api_model_combo.set("Pruebe la conexión para cargar modelos")

        # --- Prompts ---
        # ... (código de prompts sin cambios)
        prompts_frame = ttk.LabelFrame(parent, text="Prompts Personalizados", padding="10")
        prompts_frame.pack(fill="both", expand=True, pady=5, padx=5)
        prompts_frame.rowconfigure(1, weight=1)
        prompts_frame.rowconfigure(3, weight=1)
        prompts_frame.columnconfigure(0, weight=1)
        ttk.Label(prompts_frame, text="Prompt para Resumen:").grid(row=0, column=0, sticky="w")
        self.summary_prompt_text = tk.Text(prompts_frame, height=8, wrap="word")
        self.summary_prompt_text.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        self.summary_prompt_text.insert("1.0", self.config.get("summary_prompt", ""))
        ttk.Label(prompts_frame, text="Prompt para Propuestas de Acción:").grid(row=2, column=0, sticky="w")
        self.action_items_prompt_text = tk.Text(prompts_frame, height=8, wrap="word")
        self.action_items_prompt_text.grid(row=3, column=0, sticky="nsew")
        self.action_items_prompt_text.insert("1.0", self.config.get("action_items_prompt", ""))

    def _test_api_connection_thread(self):
        api_key = self.api_key_entry.get()
        provider = self.api_provider_var.get()
        if not api_key:
            messagebox.showerror("Error", "El campo de API Key no puede estar vacío.")
            return
        threading.Thread(target=self._test_api_connection, args=(api_key, provider), daemon=True).start()

    def _test_api_connection(self, api_key, provider):
        # Novedad: Lógica condicional para URL y Headers
        headers = {"Authorization": f"Bearer {api_key}"}
        if provider == "openai":
            url = "https://api.openai.com/v1/models"
        elif provider == "openrouter":
            url = "https://openrouter.ai/api/v1/models"
            headers['HTTP-Referer'] = self.config.get("openrouter_site_url", "")
            headers['X-Title'] = self.config.get("openrouter_app_name", "")
        else:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Proveedor de API desconocido: {provider}"))
            return

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = sorted([m['id'] for m in data.get('data', [])])
                self.root.after(0, self._update_api_model_list, models)
            else:
                error_msg = response.json().get("error", {}).get("message", "Error desconocido.")
                self.root.after(0, lambda: messagebox.showerror("Error de Conexión", f"No se pudo conectar. Código: {response.status_code}\nError: {error_msg}"))
                self.root.after(0, self._update_api_model_list, [])
        except requests.exceptions.RequestException as e:
            self.root.after(0, lambda: messagebox.showerror("Error de Red", f"No se pudo alcanzar el servidor de la API.\nError: {e}"))
            self.root.after(0, self._update_api_model_list, [])

    def save_and_close(self):
        new_config = self.config.copy()
        new_config.update({
            "llm_provider": self.llm_provider_var.get(),
            # Novedad: Guardar el proveedor de API seleccionado
            "api_provider": self.api_provider_var.get(),
            "api_key": self.api_key_entry.get(),
            "api_model_name": self.api_model_combo.get(),
            # ... (resto de las configuraciones a guardar)
            "ollama_host": self.ollama_host_entry.get(),
            "ollama_port": self.ollama_port_entry.get(),
            "local_model_name": self.local_model_combo.get(),
            "summary_prompt": self.summary_prompt_text.get("1.0", tk.END).strip(),
            "action_items_prompt": self.action_items_prompt_text.get("1.0", tk.END).strip(),
            "audio_input_device": self.input_device_combo.get(),
            "audio_output_device": self.output_device_combo.get(),
            "save_path": self.save_path_var.get()
        })
        self.config_manager.save_config(new_config)
        messagebox.showinfo("Guardado", "La configuración se ha guardado correctamente.")
        self.close()

    # ... (resto de las funciones sin cambios)
    def _update_api_model_list(self, models):
        if models:
            messagebox.showinfo("Éxito", "Conexión exitosa. Se han cargado los modelos disponibles.")
            self.api_model_combo.config(state="readonly")
            self.api_model_combo['values'] = models
            
            current_model = self.config.get("api_model_name")
            if current_model in models:
                self.api_model_combo.set(current_model)
            else:
                self.api_model_combo.current(0)
        else:
            self.api_model_combo.config(state="disabled")
            self.api_model_combo['values'] = []
            self.api_model_combo.set("Pruebe la conexión para cargar modelos")

    def _create_audio_file_settings(self, parent):
        parent.columnconfigure(0, weight=1)
        audio_frame = ttk.LabelFrame(parent, text="Dispositivos de Audio", padding="10")
        audio_frame.pack(fill="x", expand=True, pady=5, padx=5)
        
        devices = sd.query_devices()
        input_devices = [f"{i}: {dev['name']}" for i, dev in enumerate(devices) if dev['max_input_channels'] > 0]
        output_devices = [f"{i}: {dev['name']}" for i, dev in enumerate(devices) if dev['max_output_channels'] > 0]
        
        ttk.Label(audio_frame, text="Dispositivo de Entrada (Micrófono):").pack(anchor="w")
        self.input_device_combo = ttk.Combobox(audio_frame, values=input_devices, state="readonly")
        self.input_device_combo.pack(fill="x", expand=True, pady=(0, 10))
        try:
            self.input_device_combo.set(self.config.get("audio_input_device", "default"))
        except tk.TclError:
            self.input_device_combo.set("default")

        ttk.Label(audio_frame, text="Dispositivo de Salida (Altavoces/Loopback):").pack(anchor="w")
        self.output_device_combo = ttk.Combobox(audio_frame, values=output_devices, state="readonly")
        self.output_device_combo.pack(fill="x", expand=True)
        try:
            self.output_device_combo.set(self.config.get("audio_output_device", "default"))
        except tk.TclError:
            self.output_device_combo.set("default")

        file_frame = ttk.LabelFrame(parent, text="Gestión de Archivos", padding="10")
        file_frame.pack(fill="x", expand=True, pady=5, padx=5)
        ttk.Label(file_frame, text="Carpeta para Guardar Grabaciones:").pack(anchor="w")
        path_frame = ttk.Frame(file_frame)
        path_frame.pack(fill="x", expand=True)
        path_entry = ttk.Entry(path_frame, textvariable=self.save_path_var, state="readonly")
        path_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(path_frame, text="Explorar...", command=self._browse_folder).pack(side="right")

    def _detect_ollama_models_thread(self):
        self.local_model_combo.set("Conectando...")
        threading.Thread(target=self._detect_ollama_models, daemon=True).start()

    def _detect_ollama_models(self):
        host = self.ollama_host_entry.get()
        port = self.ollama_port_entry.get()
        url = f"{host}:{port}/api/tags"
        try:
            response = requests.get(url, timeout=3)
            response.raise_for_status()
            models = [m['name'] for m in response.json().get('models', [])]
            if models:
                self.root.after(0, self._update_ollama_list, models)
            else:
                self.root.after(0, self._update_ollama_list, [], "Conexión exitosa, pero no hay modelos.")
        except requests.exceptions.RequestException as e:
            self.root.after(0, self._update_ollama_list, [], f"Error de conexión a {url}.")

    def _create_history_settings(self, parent):
        history_frame = ttk.LabelFrame(parent, text="Historial de Reuniones", padding="10")
        history_frame.pack(fill="both", expand=True, pady=5, padx=5)
        ttk.Label(history_frame, text="Esta funcionalidad está en desarrollo.").pack(pady=20)

    def _create_action_buttons(self, parent):
        button_frame = ttk.Frame(parent, padding="10")
        button_frame.pack(fill="x", side="bottom")
        ttk.Button(button_frame, text="Guardar y Cerrar", command=self.save_and_close).pack(side="right")
        ttk.Button(button_frame, text="Cancelar", command=self.close).pack(side="right", padx=5)

    def _browse_folder(self):
        path = filedialog.askdirectory(initialdir=self.save_path_var.get())
        if path:
            self.save_path_var.set(path)

    def _on_provider_change(self):
        provider = self.llm_provider_var.get()
        if provider == "local":
            self.local_frame.pack(fill="x", expand=True, padx=20, pady=5)
            self.api_frame.pack_forget()
        else:
            self.local_frame.pack_forget()
            self.api_frame.pack(fill="x", expand=True, padx=20, pady=5)

    def _update_ollama_list(self, models, message=None):
        if models:
            self.local_model_combo['values'] = models
            current_model = self.config.get("local_model_name")
            if current_model in models:
                self.local_model_combo.set(current_model)
            elif models:
                self.local_model_combo.current(0)
        else:
            self.local_model_combo['values'] = []
            self.local_model_combo.set(message)
        self.local_model_combo.config(state="readonly")

    def close(self):
        self.root.destroy()
        if self.on_close:
            self.on_close()