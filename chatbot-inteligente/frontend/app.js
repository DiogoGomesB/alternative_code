// Selecione os elementos necessários da página
const chatDiv = document.getElementById('chat');
const messageInput = document.getElementById('message');
const sendButton = document.querySelector('button');

// Função para adicionar uma mensagem no chat
function appendMessage(text, sender) {
    const messageElement = document.createElement('p');
    messageElement.classList.add(sender);  // 'user' ou 'assistant'
    messageElement.textContent = text;
    chatDiv.appendChild(messageElement);
    chatDiv.scrollTop = chatDiv.scrollHeight;  // Rola a tela para o final
}

// Função para enviar a mensagem ao backend (Flask) e obter resposta da OpenAI
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    // Adiciona a mensagem do usuário ao chat
    appendMessage("Você: " + message, 'user');
    messageInput.value = ''; // Limpa o campo de entrada

    try {
        // Envia a mensagem para o backend Flask
        const response = await fetch('http://localhost:5000/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });

        const data = await response.json();

        if (data.reply) {
            // Se a resposta for bem-sucedida, exibe a resposta da IA
            appendMessage("Chatbot: " + data.reply, 'assistant');
        } else if (data.error) {
            // Se ocorrer um erro, exibe o erro
            appendMessage("Erro: " + data.error, 'assistant');
        }
    } catch (error) {
        // Em caso de erro de comunicação
        appendMessage("Erro de conexão com o servidor.", 'assistant');
    }
}

// Função para resetar o chat (apagar histórico)
async function resetChat() {
    // Envia requisição ao backend para resetar o histórico
    await fetch('http://localhost:5000/reset', { method: 'POST' });

    // Limpa o histórico no frontend
    chatDiv.innerHTML = '';
}

// Evento de clique no botão de enviar
sendButton.addEventListener('click', sendMessage);

// Evento de pressionamento de tecla para enviar a mensagem (opcional)
messageInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        sendMessage();
    }
});
