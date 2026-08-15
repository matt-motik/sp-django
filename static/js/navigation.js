// static/js/navigation.js
document.addEventListener('DOMContentLoaded', function() {
    // Получаем имя текущей страницы из URL
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';

    // Находим все ссылки в меню
    document.querySelectorAll('.nav-link').forEach(link => {
        const href = link.getAttribute('href');

        // Если href совпадает с текущей страницей
        if (href === currentPage) {
            link.classList.add('active');
            link.classList.remove('text-white');
        } else {
            link.classList.remove('active');
            link.classList.add('text-white');
        }
    });
});