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
            # Tenta usar cookies do navegador. 
            # Se usar Chrome e der erro, tente instalar Firefox, logar no YT nele e mudar 'chrome' para 'firefox'
            'cookiesfrombrowser': ('chrome',), 
        }

        # Se o arquivo cookies.txt existir e for válido, usamos ele como prioridade
        cookie_file_path = os.path.join(os.getcwd(), 'cookies.txt')
        if os.path.exists(cookie_file_path):
             ydl_opts['cookiefile'] = cookie_file_path
             if 'cookiesfrombrowser' in ydl_opts:
                 del ydl_opts['cookiesfrombrowser'] # Remove a opção do navegador se o arquivo existe

        if formato == 'video':
            ydl_opts['format'] = 'best[ext=mp4][protocol^=http]/best[ext=mp4]/best'
        else:
            ydl_opts['format'] = 'bestaudio/best'

        info_dict = None
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_link, download=True)
            filename = ydl.prepare_filename(info_dict)

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
                print(f"Erro ao remover arquivo: {e}")
            return response

        return send_file(filename, as_attachment=True, download_name=os.path.basename(filename))

    except Exception as e:
        print(f"Erro no download: {e}")
        return {'error': str(e)}, 500

def limpar_downloads_antigos():
    now = time.time()
    try:
        for f in os.listdir(DOWNLOAD_FOLDER):
            f_path = os.path.join(DOWNLOAD_FOLDER, f)
            if os.stat(f_path).st_mtime < now - 600:
                os.remove(f_path)
    except:
        pass

if __name__ == '__main__':
    app.run(debug=True, port=5000)
