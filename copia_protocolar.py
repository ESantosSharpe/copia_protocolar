#!/usr/bin/env python3
"""
copia_protocolar.py
===================
Genera copias protocolares de PDFs para IGJ.

Márgenes:
  - Páginas impares : 8 cm a la IZQUIERDA
  - Páginas pares   : 8 cm a la DERECHA
  - Resto de márgenes: 1,5 cm
  - Imagen alineada al tope de la hoja
  - Contenido tratado como imagen (sin manipulación de texto)

Tamaños de hoja:
  - A4    : 21,0 × 29,7 cm
  - Oficio: 21,59 × 33,02 cm

Uso CLI:
  python copia_protocolar.py input.pdf --hoja a4
  python copia_protocolar.py input.pdf --hoja oficio
  python copia_protocolar.py input.pdf           # por defecto: A4

Uso GUI:
  python copia_protocolar.py
"""

import argparse
import io
import os
import sys

# ---------------------------------------------------------------------------
# Lógica principal (sin dependencias de UI)
# ---------------------------------------------------------------------------

def generar_copia_protocolar(input_path: str, output_path: str, hoja: str = "a4") -> int:
    """
    Genera la copia protocolar.
    Devuelve la cantidad de páginas procesadas.
    Lanza excepciones ante errores.
    """
    from pdf2image import convert_from_path
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.lib.units import cm
    from reportlab.lib.utils import ImageReader

    HOJAS = {
        "a4":     (21.0  * cm, 29.7  * cm),
        "oficio": (21.59 * cm, 33.02 * cm),
    }

    hoja = hoja.lower()
    if hoja not in HOJAS:
        raise ValueError(f"Hoja inválida: '{hoja}'. Usá 'a4' u 'oficio'.")

    PAGE_W, PAGE_H = HOJAS[hoja]
    MARGEN_PROTO  = 8.0 * cm
    MARGEN_CHICO  = 1.5 * cm

    pages = convert_from_path(input_path, dpi=200)
    c = rl_canvas.Canvas(output_path, pagesize=(PAGE_W, PAGE_H))

    for i, img in enumerate(pages):
        page_num = i + 1

        if page_num % 2 == 1:          # impar → margen grande a la izquierda
            x_offset = MARGEN_PROTO
        else:                           # par   → margen grande a la derecha
            x_offset = MARGEN_CHICO

        avail_w = PAGE_W - MARGEN_PROTO - MARGEN_CHICO
        avail_h = PAGE_H - 2 * MARGEN_CHICO

        img_w, img_h = img.size
        scale  = min(avail_w / img_w, avail_h / img_h)
        draw_w = img_w * scale
        draw_h = img_h * scale

        # Alineado al tope
        y_offset = PAGE_H - MARGEN_CHICO - draw_h

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        c.drawImage(ImageReader(buf), x_offset, y_offset,
                    width=draw_w, height=draw_h)
        c.showPage()

    c.save()
    return len(pages)


def output_path_from_input(input_path: str, hoja: str) -> str:
    base, _ = os.path.splitext(input_path)
    return f"{base}_protocolar_{hoja}.pdf"


# ---------------------------------------------------------------------------
# Interfaz CLI
# ---------------------------------------------------------------------------

def cli():
    parser = argparse.ArgumentParser(
        description="Genera copia protocolar de un PDF para IGJ."
    )
    parser.add_argument("input", help="PDF de entrada")
    parser.add_argument(
        "--hoja",
        choices=["a4", "oficio"],
        default="a4",
        help="Tamaño de hoja destino (default: a4)",
    )
    parser.add_argument(
        "--salida",
        default=None,
        help="Ruta del PDF de salida (opcional)",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: no se encontró el archivo '{args.input}'")
        sys.exit(1)

    output = args.salida or output_path_from_input(args.input, args.hoja)

    print(f"Procesando '{args.input}' → '{output}' (hoja: {args.hoja.upper()})...")
    try:
        n = generar_copia_protocolar(args.input, output, args.hoja)
        print(f"✓ Listo. {n} página(s) generada(s).")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Interfaz GUI (tkinter)
# ---------------------------------------------------------------------------

def gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    root = tk.Tk()
    root.title("Copia Protocolar — IGJ")
    root.resizable(False, False)

    # ── Variables ──────────────────────────────────────────────────────────
    var_input  = tk.StringVar()
    var_output = tk.StringVar()
    var_hoja   = tk.StringVar(value="a4")

    # ── Helpers ────────────────────────────────────────────────────────────
    def browse_input():
        path = filedialog.askopenfilename(
            title="Seleccionar PDF de entrada",
            filetypes=[("Archivos PDF", "*.pdf")],
        )
        if path:
            var_input.set(path)
            if not var_output.get():
                var_output.set(output_path_from_input(path, var_hoja.get()))

    def browse_output():
        path = filedialog.asksaveasfilename(
            title="Guardar copia protocolar como…",
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf")],
        )
        if path:
            var_output.set(path)

    def on_hoja_change(*_):
        inp = var_input.get()
        if inp:
            var_output.set(output_path_from_input(inp, var_hoja.get()))

    def procesar():
        inp = var_input.get().strip()
        out = var_output.get().strip()

        if not inp:
            messagebox.showwarning("Falta archivo", "Seleccioná el PDF de entrada.")
            return
        if not os.path.isfile(inp):
            messagebox.showerror("Archivo no encontrado", f"No se encontró:\n{inp}")
            return
        if not out:
            messagebox.showwarning("Falta destino", "Especificá dónde guardar el resultado.")
            return

        btn_procesar.config(state="disabled", text="Procesando…")
        root.update_idletasks()

        try:
            n = generar_copia_protocolar(inp, out, var_hoja.get())
            messagebox.showinfo(
                "¡Listo!",
                f"Copia protocolar generada correctamente.\n\n"
                f"Páginas: {n}\n"
                f"Hoja: {var_hoja.get().upper()}\n\n"
                f"Guardado en:\n{out}",
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            btn_procesar.config(state="normal", text="Generar copia protocolar")

    # ── Layout ─────────────────────────────────────────────────────────────
    PAD = dict(padx=10, pady=6)

    frame = ttk.Frame(root, padding=16)
    frame.grid(sticky="nsew")

    # Título
    ttk.Label(
        frame,
        text="Generador de Copias Protocolares",
        font=("", 13, "bold"),
    ).grid(row=0, column=0, columnspan=3, pady=(0, 12))

    # PDF entrada
    ttk.Label(frame, text="PDF de entrada:").grid(row=1, column=0, sticky="e", **PAD)
    ttk.Entry(frame, textvariable=var_input, width=48).grid(row=1, column=1, **PAD)
    ttk.Button(frame, text="…", width=3, command=browse_input).grid(row=1, column=2, **PAD)

    # PDF salida
    ttk.Label(frame, text="Guardar como:").grid(row=2, column=0, sticky="e", **PAD)
    ttk.Entry(frame, textvariable=var_output, width=48).grid(row=2, column=1, **PAD)
    ttk.Button(frame, text="…", width=3, command=browse_output).grid(row=2, column=2, **PAD)

    # Tamaño de hoja
    ttk.Label(frame, text="Tamaño de hoja:").grid(row=3, column=0, sticky="e", **PAD)
    hoja_frame = ttk.Frame(frame)
    hoja_frame.grid(row=3, column=1, sticky="w", **PAD)
    ttk.Radiobutton(
        hoja_frame, text="A4  (21 × 29,7 cm)",
        variable=var_hoja, value="a4", command=on_hoja_change,
    ).pack(side="left", padx=(0, 20))
    ttk.Radiobutton(
        hoja_frame, text="Oficio  (21,59 × 33,02 cm)",
        variable=var_hoja, value="oficio", command=on_hoja_change,
    ).pack(side="left")

    # Info márgenes
    info = (
        "Margen protocolar: 8 cm  |  "
        "Páginas impares: margen izquierdo  |  "
        "Páginas pares: margen derecho"
    )
    ttk.Label(frame, text=info, foreground="gray").grid(
        row=4, column=0, columnspan=3, pady=(0, 10)
    )

    # Separador
    ttk.Separator(frame, orient="horizontal").grid(
        row=5, column=0, columnspan=3, sticky="ew", pady=4
    )

    # Botón principal
    btn_procesar = ttk.Button(frame, text="Generar copia protocolar", command=procesar)
    btn_procesar.grid(row=6, column=0, columnspan=3, pady=(10, 0), ipadx=10, ipady=4)

    root.mainloop()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Si hay argumentos posicionales → CLI; si no → GUI
    if len(sys.argv) > 1:
        cli()
    else:
        gui()
