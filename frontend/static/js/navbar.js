const links = document.querySelectorAll(".navbar-links a")

links.forEach(link => {
    link.addEventListener('mouseenter', () => {
        link.style.backgroundColor = 'rgb(230, 226, 18)';
        link.style.color = 'black';
    });

    link.addEventListener('mouseleave', () => {
        link.style.backgroundColor = 'black';
        link.style.color = 'white';
    });
});