document.addEventListener('DOMContentLoaded', () => {
    if (!requireAuth()) return;

    const tools = window.NETOPS_TOOLS || [];
    const grid = document.getElementById('tools-grid');
    const searchInput = document.getElementById('tool-search');
    const catalogTitle = document.getElementById('catalog-title');
    const profileToggle = document.getElementById('profile-toggle');
    const profileDropdown = document.getElementById('profile-dropdown');
    const favoritesKey = 'netops_favorites';
    const favoritesOnly = new URLSearchParams(window.location.search).get('favorites') === '1';

    let favorites = readFavorites();

    function readFavorites() {
        try {
            const stored = JSON.parse(localStorage.getItem(favoritesKey) || '[]');
            return Array.isArray(stored) ? stored.filter((id) => typeof id === 'string') : [];
        } catch {
            return [];
        }
    }

    function isFavorite(toolId) {
        return favorites.includes(toolId);
    }

    function makeFavoriteButton(tool) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'favorite-button';
        button.textContent = isFavorite(tool.id) ? '★' : '☆';
        button.setAttribute('aria-label', isFavorite(tool.id)
            ? `Quitar ${tool.name} de favoritos`
            : `Agregar ${tool.name} a favoritos`);
        button.setAttribute('aria-pressed', String(isFavorite(tool.id)));
        button.addEventListener('click', (event) => {
            event.preventDefault();
            event.stopPropagation();
            favorites = isFavorite(tool.id)
                ? favorites.filter((id) => id !== tool.id)
                : [...favorites, tool.id];
            localStorage.setItem(favoritesKey, JSON.stringify(favorites));
            renderGrid(searchInput?.value || '');
        });
        return button;
    }

    function matchesTool(tool, query) {
        const normalize = (value) => String(value)
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLocaleLowerCase();
        const searchable = normalize(`${tool.name} ${tool.description} módulo ${tool.module}`);
        return searchable.includes(normalize(query));
    }

    function renderGrid(query = '') {
        if (!grid) return;
        const normalizedQuery = query.trim();
        const visibleTools = tools.filter((tool) => {
            return (!favoritesOnly || isFavorite(tool.id)) && matchesTool(tool, normalizedQuery);
        });

        grid.replaceChildren();
        if (visibleTools.length === 0) {
            const empty = document.createElement('p');
            empty.className = 'empty-tools-message';
            empty.textContent = favoritesOnly
                ? 'Todavía no guardaste herramientas favoritas.'
                : 'No hay herramientas que coincidan con la búsqueda.';
            grid.append(empty);
            return;
        }

        visibleTools.forEach((tool) => {
            const card = document.createElement('article');
            card.className = 'tool-card';

            const link = document.createElement('a');
            link.className = 'tool-card-link';
            link.href = tool.url;

            const moduleLabel = document.createElement('span');
            moduleLabel.className = 'tool-card-module';
            moduleLabel.textContent = `Módulo ${tool.module}`;

            const title = document.createElement('h3');
            title.textContent = tool.name;

            const description = document.createElement('p');
            description.textContent = tool.description;
            link.append(moduleLabel, title, description);
            card.append(link, makeFavoriteButton(tool));
            grid.append(card);
        });
    }

    function closeProfile() {
        if (!profileToggle || !profileDropdown) return;
        profileToggle.setAttribute('aria-expanded', 'false');
        profileDropdown.hidden = true;
    }

    if (favoritesOnly && catalogTitle) catalogTitle.textContent = 'Herramientas favoritas';
    renderGrid();

    const cachedUser = getUser();
    if (cachedUser?.username) {
        const cachedName = cachedUser.username;
        const topbarName = document.getElementById('topbar-user');
        const profileName = document.getElementById('profile-name');
        const profileAvatar = document.getElementById('profile-avatar');
        if (topbarName) topbarName.textContent = cachedName;
        if (profileName) profileName.textContent = cachedName;
        if (profileAvatar) profileAvatar.textContent = cachedName.charAt(0).toUpperCase();
    }

    if (searchInput) {
        searchInput.addEventListener('input', () => {
            renderGrid(searchInput.value);
        });
    }

    document.addEventListener('click', (event) => {
        if (profileDropdown && !event.target.closest('.profile-menu')) closeProfile();
    });

    if (profileToggle && profileDropdown) {
        profileToggle.addEventListener('click', () => {
            const expanded = profileToggle.getAttribute('aria-expanded') === 'true';
            profileToggle.setAttribute('aria-expanded', String(!expanded));
            profileDropdown.hidden = expanded;
        });
        profileDropdown.querySelector('[data-logout]')?.addEventListener('click', logout);
        profileToggle.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') closeProfile();
        });
    }

    loadProfile();

    async function loadProfile() {
        try {
            const response = await fetch('/api/v1/auth/me');
            if (!response.ok) return;
            const user = await response.json();
            localStorage.setItem('netops_user', JSON.stringify({ username: user.username }));
            const name = user.username || 'Usuario';
            const topbarName = document.getElementById('topbar-user');
            const profileName = document.getElementById('profile-name');
            const profileRole = document.getElementById('profile-role');
            const profileAvatar = document.getElementById('profile-avatar');
            const sidebarName = document.getElementById('user-name');
            const sidebarRole = document.getElementById('user-role');
            const sidebarAvatar = document.getElementById('user-avatar');

            if (topbarName) topbarName.textContent = name;
            if (profileName) profileName.textContent = name;
            if (profileAvatar) profileAvatar.textContent = name.charAt(0).toUpperCase();
            if (profileRole) profileRole.textContent = user.role || 'Usuario';
            if (sidebarName) sidebarName.textContent = name;
            if (sidebarRole) sidebarRole.textContent = user.role || 'Usuario';
            if (sidebarAvatar) sidebarAvatar.textContent = name.charAt(0).toUpperCase();
        } catch {
            // El interceptor global gestiona los errores de autenticación.
        }
    }
});
