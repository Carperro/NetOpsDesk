/**
 * common.js - Utilidades compartidas para NetOps Desk
 */

const AUTH_KEY = 'netops_token';
const USER_KEY = 'netops_user';
const THEME_KEY = 'netops-desk-theme';

// --- 1. Autenticación ---
function isAuthenticated() {
    return localStorage.getItem(AUTH_KEY) !== null;
}

function getUser() {
    const userStr = localStorage.getItem(USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
}

function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = '/login';
    }
}

function logout() {
    localStorage.removeItem(AUTH_KEY);
    localStorage.removeItem(USER_KEY);
    window.location.href = '/login';
}

function login(username, password) {
    if (username && password) {
        localStorage.setItem(AUTH_KEY, 'fake-jwt-token-' + Date.now());
        localStorage.setItem(USER_KEY, JSON.stringify({
            username: username,
            role: 'admin',
            loginAt: new Date().toISOString()
        }));
        return true;
    }
    return false;
}

// --- 2. Gestión de Tema (Claro / Oscuro) ---
function initTheme() {
    const stored = localStorage.getItem(THEME_KEY);
    const theme = (stored === 'dark' || stored === 'light') ? stored : 'dark';
    document.documentElement.setAttribute('data-theme', theme);
    updateThemeButton(theme);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem(THEME_KEY, next);
    updateThemeButton(next);
}

function updateThemeButton(theme) {
    const btn = document.getElementById('theme-toggle');
    if (!btn) return;
    
    // Actualiza el texto del botón
    const textEl = btn.querySelector('#theme-text') || btn.querySelector('.theme-toggle__label');
    if (textEl) {
        textEl.textContent = theme === 'dark' ? 'Modo claro' : 'Modo oscuro';
    }
}

// Ejecutar cuando la página termine de cargar
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    
    // Lógica del botón de tema
    const themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) {
        themeBtn.addEventListener('click', toggleTheme);
    }
    
    // Cargar el usuario en el sidebar
    loadUserUI(); 

     // --- NUEVO: Configurar el botón de Cerrar Sesión global ---
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
});


// --- 3. Utilidades Globales ---
document.addEventListener('DOMContentLoaded', () => {
    // Actualizar el año del footer automáticamente
    const yearSpan = document.getElementById('current-year');
    if (yearSpan) {
        yearSpan.textContent = new Date().getFullYear();
    }
});

// --- Función para cargar datos del usuario en el Sidebar ---
function loadUserUI() {
    const user = getUser();
    if (user) {
        const userNameEl = document.getElementById('user-name');
        const userAvatarEl = document.getElementById('user-avatar');
        
        if (userNameEl) userNameEl.textContent = user.username;
        if (userAvatarEl) userAvatarEl.textContent = user.username.charAt(0).toUpperCase();
    }
}

