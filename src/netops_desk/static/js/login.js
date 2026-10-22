const savedTheme = localStorage.getItem('netops-desk-theme');
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
document.documentElement.setAttribute(
    'data-theme',
    savedTheme === 'light' || savedTheme === 'dark' ? savedTheme : prefersDark ? 'dark' : 'light',
);

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('login-form');
    const errorMessage = document.getElementById('error-message');
    const submitButton = form?.querySelector('button[type="submit"]');

    if (!form || !errorMessage) return;

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        errorMessage.hidden = true;
        const idleLabel = submitButton?.textContent;
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = 'Ingresando...';
            submitButton.setAttribute('aria-busy', 'true');
        }

        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;

        try {
            const response = await fetch('/api/v1/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
            });
            const data = await response.json().catch(() => ({}));

            if (!response.ok || !data.access_token) {
                localStorage.removeItem('netops_token');
                localStorage.removeItem('netops_user');
                const serverMessage = typeof data.detail === 'string'
                    ? data.detail
                    : typeof data.detail?.detail === 'string'
                        ? data.detail.detail
                        : '';
                errorMessage.textContent = serverMessage || 'Usuario o contraseña incorrectos.';
                errorMessage.hidden = false;
                return;
            }

            localStorage.setItem('netops_token', data.access_token);
            localStorage.setItem('netops_user', JSON.stringify({ username }));
            window.location.replace('/');
        } catch {
            errorMessage.textContent = 'No se pudo conectar con el servidor. Intentá de nuevo.';
            errorMessage.hidden = false;
        } finally {
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = idleLabel;
                submitButton.removeAttribute('aria-busy');
            }
        }
    });
});
