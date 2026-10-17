document.addEventListener('DOMContentLoaded', () => {
    // 1. Proteger la página (por si acaso, common.js también lo hace)
    requireAuth();

    // 2. Cargar datos SOLO para el contenido principal del dashboard
    const user = getUser();
    if (user) {
        // Esto es solo para el título grande de "Bienvenido, admin"
        const welcomeTitle = document.getElementById('welcome-title');
        if (welcomeTitle) {
            welcomeTitle.textContent = `Bienvenido, ${user.username}`;
        }
    }


});