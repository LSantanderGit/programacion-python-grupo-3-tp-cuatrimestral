"""Servidor web local para visualizar el Dashboard interactivo de resultados.

Levanta un servidor HTTP local ligero con la biblioteca estandar de Python y
dispara la apertura automatica del dashboard en el navegador predeterminado.
"""

import http.server
import socketserver
import webbrowser
from pathlib import Path

from scripts.make_dashboard import generate_dashboard_html


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """Manejador HTTP silencioso para evitar saturar la consola con logs de assets."""

    def log_message(self, format: str, *args: object) -> None:
        pass


def get_available_port(start_port: int = 8000, max_attempts: int = 50) -> int:
    """Encuentra un puerto disponible comenzando desde start_port."""
    import socket

    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return start_port


def serve_dashboard(port: int | None = None, open_browser: bool = True) -> None:
    """Inicia el servidor local y abre el dashboard en el navegador."""
    raw_dir = Path("results/raw")
    dashboard_file = Path("results/dashboard.html")

    # Asegurar que el dashboard exista
    if not dashboard_file.exists():
        print("-> Dashboard no encontrado. Generando desde results/raw/...")
        generate_dashboard_html(raw_dir, dashboard_file)

    target_port = port or get_available_port(8000)
    url = f"http://localhost:{target_port}/results/dashboard.html"

    print("\n" + "=" * 70)
    print("               SERVIDOR DE DASHBOARD WEB LOCAL")
    print("=" * 70)
    print(f"-> Servidor activo en: {url}")
    print("-> Presione Ctrl+C en esta terminal para detener el servidor.")
    print("=" * 70 + "\n")

    if open_browser:
        webbrowser.open(url)

    # Iniciar servidor
    try:
        with socketserver.TCPServer(("127.0.0.1", target_port), QuietHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[OK] Servidor detenido por el usuario.")


if __name__ == "__main__":
    serve_dashboard()
