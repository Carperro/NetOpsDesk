/**
 * auth.js - Lógica para la página de Login
 */
document.addEventListener('DOMContentLoaded', () => {
    // Si ya está logueado, redirigir al inicio
    if (isAuthenticated()) {
        window.location.href = '/';
        return;
    }

    const form = document.getElementById('login-form');
    const errorDiv = document.getElementById('error-message');

    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const user = document.getElementById('username').value;
            const pass = document.getElementById('password').value;

            if (login(user, pass)) {
                window.location.href = '/';
            } else {
                errorDiv.textContent = 'Por favor, completá todos los campos.';
                errorDiv.hidden = false;
            }
        });
    }
});