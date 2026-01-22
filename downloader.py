import yt_dlp
import os

def main():
    print("=== Downloader Simples (Sem Conversão) ===")
    video_link = input("Cole o link do YouTube aqui: ").strip()

    if not video_link:
        print("Link vazio.")
        return

    print("Escolha o formato:")
    print("1 - Áudio")
    print("2 - Vídeo")
    
    while True:
        opcao = input("Digite a opção (1 ou 2): ").strip()
        if opcao in ['1', '2']:
            break
        print("Opção inválida. Tente digitar 1 ou 2.")

    # Define pasta Downloads
    pasta_downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
    
    ydl_opts = {
        'outtmpl': os.path.join(pasta_downloads, '%(title)s.%(ext)s'),
        'noplaylist': True,
    }

    # SEGURANÇA: Só carrega cookies se o arquivo existir LOCALMENTE.
    # Não forçamos o uso do navegador para evitar erros e riscos desnecessários.
    caminho_cookies = os.path.join(os.getcwd(), 'cookies.txt')
    if os.path.exists(caminho_cookies):
        print("Aviso: Usando arquivo de cookies.txt para autenticação.")
        ydl_opts['cookiefile'] = caminho_cookies
    
    # Se quiser testar sem login (mais seguro e padrão), não precisa fazer nada.
    # O yt-dlp tentará baixar anonimamente primeiro.

    if opcao == '2':
        # Tenta evitar HLS/m3u8 que costuma dar erro de fragmento
        # Prioriza streams HTTP diretos (progressivos) em MP4
        ydl_opts['format'] = 'best[ext=mp4][protocol^=http]/best[ext=mp4]/best'
        print(f"O vídeo será salvo em: {pasta_downloads}")
    else:
        ydl_opts['format'] = 'bestaudio/best'
        print(f"O áudio será salvo em: {pasta_downloads}")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_link])
        print("\nSUCESSO! Pode conferir na sua pasta Downloads.")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()