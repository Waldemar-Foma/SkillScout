document.addEventListener("DOMContentLoaded", function () {
    const ruBtn = document.querySelector('.language-btn:nth-child(1)');
    const enBtn = document.querySelector('.language-btn:nth-child(2)');
    const ruContent = document.getElementById('ru-content');
    const enContent = document.getElementById('en-content');

    ruBtn.addEventListener('click', function () {
        ruBtn.classList.add('active');
        enBtn.classList.remove('active');
        ruContent.classList.remove('hidden');
        enContent.classList.add('hidden');
    });

    enBtn.addEventListener('click', function () {
        enBtn.classList.add('active');
        ruBtn.classList.remove('active');
        enContent.classList.remove('hidden');
        ruContent.classList.add('hidden');
    });
});
