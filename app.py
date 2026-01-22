from flask import Flask, render_template, request, send_file, after_this_request
import yt_dlp
import os
import glob
import time

app = Flask(__name__)

# Configura pasta temporária
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'downloads_tmp')
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    video_link = data.get('url')
    formato = data.get('format')

    if not video_link:
        return {'error': 'Link não fornecido'}, 400

    limpar_downloads_antigos()

    try:
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'restrictfilenames': True,
        }

        # Lógica de Cookies Inteligente
        cookie_file = os.path.join(os.getcwd(), 'cookies.txt')
        
        # 1. Se existir o arquivo cookies.txt (no PC ou Servidor), usa ele
        if os.path.exists(cookie_file):
            ydl_opts['cookiefile'] = cookie_file
        # 2. Se NÃO tiver arquivo E estivermos no Windows (PC Local), tenta usar o navegador
        # (Render roda em Linux, então isso evita o erro lá)
        elif os.name == 'nt': 
            ydl_opts['cookiesfrombrowser'] = ('chrome',)

        if formato == 'video':
            ydl_opts['format'] = 'best[ext=mp4][protocol^=http]/best[ext=mp4]/best'
        else:
            ydl_opts['format'] = 'bestaudio/best'

        info_dict = None
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_link, download=True)
            filename = ydl.prepare_filename(info_dict)

        # Fallback para encontrar o arquivo caso o nome mude ligeiramente
        if not os.path.exists(filename):
            list_of_files = glob.glob(os.path.join(DOWNLOAD_FOLDER, '*'))
            if list_of_files:
                filename = max(list_of_files, key=os.path.getctime)

        @after_this_request
        def remove_file(response):
            try:
                if os.path.exists(filename):
                    os.remove(filename)
            except Exception as e:
                print(f"Erro ao limpar: {e}")
            return response

        return send_file(filename, as_attachment=True, download_name=os.path.basename(filename))

    except Exception as e:
        print(f"Erro: {e}")
        return {'error': str(e)}, 500

def limpar_downloads_antigos():
    now = time.time()
    try:
        if os.path.exists(DOWNLOAD_FOLDER):
            for f in os.listdir(DOWNLOAD_FOLDER):
                path = os.path.join(DOWNLOAD_FOLDER, f)
                if os.stat(path).st_mtime < now - 600: # 10 minutos
                    os.remove(path)
    except:
        pass

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
