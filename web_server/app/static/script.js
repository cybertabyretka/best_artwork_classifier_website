const ARTISTS = [
    'Albrecht Dürer',
    'Alfred Sisley',
    'Amedeo Modigliani',
    'Andrei Rublev',
    'Andy Warhol',
    'Camille Pissarro',
    'Caravaggio',
    'Claude Monet',
    'Diego Rivera',
    'Diego Velázquez',
    'Edgar Degas',
    'Édouard Manet',
    'Edvard Munch',
    'El Greco',
    'Eugène Delacroix',
    'Francisco Goya',
    'Frida Kahlo',
    'Georges Seurat',
    'Giotto di Bondone',
    'Gustav Klimt',
    'Gustave Courbet',
    'Henri Matisse',
    'Henri Rousseau',
    'Henri de Toulouse-Lautrec',
    'Hieronymus Bosch',
    'Jackson Pollock',
    'Jan van Eyck',
    'Joan Miró',
    'Kazimir Malevich',
    'Leonardo da Vinci',
    'Marc Chagall',
    'Michelangelo',
    'Mikhail Vrubel',
    'Pablo Picasso',
    'Paul Cézanne',
    'Paul Gauguin',
    'Paul Klee',
    'Peter Paul Rubens',
    'Pierre-Auguste Renoir',
    'Piet Mondrian',
    'Pieter Bruegel',
    'Raphael',
    'Rembrandt',
    'René Magritte',
    'Salvador Dalí',
    'Sandro Botticelli',
    'Titian',
    'Vasiliy Kandinskiy',
    'Vincent van Gogh',
    'William Turner'
];

const themeToggle = document.getElementById('theme-toggle');
const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');

if (localStorage.getItem('theme') === 'dark' ||
    (!localStorage.getItem('theme') && prefersDarkScheme.matches)) {
    document.documentElement.classList.add('dark-mode');
    themeToggle.checked = true;
}

themeToggle.addEventListener('change', function() {
    if (this.checked) {
        document.documentElement.classList.add('dark-mode');
        localStorage.setItem('theme', 'dark');
    } else {
        document.documentElement.classList.remove('dark-mode');
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

document.addEventListener('DOMContentLoaded', function() {
    const artistsList = document.getElementById('artists-list');

    ARTISTS.forEach(artist => {
        const card = document.createElement('div');
        card.className = 'artist-card';
        card.textContent = artist;
        artistsList.appendChild(card);
    });
});

document.documentElement.classList.remove('theme-init');