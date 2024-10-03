document.querySelectorAll('.faq-item').forEach(item => {
    item.addEventListener('click', () => {
        item.classList.toggle('active');
    });
});
function chuyenHuong() {
    window.location.href = "{% url 'ten_view' %}";
}
