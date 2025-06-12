// JavaScript para controlar las animaciones de scroll
document.addEventListener('DOMContentLoaded', function() {
    // Configuración del Intersection Observer
    const observerOptions = {
        root: null,
        rootMargin: '0px 0px -20% 0px',
        threshold: [0, 0.1, 0.25, 0.5, 0.75, 1]
    };

    // Observer para las secciones principales
    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            const section = entry.target;
            
            if (entry.isIntersecting) {
                // Sección está entrando en vista
                section.classList.add('fade-in', 'animate-in');
                section.classList.remove('fade-out');
                
                // Añadir efecto de superposición si no es la primera sección
                if (!section.classList.contains('hero-section')) {
                    section.classList.add('overlapping');
                }
            } else {
                // Sección está saliendo de vista
                if (entry.boundingClientRect.top < 0) {
                    // Sección se está moviendo hacia arriba
                    section.classList.add('slide-up', 'fade-out');
                    section.classList.remove('fade-in');
                } else {
                    // Sección se está moviendo hacia abajo
                    section.classList.remove('slide-up', 'overlapping', 'animate-in');
                }
            }
        });
    }, observerOptions);

    // Observer para elementos individuales dentro de secciones
    const elementObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -10% 0px'
    });

    // Aplicar clases a las secciones existentes
    const sections = document.querySelectorAll('section');
    sections.forEach(section => {
        section.classList.add('scroll-overlay-section');
        sectionObserver.observe(section);

        // Observar elementos internos para animaciones adicionales
        const elementsToAnimate = section.querySelectorAll('.section-title, .benefit-card, .classes-card, .card_instructors, .contact-card, .faq-item');
        elementsToAnimate.forEach(element => {
            element.classList.add('fade-in-element');
            elementObserver.observe(element);
        });
    });

    // Función para suavizar el scroll
    function smoothScrollTo(targetPosition) {
        const startPosition = window.pageYOffset;
        const distance = targetPosition - startPosition;
        const duration = 500;
        let start = null;

        function animation(currentTime) {
            if (start === null) start = currentTime;
            const timeElapsed = currentTime - start;
            const run = ease(timeElapsed, startPosition, distance, duration);
            window.scrollTo(0, run);
            if (timeElapsed < duration) requestAnimationFrame(animation);
        }

        function ease(t, b, c, d) {
            t /= d / 2;
            if (t < 1) return c / 2 * t * t + b;
            t--;
            return -c / 2 * (t * (t - 2) - 1) + b;
        }

        requestAnimationFrame(animation);
    }

    // Mejorar navegación suave para enlaces internos
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const targetPosition = target.offsetTop - 80; // Ajuste para header fijo
                smoothScrollTo(targetPosition);
            }
        });
    });

    // Efectos adicionales al hacer scroll
    let ticking = false;
    function updateScrollEffects() {
        const scrolled = window.pageYOffset;
        const rate = scrolled * -0.5;

        // Paralaje sutil en el hero
        const heroSection = document.querySelector('.hero-section');
        if (heroSection && scrolled < window.innerHeight) {
            heroSection.style.transform = `translateY(${rate}px)`;
        }

        ticking = false;
    }

    function requestTick() {
        if (!ticking) {
            requestAnimationFrame(updateScrollEffects);
            ticking = true;
        }
    }

    window.addEventListener('scroll', requestTick);
});