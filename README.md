# copia_protocolar

Script en Python para generar **copias protocolares** de instrumentos en PDF, listas para presentar ante la **IGJ** (o cualquier organismo que exija el formato de margen protocolar de 8 cm).

Convierte cada página del PDF de entrada en una imagen y la vuelca sobre una hoja nueva (A4 u Oficio), dejando el margen ancho alternado según la página sea impar o par, tal como se estila para la encuadernación protocolar.

## Características

- **Márgenes automáticos y alternados:**
  - Páginas impares → 8 cm de margen a la **izquierda**
  - Páginas pares → 8 cm de margen a la **derecha**
  - Resto de márgenes: 1,5 cm
  - Contenido alineado al tope de la hoja
- **Tamaños de hoja disponibles:**
  - A4 (21,0 × 29,7 cm)
  - Oficio (21,59 × 33,02 cm)
- El contenido original se trata como **imagen** (rasterizado a 200 DPI), sin manipular el texto del PDF de origen.
- Dos interfaces de uso: **línea de comandos (CLI)** y **interfaz gráfica (GUI)** con tkinter.

## Requisitos

- Python 3.8+
- Dependencias de Python:
  ```bash
  pip install pdf2image reportlab
  ```
- **Poppler** instalado en el sistema (requerido por `pdf2image` para convertir el PDF a imágenes):
  - **Windows:** descargar los binarios de [poppler para Windows](https://github.com/oschwartz10612/poppler-windows/releases/) y agregar la carpeta `bin` al PATH.
  - **macOS:** `brew install poppler`
  - **Linux (Debian/Ubuntu):** `sudo apt install poppler-utils`

## Uso

### Interfaz gráfica (GUI)

Ejecutar el script sin argumentos abre una ventana de tkinter para elegir el PDF de entrada, el destino y el tamaño de hoja:

```bash
python copia_protocolar.py
```

### Línea de comandos (CLI)

Pasar el PDF como argumento posicional activa el modo CLI:

```bash
python copia_protocolar.py input.pdf --hoja a4
python copia_protocolar.py input.pdf --hoja oficio
python copia_protocolar.py input.pdf
```

Si no se especifica `--hoja`, se usa **A4** por defecto.

#### Argumentos

| Argumento    | Obligatorio | Valores            | Descripción                                                        |
|--------------|:-----------:|---------------------|---------------------------------------------------------------------|
| `input`      | Sí          | ruta a un `.pdf`     | PDF del instrumento a protocolizar                                  |
| `--hoja`     | No          | `a4`, `oficio`       | Tamaño de la hoja de salida (default: `a4`)                          |
| `--salida`   | No          | ruta a un `.pdf`     | Ruta del PDF de salida. Si se omite, se genera automáticamente       |

Si no se indica `--salida`, el archivo de salida se genera junto al de entrada con el sufijo `_protocolar_<hoja>.pdf`, por ejemplo:

```
instrumento.pdf → instrumento_protocolar_a4.pdf
```

## Ejemplo

```bash
python copia_protocolar.py escritura.pdf --hoja oficio --salida escritura_protocolar.pdf
```

Salida esperada:

```
Procesando 'escritura.pdf' → 'escritura_protocolar.pdf' (hoja: OFICIO)...
✓ Listo. 12 página(s) generada(s).
```

## Cómo funciona

1. Convierte cada página del PDF de entrada en una imagen (200 DPI) usando `pdf2image` (Poppler).
2. Calcula el margen ancho (8 cm) a la izquierda en páginas impares y a la derecha en páginas pares, con márgenes chicos de 1,5 cm en el resto de los bordes.
3. Escala la imagen de cada página para que entre en el área disponible, manteniendo la proporción, y la ubica alineada al tope de la hoja.
4. Ensambla todas las páginas en un nuevo PDF con `reportlab`.

## Licencia

Sin licencia especificada.
