# bacbo_gui.py
"""
VT BACBO ANALYZER - GUI
- Load screenshot (manual)
- Crop and OCR area for result
- Confirm result (Jogador/Banca/Empate)
- Save to SQLite
- Simple analysis (runs, transitions)
- Telegram notifications via telegramer.py (config.ini)
"""

import os
import io
import sqlite3
import configparser
import threading
from datetime import datetime
from tkinter import (
    Tk, Frame, Button, Label, PhotoImage, Canvas, NW, filedialog, messagebox, Toplevel, StringVar
)
from PIL import Image, ImageTk, ImageOps
from analyzer import StatsAnalyzer
from ocr_reader import OCRReader
from telegramer import Telegramer

# Files
CONFIG_FILE = "config.ini"
DB_FILE = "bacbo_history.db"
EXPORT_CSV = "bacbo_history_export.csv"

# Load config (create template if missing)
DEFAULT_CONFIG = {
    "telegram": {"token": "SEU_TOKEN_AQUI", "chat_id": "SEU_CHAT_ID_AQUI"},
    "ocr": {"tesseract_cmd": ""}
}

config = configparser.ConfigParser()
if not os.path.exists(CONFIG_FILE):
    config.read_dict(DEFAULT_CONFIG)
    with open(CONFIG_FILE, "w") as f:
        config.write(f)
else:
    config.read(CONFIG_FILE)

# Setup components
ocr_reader = OCRReader(config)
tg = Telegramer(config)

# DB init
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS rounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            result TEXT,
            image BLOB
        )
        """
    )
    conn.commit()
    conn.close()


class BacBoApp:
    def __init__(self, root):
        self.root = root
        root.title("VT BACBO ANALYZER")
        root.geometry("1100x720")
        root.configure(bg="#0b0f14")

        # Header
        header = Frame(root, bg="#061018", height=80)
        header.pack(fill="x")
        logo_path = "logo.png"
        if os.path.exists(logo_path):
            try:
                self.logo_img = PhotoImage(file=logo_path)
                Label(header, image=self.logo_img, bg="#061018").pack(side="left", padx=12, pady=6)
            except Exception:
                Label(header, text="VT BACBO ANALYZER", fg="#66f0ff", bg="#061018", font=("Inter", 20, "bold")).pack(side="left", padx=12)
        else:
            Label(header, text="VT BACBO ANALYZER", fg="#66f0ff", bg="#061018", font=("Inter", 20, "bold")).pack(side="left", padx=12)

        # Main layout: left controls, right stats
        main = Frame(root, bg="#0b0f14")
        main.pack(fill="both", expand=True, padx=12, pady=12)

        left = Frame(main, bg="#0b0f14", width=680)
        left.pack(side="left", fill="both", expand=True)

        right = Frame(main, bg="#071018", width=380)
        right.pack(side="right", fill="y")

        # Left: image canvas + controls
        self.canvas = Canvas(left, bg="#041018", width=640, height=480)
        self.canvas.pack(padx=8, pady=8)
        self.current_image = None
        self.cropped = None

        btn_frame = Frame(left, bg="#0b0f14")
        btn_frame.pack(fill="x", padx=8)

        Button(btn_frame, text="Carregar Print...", command=self.load_image, width=14).pack(side="left", padx=6, pady=6)
        Button(btn_frame, text="Selecionar Área (crop)", command=self.crop_image, width=18).pack(side="left", padx=6)
        Button(btn_frame, text="Detectar OCR", command=self.detect_ocr, width=14).pack(side="left", padx=6)
        Button(btn_frame, text="Exportar CSV", command=self.export_csv, width=12).pack(side="left", padx=6)

        confirm_frame = Frame(left, bg="#0b0f14")
        confirm_frame.pack(fill="x", padx=8, pady=(6,0))
        Label(confirm_frame, text="Confirmar Resultado:", fg="#c7f1ff", bg="#0b0f14").pack(side="left", padx=6)
        Button(confirm_frame, text="Jogador (P)", command=lambda: self.save_result("P"), bg="#1b8fbd", fg="white").pack(side="left", padx=6)
        Button(confirm_frame, text="Banca (B)", command=lambda: self.save_result("B"), bg="#bd4141", fg="white").pack(side="left", padx=6)
        Button(confirm_frame, text="Empate (T)", command=lambda: self.save_result("T"), bg="#9b8fbd", fg="white").pack(side="left", padx=6)

        # Status
        self.status_var = StringVar()
        self.status_var.set("Pronto")
        Label(left, textvariable=self.status_var, fg="#bcd", bg="#0b0f14").pack(anchor="w", padx=10, pady=(6,0))

        # Right: stats panel
        Label(right, text="Painel de Padrões", fg="#66f0ff", bg="#071018", font=("Inter", 14, "bold")).pack(padx=8, pady=(12,6))
        self.stats_text = Label(right, text="— sem dados —", justify="left", fg="#d5f7ff", bg="#071018")
        self.stats_text.pack(fill="both", padx=8, pady=8)

        Label(right, text="Últimos Resultados", fg="#9be7ff", bg="#071018").pack(padx=8)
        self.last_text = Label(right, text="", fg="#fff", bg="#071018", justify="left")
        self.last_text.pack(fill="x", padx=8, pady=(0,8))

        Label(right, text="Config Telegram", fg="#9be7ff", bg="#071018").pack(padx=8, pady=(12,0))
        Button(right, text="Testar Telegram", command=self.test_telegram, fg="#071018").pack(padx=8, pady=8)

        init_db()
        self.analyzer = StatsAnalyzer(DB_FILE)
        self.refresh_ui()

    # ---------------- UI actions ----------------
    def set_status(self, text):
        self.status_var.set(text)

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("PNG/JPG", "*.png;*.jpg;*.jpeg;*.bmp")])
        if not path:
            return
        img = Image.open(path).convert("RGB")
        self.current_image = img
        # fit to canvas
        w,h = img.size
        maxw,maxh = 640,480
        ratio = min(maxw/w, maxh/h, 1.0)
        disp = img.resize((int(w*ratio), int(h*ratio)), Image.LANCZOS)
        self.tkimg = ImageTk.PhotoImage(disp)
        self.canvas.delete("all")
        self.canvas.create_image(0,0,anchor=NW,image=self.tkimg)
        self.set_status(f"Imagem carregada: {os.path.basename(path)}")

    def crop_image(self):
        if self.current_image is None:
            messagebox.showwarning("Atenção", "Carregue uma imagem primeiro.")
            return
        CropWindow(self.root, self.current_image, self.on_cropped)

    def on_cropped(self, pil_img):
        self.cropped = pil_img
        disp = pil_img.resize((480,200), Image.LANCZOS)
        self.tk_crop = ImageTk.PhotoImage(disp)
        self.canvas.create_image(10,10,anchor=NW,image=self.tk_crop, tags="crop_preview")
        self.set_status("Área selecionada. Use Detectar OCR ou confirme manualmente.")

    def detect_ocr(self):
        if self.cropped is None:
            messagebox.showwarning("Atenção", "Selecione a área primeiro.")
            return
        txt = ocr_reader.image_to_text(self.cropped)
        messagebox.showinfo("OCR", f"Texto detectado:\n{txt}")
        self.set_status("OCR executado")

    def save_result(self, result):
        # Save result with cropped image
        img_blob = None
        if self.cropped:
            bio = io.BytesIO()
            self.cropped.save(bio, format="PNG")
            img_blob = bio.getvalue()
        ts = datetime.utcnow().isoformat()
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("INSERT INTO rounds (ts, result, image) VALUES (?,?,?)", (ts, result, img_blob))
        conn.commit()
        conn.close()
        self.set_status(f"Resultado salvo: {result} ({ts})")
        self.analyzer.refresh()
        self.refresh_ui()
        # notifications: background thread
        threading.Thread(target=self.post_save_actions, args=(result,)).start()

    def post_save_actions(self, last_result):
        stats = self.analyzer.compute_stats()
        # run detection
        run_info = self.analyzer.check_run()
        if run_info and run_info["length"] >= 4:
            tg.send_message(f"🔥 RUN DETECTADO: {run_info['result']} x{run_info['length']}")
        # always send small summary
        summary = self.analyzer.summary_text()
        tg.send_message(summary)

    def refresh_ui(self):
        last = self.analyzer.last_n(20)
        self.last_text.config(text=" ".join(last[::-1]))
        stats = self.analyzer.compute_stats()
        txt = "\n".join(f"{k}: {v}" for k,v in stats.items())
        self.stats_text.config(text=txt)

    def export_csv(self):
        df = self.analyzer.to_dataframe()
        df.to_csv(EXPORT_CSV, index=False)
        messagebox.showinfo("Exportar", f"Exportado: {EXPORT_CSV}")

    def test_telegram(self):
        ok = tg.send_message("VT BacBo Analyzer: teste de notificação")
        messagebox.showinfo("Telegram", "Mensagem enviada!" if ok else "Falha ao enviar. Verifique config.ini.")


class CropWindow(Toplevel):
    def __init__(self, master, pil_image, callback):
        super().__init__(master)
        self.title("Selecionar área")
        self.callback = callback
        self.img = pil_image
        self.canvas = Canvas(self, width=800, height=500, cursor="cross")
        self.canvas.pack()
        w,h = self.img.size
        ratio = min(800/w, 500/h, 1.0)
        self.display = self.img.resize((int(w*ratio), int(h*ratio)), Image.LANCZOS)
        self.tkdisplay = ImageTk.PhotoImage(self.display)
        self.canvas.create_image(0,0,anchor=NW,image=self.tkdisplay)
        self.start = None
        self.rect = None
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        btn = Button(self, text="Confirmar Corte", command=self.confirm)
        btn.pack(pady=6)

    def on_press(self, e):
        self.start = (e.x, e.y)
        if self.rect:
            self.canvas.delete(self.rect)
            self.rect = None

    def on_move(self, e):
        if not self.start:
            return
        x0,y0 = self.start
        self.rect = self.canvas.create_rectangle(x0,y0,e.x,e.y,outline="red")

    def on_release(self, e):
        pass

    def confirm(self):
        if not self.rect:
            messagebox.showwarning("Atenção", "Selecione a área primeiro.")
            return
        coords = self.canvas.coords(self.rect)  # x0,y0,x1,y1 in display coords
        x0,y0,x1,y1 = map(int, coords)
        # map back to original image coords
        dw,dh = self.display.size
        ow,oh = self.img.size
        rx = ow / dw
        ry = oh / dh
        crop = self.img.crop((int(x0*rx), int(y0*ry), int(x1*rx), int(y1*ry)))
        self.callback(crop)
        self.destroy()


if __name__ == "__main__":
    root = Tk()
    app = BacBoApp(root)
    root.mainloop()
