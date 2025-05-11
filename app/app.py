# app/app.py

from flask import Flask, send_from_directory, render_template, send_file
import socket
import qrcode
import os
import urllib.parse

app = Flask(__name__, template_folder='static/templates', static_folder='static')
username_os = os.getlogin()

ROOT_DIR = os.path.abspath(f"C:/Users/{username_os}")  # ou os.getcwd() para raiz do projeto


# 🧠 Detectar IP local da máquina
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Conecta com IP externo para forçar uso da interface correta
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

@app.route('/')
def index():
    return render_template('index.html')  # Exibe o HTML da pasta templates


@app.route('/dashboard', defaults={'req_path': ''})
@app.route('/dashboard/<path:req_path>')
def dashboard(req_path):
    abs_path = os.path.join(ROOT_DIR, req_path)
    abs_path = os.path.abspath(abs_path)

    # Proteção contra tentativa de acessar fora da raiz
    if not abs_path.startswith(ROOT_DIR):
        return "Acesso negado.", 403

    # Se for um arquivo, faz download
    if os.path.isfile(abs_path):
        return send_file(abs_path, as_attachment=True)

    # Se for uma pasta, lista conteúdo
    files = []
    dirs = []

    try:
        for entry in os.listdir(abs_path):
            full_path = os.path.join(abs_path, entry)
            encoded_path = urllib.parse.quote(os.path.relpath(full_path, ROOT_DIR).replace("\\", "/"))

            if os.path.isdir(full_path):
                dirs.append((entry, encoded_path))
            else:
                files.append((entry, encoded_path))
    except PermissionError:
        return "Permissão negada.", 403

    # Caminho para voltar
    parent_path = os.path.relpath(os.path.dirname(abs_path), ROOT_DIR)
    back_url = urllib.parse.quote(parent_path.replace("\\", "/")) if parent_path != "." else ""

    return render_template("dashboard.html", dirs=dirs, files=files, back_url=back_url)

@app.route('/download/<path:filename>')
def download_file(filename):
    # Faz download de arquivos da pasta upload
    return send_from_directory('static/upload', filename, as_attachment=True)

if __name__ == '__main__':
    ip = get_local_ip()
    port = 5000
    url = f"http://{ip}:{port}/dashboard"

    # ✅ Gerar QR Code para acesso via celular
    qr = qrcode.make(url)
    qr_path = "app/static/qrcode.png"
    qr.save(qr_path)
    print(f"\nAcesse com seu celular: {url}")
    print(f"Ou escaneie o QR Code salvo em: {qr_path}\n")

    app.run(host='0.0.0.0', port=port)
