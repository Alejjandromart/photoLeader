document.addEventListener('DOMContentLoaded', () => {
    const replicaSetNameEl = document.getElementById('replica-set-name');
    const summaryTextEl = document.getElementById('summary-text');
    const nodesGrid = document.getElementById('nodes-grid');
    const loadingEl = document.getElementById('loading');
    const errorMessageEl = document.getElementById('error-message');
    const refreshBtn = document.getElementById('refresh-btn');

    const API_URL = '/api/replicaset/status';

    // Mapeamento de ícones para os estados
    const stateIcons = {
        'PRIMARY': '👑',
        'SECONDARY': '📦',
        'ARBITER': '⚖️',
        'RECOVERING': '🔄',
        'STARTUP': '🚀',
        'STARTUP2': '🚀',
        'UNKNOWN': '❓',
        'DOWN': '❌',
        'ROLLBACK': '↩️',
        'REMOVED': '🗑️'
    };

    async function fetchStatus() {
        // Mostrar loading e esconder erros
        loadingEl.classList.remove('hidden');
        errorMessageEl.classList.add('hidden');
        nodesGrid.innerHTML = ''; // Limpar grid

        try {
            const response = await fetch(API_URL);
            if (!response.ok) {
                throw new Error(`Erro na requisição: ${response.statusText}`);
            }
            const data = await response.json();

            if (data.success) {
                renderStatus(data);
            } else {
                showError(data.error);
            }
        } catch (error) {
            showError(error.message);
        } finally {
            loadingEl.classList.add('hidden');
        }
    }

    function renderStatus(data) {
        replicaSetNameEl.textContent = data.replica_set_name || 'N/A';

        if (data.members && data.members.length > 0) {
            // Contar membros por status
            const healthy = data.members.filter(m => m.health === 'Healthy').length;
            const total = data.members.length;
            const primary = data.members.find(m => m.state === 'PRIMARY');
            
            summaryTextEl.textContent = `${healthy}/${total} nós saudáveis • Primary: ${primary ? primary.name : 'Nenhum'}`;

            // Criar cards para cada membro
            data.members.forEach(member => {
                const card = createNodeCard(member);
                nodesGrid.appendChild(card);
            });
        } else {
            nodesGrid.innerHTML = '<p style="text-align: center; grid-column: 1/-1;">Nenhum membro encontrado.</p>';
        }
    }

    function createNodeCard(member) {
        const card = document.createElement('div');
        const isPrimary = member.state === 'PRIMARY';
        const isSecondary = member.state === 'SECONDARY';
        const isHealthy = member.health === 'Healthy';
        
        // Determinar classe do card
        let cardClass = 'node-card';
        let badgeClass = 'node-status-badge';
        if (isPrimary) {
            cardClass += ' primary';
            badgeClass += ' badge-primary';
        } else if (isSecondary && isHealthy) {
            cardClass += ' secondary';
            badgeClass += ' badge-secondary';
        } else {
            cardClass += ' unhealthy';
            badgeClass += ' badge-unhealthy';
        }

        // Obter ícone apropriado
        const icon = getStateIcon(member.state, isHealthy);

        // Formatar uptime
        const uptimeFormatted = formatUptime(member.uptime);

        card.className = cardClass;
        card.innerHTML = `
            <div class="node-header">
                <div class="node-icon">${icon}</div>
                <span class="${badgeClass}">${translateState(member.state)}</span>
            </div>
            <div class="node-title">${member.name}</div>
            <div class="node-details">
                <div class="detail-item">
                    <span class="detail-label">Saúde:</span>
                    <span class="detail-value ${isHealthy ? 'health-healthy' : 'health-unhealthy'}">
                        ${isHealthy ? '✓ Saudável' : '✗ Com Problemas'}
                    </span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Tempo Ativo:</span>
                    <span class="detail-value">${uptimeFormatted}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Ping:</span>
                    <span class="detail-value">${member.pingMs !== 'N/A' ? member.pingMs + ' ms' : 'N/A'}</span>
                </div>
            </div>
        `;

        return card;
    }

    function getStateIcon(state, isHealthy) {
        if (!isHealthy) {
            return '🔴';
        }
        
        // Primary recebe coroa
        if (state === 'PRIMARY') {
            return '👑';
        }
        
        // Todos os outros nós saudáveis recebem círculo verde
        return '🟢';
    }

    function translateState(state) {
        const translations = {
            'PRIMARY': 'Primário',
            'SECONDARY': 'Secundário',
            'ARBITER': 'Árbitro',
            'RECOVERING': 'Recuperando',
            'STARTUP': 'Iniciando',
            'STARTUP2': 'Iniciando',
            'UNKNOWN': 'Desconhecido',
            'DOWN': 'Inativo',
            'ROLLBACK': 'Revertendo',
            'REMOVED': 'Removido',
            '(not reachable/healthy)': 'Inacessível'
        };
        return translations[state] || state;
    }

    function formatUptime(seconds) {
        if (!seconds || seconds === 0) {
            return 'Indisponível';
        }
        
        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        
        if (days > 0) {
            return `${days}d ${hours}h ${minutes}m`;
        } else if (hours > 0) {
            return `${hours}h ${minutes}m`;
        } else if (minutes > 0) {
            return `${minutes} minutos`;
        } else {
            return `${seconds} segundos`;
        }
    }

    function showError(message) {
        errorMessageEl.textContent = `❌ Erro ao carregar dados: ${message}`;
        errorMessageEl.classList.remove('hidden');
        summaryTextEl.textContent = 'Erro ao conectar ao banco de dados';
    }

    // Event Listeners
    refreshBtn.addEventListener('click', fetchStatus);

    // Atualização automática a cada 10 segundos
    setInterval(fetchStatus, 10000);

    // Carregar dados ao iniciar a página
    fetchStatus();
});
