// main.js — students will add JavaScript here as features are built

document.addEventListener('DOMContentLoaded', function () {
    var openBtn = document.getElementById('how-it-works-btn');
    var overlay = document.getElementById('video-modal');
    var closeBtn = document.getElementById('video-modal-close');
    var iframe = document.getElementById('video-modal-iframe');
    var videoSrc = 'https://www.youtube.com/embed/M7lc1UVf-VE';

    if (!openBtn || !overlay || !closeBtn || !iframe) return;

    function openModal() {
        iframe.src = videoSrc + '?autoplay=1';
        overlay.classList.add('is-open');
    }

    function closeModal() {
        overlay.classList.remove('is-open');
        iframe.src = '';
    }

    openBtn.addEventListener('click', openModal);
    closeBtn.addEventListener('click', closeModal);
    overlay.addEventListener('click', function (e) {
        if (e.target === overlay) closeModal();
    });
});
