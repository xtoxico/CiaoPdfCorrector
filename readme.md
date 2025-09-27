# Corrector de PDFs del Ciaooo 🐶📚

Un buen amigo mío me escribió desesperado:  
Estudiando en la UNED, cada vez que intentaba imprimir sus apuntes el PDF salía con **fondo negro y letras blancas**, lo que hacía el gasto de tinta imposible y los apuntes casi ilegibles en papel.  

De esa necesidad nació este pequeño proyecto: un **corrector de PDFs** que invierte los colores, aplana transparencias y genera un documento nuevo, limpio y listo para imprimir.

---

## ✨ Características
- 📂 **Abrir cualquier PDF** desde una interfaz gráfica sencilla.  
- 🖼️ **Detección automática** de páginas con fondo negro → las corrige a blanco con texto oscuro.  
- ⚙️ Opciones avanzadas:
  - Forzar inversión de colores en todas las páginas.
  - Convertir a escala de grises para ahorrar tinta.
  - Ajustar resolución (DPI).  
- 💾 **Guardar un nuevo PDF corregido** junto al original.  
- ✅ Compatible con Windows, macOS y Linux (ejecutable incluido para Windows).

---

## 🚀 Instalación desde código
1. Clona el repo:
   ```bash
   git clone https://github.com/tuusuario/corrector-pdfs-ciaooo.git
   cd corrector-pdfs-ciaooo


Crea el entorno e instala dependencias:

python -m venv .venv
.\.venv\Scripts\activate  # en Windows
source .venv/bin/activate # en Linux/Mac

pip install -r requirements.txt


Ejecuta la app:

python pdf_fix_gui.py

🖥️ Ejecutable en Windows

Si no quieres instalar nada, también puedes generar un .exe:

pyinstaller --windowed --onefile --name PDFFix --icon PDFFix.ico pdf_fix_gui.py


El ejecutable aparecerá en la carpeta dist/.

📖 Uso

Abre la app y pulsa “Elegir…” para seleccionar tu PDF.

Activa las opciones que prefieras:

Detectar e invertir automáticamente (recomendado).

Forzar invertir colores si no se corrige bien.

Escala de grises para imprimir barato.

Pulsa “Generar PDF corregido”.

¡Listo! Encontrarás un archivo *_corregido.pdf en la misma carpeta.

🛠️ Tecnologías

Python 3.13

Tkinter
 – interfaz gráfica

PyMuPDF (fitz)
 – renderizado de PDF

Pillow
 – procesamiento de imágenes

PyInstaller
 – creación de ejecutables

💡 Inspiración

Este proyecto no es solo código: es un ejemplo de cómo un problema cotidiano (imprimir unos apuntes para estudiar) puede resolverse con un poco de programación y cariño.


📜 Licencia

MIT License.
Libre para usar, modificar y compartir.