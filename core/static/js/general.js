// Mobile nav toggle
const mobileToggle = document.getElementById('mobile-toggle');
const mobileMenu = document.getElementById('mobile-menu');

if (mobileToggle && mobileMenu) {
  mobileToggle.addEventListener('click', function () {
    const isOpen = !mobileMenu.classList.contains('hidden');
    mobileMenu.classList.toggle('hidden');

    // Animate hamburger lines
    const lines = mobileToggle.querySelectorAll('.hamburger-line');
    if (!isOpen) {
      lines[0].style.transform = 'rotate(45deg) translate(4px, 4px)';
      lines[1].style.opacity = '0';
      lines[2].style.transform = 'rotate(-45deg) translate(4px, -4px)';
    } else {
      lines[0].style.transform = '';
      lines[1].style.opacity = '';
      lines[2].style.transform = '';
    }
  });
}

// Navbar shadow on scroll
const nav = document.getElementById('main-nav');
if (nav) {
  window.addEventListener('scroll', function () {
    if (window.scrollY > 10) {
      nav.classList.add('shadow-md');
    } else {
      nav.classList.remove('shadow-md');
    }
  });
}
