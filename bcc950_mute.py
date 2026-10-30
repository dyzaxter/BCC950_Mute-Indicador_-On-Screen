#!/usr/bin/env python
# -*- coding: utf-8 -*-
VERSION = "v7-toggle"

import collections, collections.abc
for _name in dir(collections.abc):
    if not _name.startswith('_') and not hasattr(collections, _name):
        setattr(collections, _name, getattr(collections.abc, _name))
assert hasattr(collections, 'Callable')

import sys, os, time, threading, traceback, tkinter as tk
try:
    import pywinusb.hid as hid
except ImportError:
    print("Falta pywinusb. Instálalo con: py -3 -m pip install pywinusb")
    sys.exit(1)

LOGITECH_VID = 0x046D
LOGITECH_PIDS = {0x0837, 0x0838}
TARGET_USAGE = hid.get_full_usage_id(0x0B, 0x2F)
DEBOUNCE_SECONDS = 0.3

LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bcc950.log")
def log(m):
    linea = f"[{time.strftime('%H:%M:%S')}] {m}"
    print(linea)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(linea + "\n")
    except OSError:
        pass

log(f"=== BCC950 MUTE {VERSION} ===")

class Estado:
    def __init__(self):
        self.muted = False
        self.encontrado = False
        self.nombre = ""
        self._lock = threading.Lock()
    def toggle(self):
        with self._lock:
            self.muted = not self.muted
            return self.muted
    def get(self):
        with self._lock:
            return self.muted

estado = Estado()

def monitor():
    log("Monitor HID iniciado")
    while True:
        try:
            targets = [d for d in hid.find_all_hid_devices()
                       if d.vendor_id == LOGITECH_VID and d.product_id in LOGITECH_PIDS]
            if not targets:
                estado.encontrado = False
                time.sleep(2)
                continue

            for dev in targets:
                try:
                    dev.open()
                    tiene = any(TARGET_USAGE in rep.keys()
                                for rep in dev.find_input_reports())
                    if not tiene:
                        dev.close()
                        continue

                    estado.encontrado = True
                    estado.nombre = dev.product_name or "BCC950"
                    log(f"Escuchando: {estado.nombre} (usage 0x{TARGET_USAGE:08X})")

                    ultimo_flanco = [0.0]

                    def handler(value, event_kind):
                        # Solo actuamos cuando el botón se PRESIONA (value=1).
                        # El evento de soltado (value=0) llega siempre detrás
                        # y lo ignoramos.
                        if value != 1:
                            return
                        ahora = time.time()
                        if ahora - ultimo_flanco[0] < DEBOUNCE_SECONDS:
                            return  # Debounce
                        ultimo_flanco[0] = ahora
                        nuevo = estado.toggle()
                        log(f"*** Pulsación *** -> {'MUTE' if nuevo else 'ACTIVO'}")

                    dev.add_event_handler(TARGET_USAGE, handler, hid.HID_EVT_ALL)
                    log("Handler registrado. Pulsa el botón de mute de la BCC950...")

                    while dev.is_plugged():
                        time.sleep(0.2)
                    dev.close()
                except Exception as e:
                    log(f"Error con dispositivo: {e}")
                    traceback.print_exc()
                    try: dev.close()
                    except Exception: pass

            estado.encontrado = False
            time.sleep(1)
        except Exception:
            log(traceback.format_exc())
            time.sleep(3)

class Overlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.94)
        self.label = tk.Label(self.root, text="Buscando BCC950...",
                              font=("Segoe UI", 16, "bold"),
                              fg="white", bg="#616161", padx=20, pady=10)
        self.label.pack()
        self.label.bind("<ButtonPress-1>", self._sd)
        self.label.bind("<B1-Motion>", self._dr)
        self.label.bind("<Button-3>", lambda e: self.root.destroy())
        self.root.update_idletasks()
        w = self.root.winfo_reqwidth(); sw = self.root.winfo_screenwidth()
        self.root.geometry(f"+{(sw - w) // 2}+20")
        self.ultimo = None
        self.tick()

    def _sd(self, e): self._x, self._y = e.x, e.y
    def _dr(self, e):
        self.root.geometry(f"+{self.root.winfo_x() + e.x - self._x}"
                          f"+{self.root.winfo_y() + e.y - self._y}")

    def tick(self):
        if not estado.encontrado:
            t, c = "BCC950 no detectada", "#616161"
        elif estado.get():
            t, c = "MICRÓFONO BCC950 MUTEADO", "#c62828"
        else:
            t, c = "MICRÓFONO BCC950 ACTIVO", "#2e7d32"
        if t != self.ultimo:
            self.label.config(text=t, bg=c)
            self.ultimo = t
        self.root.after(200, self.tick)

    def run(self): self.root.mainloop()

if __name__ == "__main__":
    threading.Thread(target=monitor, daemon=True).start()
    try:
        Overlay().run()
    except Exception:
        log(traceback.format_exc())
        raise