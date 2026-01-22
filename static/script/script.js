async function iniciarDownload() {
    const linkInput = document.getElementById('videoLink');
    const formatInput = document.querySelector('input[name="format"]:checked');
    const statusDiv = document.getElementById('status');
    const btn = document.getElementById('downloadBtn');

    const link = linkInput.value.trim();
    const format = formatInput.value;

    if (!link) {
        statusDiv.textContent = "Por favor, insira um link válido.";
        statusDiv.className = "status-message error";
        return;
    }

    // Reset status
    statusDiv.textContent = "Processando...";
    statusDiv.className = "status-message loading";
    btn.disabled = true;

    try {
        console.log("Enviando solicitação:", { link, format });

        const response = await fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: link, format: format })
        });

        if (!response.ok) {
            const errClone = response.clone();
            let msg = 'Erro desconhecido';
            try {
                const resJson = await errClone.json();
                msg = resJson.error || msg;
            } catch (e) {
                msg = await response.text();
            }
            throw new Error(msg);
        }

        // Se deu certo, inicia o download pelo navegador
        // Obtemos o "blob" (arquivo) da resposta
        const blob = await response.blob();

        // Pega o nome do arquivo do header 'Content-Disposition', se disponível
        // (Isso é um jeito de tentar pegar o nome original, senão usa um padrão)
        let filename = 'download';
        const disposition = response.headers.get('Content-Disposition');
        if (disposition && disposition.indexOf('attachment') !== -1) {
            const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
            const matches = filenameRegex.exec(disposition);
            if (matches != null && matches[1]) {
                filename = matches[1].replace(/['"]/g, '');
            }
        }

        // Cria link temporário para forçar o download no navegador
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = downloadUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(downloadUrl);
        document.body.removeChild(a);

        statusDiv.textContent = "Download concluído!";
        statusDiv.className = "status-message success";

    } catch (error) {
        console.error(error);
        statusDiv.textContent = "Erro: " + error.message;
    } finally {
        btn.disabled = false;
    }
}
