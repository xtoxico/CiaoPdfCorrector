import os
import io
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from dataclasses import dataclass

# Dependencias
# pip install PyMuPDF Pillow
import fitz  # PyMuPDF
from PIL import Image, ImageOps, ImageStat


@dataclass
class ProcessOptions:
    dpi: int = 200
    force_invert: bool = False
    auto_detect_invert: bool = True
    grayscale: bool = False


def render_page_to_pil(page, dpi=200, white_bg=True):
    """
    Renderiza una página de PDF a una imagen PIL.
    Si white_bg=True, renderiza sin canal alpha (fondo blanco).
    """
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=not white_bg)  # alpha=False => fondo blanco
    mode = "RGBA" if pix.alpha else "RGB"
    img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)

    if img.mode == "RGBA":
        # Componer sobre blanco
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1])
        img = bg
    else:
        img = img.convert("RGB")
    return img


def is_dark_page(img: Image) -> bool:
    """
    Heurística sencilla: calcula luminancia media y decide si la página es 'oscura'.
    """
    # Convertir a luminosity (L) para estimar brillo
    gray = img.convert("L")
    stat = ImageStat.Stat(gray)
    mean = stat.mean[0]  # 0..255
    # Umbral conservador: < 120 se considera "oscura"
    return mean < 120


def process_pdf(input_path: str, output_path: str, opts: ProcessOptions):
    with fitz.open(input_path) as doc:
        out = fitz.open()  # nuevo PDF
        for i, page in enumerate(doc):
            img = render_page_to_pil(page, dpi=opts.dpi, white_bg=True)

            # Decidir si invertimos
            invert_this = False
            if opts.force_invert:
                invert_this = True
            elif opts.auto_detect_invert:
                invert_this = is_dark_page(img)

            if invert_this:
                img = ImageOps.invert(img)

            if opts.grayscale:
                img = img.convert("L").convert("RGB")

            # Insertar la imagen como página del nuevo PDF con el mismo tamaño "real"
            # Creamos nueva página con el tamaño original del PDF (en puntos)
            rect = page.rect
            new_page = out.new_page(width=rect.width, height=rect.height)

            # Para escalar la imagen renderizada (en px) a puntos, usamos factor: puntos = px * (72/dpi)
            img_width_pt = img.width * (72.0 / opts.dpi)
            img_height_pt = img.height * (72.0 / opts.dpi)

            # Centramos la imagen escalada a toda página
            # (normalmente coincide casi exacto si mantuvimos el ratio)
            bbox = fitz.Rect(0, 0, img_width_pt, img_height_pt)

            # Exportamos la imagen a bytes (JPEG para tamaño razonable)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=95, optimize=True)
            img_bytes = buf.getvalue()

            # Insertamos la imagen ocupando toda la página
            new_page.insert_image(bbox, stream=img_bytes)

        out.save(output_path)
        out.close()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Corrector de moñeces de los PDFs del ciao para impresión")
        self.geometry("520x260")
        self.resizable(False, False)

        self.input_path = tk.StringVar()
        self.dpi = tk.IntVar(value=200)
        self.force_invert = tk.BooleanVar(value=False)
        self.auto_detect_invert = tk.BooleanVar(value=True)
        self.grayscale = tk.BooleanVar(value=False)

        self.create_widgets()

    def create_widgets(self):
        pad = {"padx": 12, "pady": 8}

        frm_top = ttk.Frame(self)
        frm_top.pack(fill="x", **pad)

        ttk.Label(frm_top, text="Ciaooooo elige el PDF:").pack(anchor="w")
        row = ttk.Frame(frm_top)
        row.pack(fill="x", pady=4)
        entry = ttk.Entry(row, textvariable=self.input_path, width=58)
        entry.pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Elegir...", command=self.choose_file).pack(side="left", padx=6)

        frm_opts = ttk.LabelFrame(self, text="Opciones")
        frm_opts.pack(fill="x", **pad)

        # DPI
        dpi_row = ttk.Frame(frm_opts)
        dpi_row.pack(fill="x", pady=4, padx=8)
        ttk.Label(dpi_row, text="Resolución (DPI):").pack(side="left")
        dpi_entry = ttk.Spinbox(dpi_row, from_=96, to=600, increment=4, textvariable=self.dpi, width=6)
        dpi_entry.pack(side="left", padx=8)

        # Checkboxes
        chk_row = ttk.Frame(frm_opts)
        chk_row.pack(fill="x", pady=4, padx=8)
        ttk.Checkbutton(chk_row, text="Detectar e invertir automáticamente páginas oscuras", variable=self.auto_detect_invert).pack(anchor="w")
        ttk.Checkbutton(chk_row, text="Forzar invertir colores (todas las páginas)", variable=self.force_invert).pack(anchor="w")
        ttk.Checkbutton(chk_row, text="Convertir a escala de grises", variable=self.grayscale).pack(anchor="w")

        # Botón procesar
        frm_bottom = ttk.Frame(self)
        frm_bottom.pack(fill="x", **pad)
        ttk.Button(frm_bottom, text="Generar PDF corregido", command=self.run_process).pack(side="left")

        # Ayuda
        help_text = (
            "Sugerencia:\n"
            "- Si tu PDF sale con fondo negro al imprimir, prueba SOLO con 'Detectar e invertir'.\n"
            "- Si sigue igual, marca 'Forzar invertir colores'.\n"
            "- 'Escala de grises' reduce tinta y evita mezclas raras."
        )
        ttk.Label(self, text=help_text, foreground="#444").pack(anchor="w", padx=14)

    def choose_file(self):
        path = filedialog.askopenfilename(
            title="Selecciona un PDF",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        if path:
            self.input_path.set(path)

    def run_process(self):
        in_path = self.input_path.get().strip()
        if not in_path or not os.path.isfile(in_path):
            messagebox.showerror("Error", "Selecciona un archivo PDF válido.")
            return

        base, ext = os.path.splitext(in_path)
        out_path = base + "_corregido.pdf"

        opts = ProcessOptions(
            dpi=self.dpi.get(),
            force_invert=self.force_invert.get(),
            auto_detect_invert=self.auto_detect_invert.get(),
            grayscale=self.grayscale.get()
        )

        try:
            self.disable_ui()
            self.update_idletasks()
            process_pdf(in_path, out_path, opts)
            messagebox.showinfo("Listo", f"PDF generado:\n{out_path}")
            # Ofrecer abrir carpeta
            try:
                if os.name == "nt":
                    os.startfile(os.path.dirname(out_path) or ".")
                elif os.name == "posix":
                    # macOS o Linux
                    folder = os.path.dirname(out_path) or "."
                    if "darwin" in os.sys.platform:
                        os.system(f'open "{folder}"')
                    else:
                        os.system(f'xdg-open "{folder}"')
            except Exception:
                pass
        except RuntimeError as e:
            messagebox.showerror("Error", f"No se pudo procesar el PDF.\nDetalle: {e}")
        except Exception as e:
            messagebox.showerror("Error inesperado", f"Ocurrió un error: {e}")
        finally:
            self.enable_ui()

    def disable_ui(self):
        for child in self.winfo_children():
            try:
                child.configure(state="disabled")
            except tk.TclError:
                pass

    def enable_ui(self):
        for child in self.winfo_children():
            try:
                child.configure(state="normal")
            except tk.TclError:
                pass


if __name__ == "__main__":
    app = App()
    app.mainloop()
