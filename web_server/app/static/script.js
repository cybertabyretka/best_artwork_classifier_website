const themeToggle = document.getElementById('theme-toggle');
const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');

if (localStorage.getItem('theme') === 'dark' ||
    (!localStorage.getItem('theme') && prefersDarkScheme.matches)) {
    document.body.classList.add('dark-mode');
    themeToggle.checked = true;
}

themeToggle.addEventListener('change', function() {
    if (this.checked) {
        document.body.classList.add('dark-mode');
        localStorage.setItem('theme', 'dark');
    } else {
        document.body.classList.remove('dark-mode');
        localStorage.setItem('theme', 'light');
    }
});

const fileInput = document.getElementById('file-input');
const fileName = document.getElementById('file-name');
const previewContainer = document.getElementById('image-preview-container');
const previewImage = document.getElementById('preview-image');

fileInput.addEventListener('change', function() {
    if (this.files && this.files[0]) {
        fileName.textContent = this.files[0].name;

        const reader = new FileReader();
        reader.onload = function(e) {
            previewImage.src = e.target.result;
            previewContainer.style.display = 'block';
        }
        reader.readAsDataURL(this.files[0]);
    } else {
        fileName.textContent = '';
        previewContainer.style.display = 'none';
    }
});