"use strict";

const AUTH_KEY = "netops_token";
const USER_KEY = "netops_user";
const THEME_KEY = "netops-desk-theme";
let sessionRedirectInProgress = false;

(function installAuthenticatedFetch() {
    const originalFetch = window.fetch.bind(window);

    window.fetch = async function(...args) {
        const [input, requestOptions = {}] = args;
        const requestUrl = input instanceof Request
            ? input.url
            : input instanceof URL
                ? input.href
                : String(input);
        const url = new URL(requestUrl, window.location.href);
        const isSameOriginApi = url.origin === window.location.origin
            && url.pathname.startsWith("/api/");
        const isLoginRequest = isSameOriginApi
            && url.pathname === "/api/v1/auth/login";

        const headers = new Headers(input instanceof Request ? input.headers : undefined);
        new Headers(args[1]?.headers).forEach((value, name) => {
            headers.set(name, value);
        });

        const token = localStorage.getItem(AUTH_KEY);
        if (isSameOriginApi && !isLoginRequest && token) {
            headers.set("Authorization", `Bearer ${token}`);
        }

        args[1] = { ...requestOptions, headers };
        const response = await originalFetch(...args);

        if (isSameOriginApi && !isLoginRequest && response.status === 401) {
            expireSession();
        }
        return response;
    };
})();

function isLoginPage() {
    return window.location.pathname === "/login"
        || window.location.pathname.endsWith("/login.html");
}

function isAuthenticated() {
    return Boolean(localStorage.getItem(AUTH_KEY));
}

function requireAuth() {
    if (isLoginPage()) return true;
    if (isAuthenticated()) return true;
    window.location.replace("/login");
    return false;
}

function expireSession() {
    localStorage.removeItem(AUTH_KEY);
    localStorage.removeItem(USER_KEY);
    if (sessionRedirectInProgress) return;

    sessionRedirectInProgress = true;
    window.alert("Sesión expirada");
    if (!isLoginPage()) window.location.replace("/login");
}

function logout() {
    localStorage.removeItem(AUTH_KEY);
    localStorage.removeItem(USER_KEY);
    window.location.replace("/login");
}

function getUser() {
    try {
        return JSON.parse(localStorage.getItem(USER_KEY) || "null");
    } catch {
        return null;
    }
}

function initTheme() {
    const stored = localStorage.getItem(THEME_KEY);
    const theme = stored === "light" || stored === "dark" ? stored : "dark";
    document.documentElement.setAttribute("data-theme", theme);
    updateThemeButton(theme);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme") || "dark";
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem(THEME_KEY, next);
    updateThemeButton(next);
}

function updateThemeButton(theme) {
    const button = document.getElementById("theme-toggle");
    const label = button?.querySelector("#theme-text, .theme-toggle__label");
    if (label) label.textContent = theme === "dark" ? "Modo claro" : "Modo oscuro";
}

function loadUserUI() {
    const user = getUser();
    if (!user) return;
    const name = user.username || "Usuario";
    const nameElement = document.getElementById("user-name");
    const avatarElement = document.getElementById("user-avatar");
    if (nameElement) nameElement.textContent = name;
    if (avatarElement) avatarElement.textContent = name.charAt(0).toUpperCase();
}

document.addEventListener("DOMContentLoaded", (event) => {
    if (!requireAuth()) {
        document.body.hidden = true;
        event.stopImmediatePropagation();
        return;
    }

    initTheme();
    loadUserUI();

    const themeBtn = document.getElementById("theme-toggle");
    if (themeBtn) themeBtn.addEventListener('click', toggleTheme);

    const year = document.getElementById("current-year");
    if (year) year.textContent = String(new Date().getFullYear());
});
