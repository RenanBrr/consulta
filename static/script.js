document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('consultaForm');
    const estadoSelect = document.getElementById('estado');
    const cepInput = document.getElementById('cep');
    const numeroInput = document.getElementById('numero');
    const limparBtn = document.getElementById('limparBtn');
    const buscarBtn = document.getElementById('buscarBtn');
    const modal = document.getElementById('modal');
    const modalContent = document.getElementById('modalContent');
    const fecharModal = document.getElementById('fecharModal');

    console.log('JavaScript carregado');

    // Habilitar/desabilitar campos baseado na seleção do estado
    estadoSelect.addEventListener('change', () => {
        const estadoSelecionado = estadoSelect.value;
        console.log('Estado selecionado:', estadoSelecionado);
        
        cepInput.disabled = !estadoSelecionado;
        numeroInput.disabled = !estadoSelecionado;
        buscarBtn.disabled = !estadoSelecionado;

        if (!estadoSelecionado) {
            cepInput.value = '';
            numeroInput.value = '';
        }
        
        // Foca no campo de CEP quando um estado é selecionado
        if (estadoSelecionado) {
            cepInput.focus();
        }
    });

    // Máscara para o CEP
    cepInput.addEventListener('input', (e) => {
        e.target.value = e.target.value.replace(/\D/g, '');
    });

    // Máscara para o número
    numeroInput.addEventListener('input', (e) => {
        e.target.value = e.target.value.replace(/\D/g, '');
    });

    // Limpar campos
    limparBtn.addEventListener('click', () => {
        form.reset();
        cepInput.disabled = true;
        numeroInput.disabled = true;
        buscarBtn.disabled = true;
        console.log('Campos limpos');
    });

    // Fechar modal
    fecharModal.addEventListener('click', () => {
        modal.classList.remove('active');
        console.log('Modal fechado');
    });

    // Função para exibir lista de endereços
    async function exibirEnderecos(estado, cep) {
        try {
            const response = await fetch('/consulta', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ estado, cep, numero: '' }),
            });

            const data = await response.json();
            if (data.viavel && data.enderecos) {
                const enderecosList = data.enderecos.map(end => `<li>${end}</li>`).join('');
                showModal(`
                    <div class="modal-scroll">
                        <ul class="endereco-list">
                            ${enderecosList}
                        </ul>
                    </div>
                    <button id="contrateBtn" class="action-button" onclick="window.location.href='https://www.google.com'">
                        Contrate agora!
                    </button>
                `, 'success');
            }
        } catch (error) {
            console.error('Erro ao buscar endereços:', error);
        }
    }

    // Consulta de viabilidade
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        console.log('Formulário submetido');

        const estado = estadoSelect.value;
        const cep = cepInput.value;
        const numero = numeroInput.value;

        console.log('Dados do formulário:', { estado, cep, numero });

        if (!estado) {
            showModal('Por favor, selecione um estado.', 'error');
            return;
        }

        if (!cep) {
            showModal('Por favor, preencha o CEP.', 'error');
            return;
        }

        try {
            console.log('Iniciando consulta ao servidor...');
            const response = await fetch('/consulta', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ estado, cep, numero }),
            });

            console.log('Resposta recebida:', response);
            const data = await response.json();
            console.log('Dados da resposta:', data);

            if (data.viavel) {
                if (numero && data.numero_invalido) {
                    showModal(`
                        <div>
                            <div class="success-message">O CEP ${cep} consta na SuperLista Tim ✓</div>
                            <div class="error-message">Fachada nº ${numero} INVIÁVEL ✗</div>
                            <div class="button-container">
                                <button onclick="window.exibirEnderecos('${estado}', '${cep}')" class="action-button bg-blue-600 hover:bg-blue-700 text-white">
                                    Exibir Disponibilidade CEP
                                </button>
                                <button id="contrateBtn" class="action-button" onclick="window.location.href='https://www.google.com'">
                                    Contrate agora!
                                </button>
                            </div>
                        </div>
                    `, 'warning');
                } else if (numero) {
                    showModal(`
                        <div class="success-message">Viável UltraFibra ✓</div>
                        <div class="text-gray-700 mb-4">${data.endereco}</div>
                        <button id="contrateBtn" class="action-button" onclick="window.location.href='https://www.google.com'">
                            Contrate agora!
                        </button>
                    `, 'success');
                }
            } else {
                showModal(`
                    <div class="error-message">${data.mensagem} ✗</div>
                `, 'error');
            }
        } catch (error) {
            console.error('Erro na consulta:', error);
            showModal('Erro ao realizar a consulta. Tente novamente.', 'error');
        }
    });

    function showModal(content, type) {
        console.log('Exibindo modal:', { content, type });
        modalContent.innerHTML = content;
        modal.classList.add('active');

        // Adiciona evento ao botão de exibir disponibilidade
        const btnExibir = modalContent.querySelector('button[onclick^="window.exibirEnderecos"]');
        if (btnExibir) {
            const onclick = btnExibir.getAttribute('onclick');
            const [estado, cep] = onclick.match(/'([^']+)'/g).map(str => str.replace(/'/g, ''));
            btnExibir.onclick = () => exibirEnderecos(estado, cep);
        }
    }

    // Expor função exibirEnderecos globalmente
    window.exibirEnderecos = exibirEnderecos;
}); 