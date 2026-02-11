// Confirmation dialogs
function confirmDelete(formId) {
    if (confirm('Bu kaydı silmek istediğinizden emin misiniz?')) {
        document.getElementById(formId).submit();
    }
}

// Auto-hide alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function () {
    setTimeout(function () {
        const alerts = document.querySelectorAll('.alert-auto-hide');
        alerts.forEach(a => a.style.display = 'none');
    }, 5000);
});
