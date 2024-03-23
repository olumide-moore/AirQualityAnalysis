//Hamburger menu
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('active');
    navMenu.classList.toggle('active');
});
//Ensure that the hamburger menu is hidden when a menu item is clicked
const menuLinks = document.querySelectorAll('.nav-link');
menuLinks.forEach((menuLink) => {
    menuLink.addEventListener('click', () => {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
    });
});