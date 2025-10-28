/**
 * API Client para PhotoLeader
 * Funções para comunicação com o backend Flask
 */

const API_BASE_URL = 'http://localhost:5000/api';

/**
 * Configuração padrão para fetch
 */
const fetchConfig = {
    headers: {
        'Content-Type': 'application/json',
    }
};

/**
 * API Health Check
 */
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        return await response.json();
    } catch (error) {
        console.error('Erro ao verificar status da API:', error);
        return { status: 'error', error: error.message };
    }
}

/**
 * Busca todas as fotos
 * @param {Object} params - Parâmetros de query (limit, skip, tag, user)
 */
async function getPhotos(params = {}) {
    try {
        const queryString = new URLSearchParams(params).toString();
        const url = `${API_BASE_URL}/photos${queryString ? '?' + queryString : ''}`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error);
        }
        
        return data.photos;
    } catch (error) {
        console.error('Erro ao buscar fotos:', error);
        throw error;
    }
}

/**
 * Busca uma foto específica
 * @param {string} photoId - ID da foto
 */
async function getPhoto(photoId) {
    try {
        const response = await fetch(`${API_BASE_URL}/photos/${photoId}`);
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error);
        }
        
        return data.photo;
    } catch (error) {
        console.error('Erro ao buscar foto:', error);
        throw error;
    }
}

/**
 * Upload de nova foto (metadados)
 * @param {Object} photoData - Dados da foto
 */
async function uploadPhoto(photoData) {
    try {
        const response = await fetch(`${API_BASE_URL}/photos`, {
            method: 'POST',
            headers: fetchConfig.headers,
            body: JSON.stringify(photoData)
        });
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error);
        }
        
        return data;
    } catch (error) {
        console.error('Erro ao fazer upload:', error);
        throw error;
    }
}

/**
 * Remove uma foto
 * @param {string} photoId - ID da foto
 */
async function deletePhoto(photoId) {
    try {
        const response = await fetch(`${API_BASE_URL}/photos/${photoId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error);
        }
        
        return data;
    } catch (error) {
        console.error('Erro ao deletar foto:', error);
        throw error;
    }
}

/**
 * Busca fotos de um usuário
 * @param {string} username - Nome do usuário
 */
async function getPhotosByUser(username) {
    try {
        const response = await fetch(`${API_BASE_URL}/photos/user/${username}`);
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error);
        }
        
        return data.photos;
    } catch (error) {
        console.error('Erro ao buscar fotos do usuário:', error);
        throw error;
    }
}

/**
 * Busca fotos por tag
 * @param {string} tag - Tag para buscar
 */
async function getPhotosByTag(tag) {
    try {
        const response = await fetch(`${API_BASE_URL}/photos/tag/${tag}`);
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error);
        }
        
        return data.photos;
    } catch (error) {
        console.error('Erro ao buscar fotos por tag:', error);
        throw error;
    }
}

/**
 * Busca fotos por texto
 * @param {string} query - Texto para buscar
 */
async function searchPhotos(query) {
    try {
        const response = await fetch(`${API_BASE_URL}/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error);
        }
        
        return data.photos;
    } catch (error) {
        console.error('Erro ao buscar fotos:', error);
        throw error;
    }
}

/**
 * Busca estatísticas do sistema
 */
async function getStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error);
        }
        
        return {
            totalPhotos: data.total_photos,
            topUsers: data.top_users,
            topTags: data.top_tags
        };
    } catch (error) {
        console.error('Erro ao buscar estatísticas:', error);
        throw error;
    }
}

/**
 * Formata data para exibição
 * @param {string} dateString - Data em formato ISO
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Exibe mensagem de erro na UI
 * @param {string} message - Mensagem de erro
 * @param {HTMLElement} container - Container para exibir erro
 */
function showError(message, container) {
    if (container) {
        container.innerHTML = `
            <div class="error-message">
                <strong>Erro:</strong> ${message}
            </div>
        `;
    } else {
        alert(`Erro: ${message}`);
    }
}

/**
 * Exibe mensagem de sucesso na UI
 * @param {string} message - Mensagem de sucesso
 * @param {HTMLElement} container - Container para exibir sucesso
 */
function showSuccess(message, container) {
    if (container) {
        container.innerHTML = `
            <div class="success-message">
                ${message}
            </div>
        `;
        
        // Remove mensagem após 3 segundos
        setTimeout(() => {
            container.innerHTML = '';
        }, 3000);
    } else {
        alert(message);
    }
}

/**
 * Cria elemento HTML de foto para galeria
 * @param {Object} photo - Dados da foto
 */
function createPhotoElement(photo) {
    const photoDiv = document.createElement('div');
    photoDiv.className = 'photo-item';
    photoDiv.dataset.photoId = photo._id;
    
    photoDiv.innerHTML = `
        <div class="photo-header">
            <span class="photo-user">👤 ${photo.user}</span>
            <span class="photo-date">${formatDate(photo.upload_date)}</span>
        </div>
        <div class="photo-body">
            <h3 class="photo-filename">📷 ${photo.filename}</h3>
            ${photo.description ? `<p class="photo-description">${photo.description}</p>` : ''}
            <div class="photo-tags">
                ${photo.tags.map(tag => `<span class="tag">#${tag}</span>`).join(' ')}
            </div>
        </div>
        <div class="photo-footer">
            <span class="photo-size">${photo.size_kb ? photo.size_kb + ' KB' : ''}</span>
            <button class="btn-delete" onclick="handleDeletePhoto('${photo._id}')">🗑️ Deletar</button>
        </div>
    `;
    
    return photoDiv;
}

/**
 * Renderiza lista de fotos na galeria
 * @param {Array} photos - Array de fotos
 * @param {HTMLElement} container - Container para renderizar
 */
function renderPhotos(photos, container) {
    if (!container) {
        console.error('Container não encontrado');
        return;
    }
    
    container.innerHTML = '';
    
    if (photos.length === 0) {
        container.innerHTML = '<p class="no-photos">Nenhuma foto encontrada</p>';
        return;
    }
    
    photos.forEach(photo => {
        const photoElement = createPhotoElement(photo);
        container.appendChild(photoElement);
    });
}

/**
 * Handler para deletar foto (deve ser implementado em cada página)
 * @param {string} photoId - ID da foto
 */
async function handleDeletePhoto(photoId) {
    if (!confirm('Tem certeza que deseja deletar esta foto?')) {
        return;
    }
    
    try {
        await deletePhoto(photoId);
        alert('Foto deletada com sucesso!');
        
        // Remove elemento da DOM
        const photoElement = document.querySelector(`[data-photo-id="${photoId}"]`);
        if (photoElement) {
            photoElement.remove();
        }
    } catch (error) {
        alert('Erro ao deletar foto: ' + error.message);
    }
}

// Exporta funções para uso global
window.PhotoLeaderAPI = {
    checkAPIHealth,
    getPhotos,
    getPhoto,
    uploadPhoto,
    deletePhoto,
    getPhotosByUser,
    getPhotosByTag,
    searchPhotos,
    getStats,
    formatDate,
    showError,
    showSuccess,
    createPhotoElement,
    renderPhotos,
    handleDeletePhoto
};
