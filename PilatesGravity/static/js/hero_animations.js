// Animaciones para la sección hero
document.addEventListener('DOMContentLoaded', function() {
    
    // Función para crear efecto de máquina de escribir letra por letra
    function typewriterEffect(element, text, speed = 50) {
        return new Promise((resolve) => {
            if (!text || text.length === 0) {
                resolve();
                return;
            }
            
            element.innerHTML = '';
            element.style.opacity = '1';
            
            // Crear un cursor temporal
            const cursor = document.createElement('span');
            cursor.className = 'typewriter-cursor';
            cursor.innerHTML = '';
            element.appendChild(cursor);
            
            let i = 0;
            const timer = setInterval(() => {
                if (i < text.length) {
                    // Crear span para cada letra
                    const letter = document.createElement('span');
                    letter.textContent = text.charAt(i);
                    letter.style.animationDelay = '0s';
                    
                    // Insertar letra antes del cursor
                    element.insertBefore(letter, cursor);
                    i++;
                } else {
                    clearInterval(timer);
                    // Remover cursor después de un momento
                    setTimeout(() => {
                        if (cursor && cursor.parentNode) {
                            cursor.remove();
                        }
                        resolve();
                    }, 150);
                }
            }, speed);
        });
    }

    // Función para animar múltiples líneas de texto
    async function animateTitle(titleElement) {
        // Usar siempre el contenido original guardado
        const originalHTML = titleElement.dataset.originalContent || titleElement.innerHTML;
        
        // Si no tenemos el original guardado, guardarlo ahora
        if (!titleElement.dataset.originalContent) {
            titleElement.dataset.originalContent = originalHTML;
        }
        
        // Separar las líneas por <br>
        const lines = originalHTML.split('<br>');
        
        // Crear contenedor para las líneas
        titleElement.innerHTML = '';
        
        for (let i = 0; i < lines.length; i++) {
            const lineDiv = document.createElement('div');
            lineDiv.className = `typewriter-line ${i > 0 ? 'second-line' : ''}`;
            titleElement.appendChild(lineDiv);
            
            let lineText = '';
            let hasSpan = false;
            
            // Procesar cada línea
            if (lines[i].includes('<span>') && lines[i].includes('</span>')) {
                // Línea con span (segunda línea normalmente)
                const spanMatch = lines[i].match(/<span[^>]*>(.*?)<\/span>/);
                if (spanMatch) {
                    hasSpan = true;
                    lineText = spanMatch[1].trim(); // Solo el texto dentro del span
                }
            } else {
                // Línea normal (primera línea normalmente)
                // Simplemente limpiar HTML tags y espacios extra
                lineText = lines[i].replace(/<[^>]*>/g, '').trim();
                
                // Limpiar caracteres invisibles adicionales
                lineText = lineText.replace(/[\u200B-\u200D\uFEFF]/g, '');
            }
            
            // Escribir el texto letra por letra
            if (lineText && lineText.length > 0) {
                await typewriterEffect(lineDiv, lineText, 50);
                
                // Si tenía span, aplicar el estilo después de escribir
                if (hasSpan) {
                    lineDiv.innerHTML = `<span style="color: #5D768B;">${lineText}</span>`;
                }
            }
            
            // Pausa entre líneas
            if (i < lines.length - 1) {
                await new Promise(resolve => setTimeout(resolve, 150));
            }
        }
    }
    
    // Función para iniciar las animaciones
    async function startHeroAnimations() {
        const heroSection = document.querySelector('.hero-section');
        if (!heroSection) return;

        // Verificar si ya están activas las animaciones para evitar duplicados
        if (heroSection.classList.contains('animations-active')) {
            return;
        }

        // Agregar clase para activar animaciones
        heroSection.classList.add('animations-active');

        const heroTitle = heroSection.querySelector('.hero-text h1');
        const heroDescription = heroSection.querySelector('.hero-text p');
        const heroButtons = heroSection.querySelector('.hero-buttons');
        const heroImage = heroSection.querySelector('.hero-image');
        const waves = heroSection.querySelectorAll('.wave');

        // Ocultar inicialmente todos los elementos excepto el título
        if (heroDescription) {
            heroDescription.style.opacity = '0';
            heroDescription.style.transform = 'translateY(30px)';
        }
        if (heroButtons) {
            heroButtons.style.opacity = '0';
            heroButtons.style.transform = 'translateY(20px)';
        }
        if (heroImage) {
            heroImage.style.opacity = '0';
            heroImage.style.transform = 'scale(0.8)';
        }

        // Animar el título primero
        if (heroTitle) {
            // Verificar si ya tiene el contenido original guardado
            if (!heroTitle.dataset.originalContent) {
                heroTitle.dataset.originalContent = heroTitle.innerHTML;
            }
            
            await animateTitle(heroTitle);
            
            // Pequeña pausa después del título
            await new Promise(resolve => setTimeout(resolve, 100));
        }

        // Después del título, animar otros elementos secuencialmente
        if (heroDescription) {
            heroDescription.classList.add('fade-in-up');
            // Espera a que termine la animación del párrafo
            await new Promise(resolve => setTimeout(resolve, 150));
        }

        if (heroButtons) {
            heroButtons.classList.add('slide-in-buttons');
        }

        if (heroImage) {
            heroImage.classList.add('scale-in-image');
        }

        // Anima las ondas del fondo
        waves.forEach((wave, index) => {
            wave.classList.add('wave-animation');
            if (index === 1) {
                wave.classList.add('wave2');
            }
        });
    }

    // Función para reiniciar animaciones
    function resetAnimations() {
        const heroSection = document.querySelector('.hero-section');
        if (!heroSection) return;

        heroSection.classList.remove('animations-active');
        
        // Restaurar contenido original del título
        const heroTitle = heroSection.querySelector('.hero-text h1');
        if (heroTitle && heroTitle.dataset.originalContent) {
            heroTitle.innerHTML = heroTitle.dataset.originalContent;
        }
        
        // Remover clases de animación
        const animatedElements = heroSection.querySelectorAll('.fade-in-up, .slide-in-buttons, .scale-in-image, .wave-animation');
        animatedElements.forEach(el => {
            el.classList.remove('fade-in-up', 'slide-in-buttons', 'scale-in-image', 'wave-animation', 'wave2');
        });
    }

    // Observador de intersección para activar animaciones cuando la sección sea visible
    const observerOptions = {
        threshold: 0.15,
        rootMargin: '0px 0px -50px 0px'
    };

    const heroObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.classList.contains('animations-active')) {
                startHeroAnimations();
            }
        });
    }, observerOptions);

    // Observar la sección hero
    const heroSection = document.querySelector('.hero-section');
    if (heroSection) {
        // Guardar contenido original del título
        const heroTitle = heroSection.querySelector('.hero-text h1');
        if (heroTitle) {
            heroTitle.dataset.originalContent = heroTitle.innerHTML;
        }
        
        heroObserver.observe(heroSection);
    }

    // Iniciar animaciones inmediatamente si la sección ya está visible
    if (heroSection) {
        const rect = heroSection.getBoundingClientRect();
        const isVisible = rect.top < window.innerHeight && rect.bottom > 0;
        
        if (isVisible) {
            setTimeout(() => {
                startHeroAnimations();
            }, 150); // Pequeño retraso para mejor UX
        }
    }

    // Opcional: Función para activar animaciones manualmente
    window.startHeroAnimations = startHeroAnimations;
    window.resetHeroAnimations = resetAnimations;
});

// Función mejorada para efecto de escritura letra por letra
function advancedTypewriter(element, text, speed = 50) {
    return new Promise((resolve) => {
        if (!element) {
            resolve();
            return;
        }
        
        element.innerHTML = '';
        element.style.opacity = '1';
        
        // Crear cursor temporal
        const cursor = document.createElement('span');
        cursor.className = 'typewriter-cursor';
        cursor.textContent = '|';
        element.appendChild(cursor);
        
        let i = 0;
        const timer = setInterval(() => {
            if (i < text.length) {
                const letter = document.createElement('span');
                letter.textContent = text.charAt(i);
                letter.style.opacity = '0';
                letter.style.animation = `letterReveal 0.1s ease-in-out forwards`;
                
                element.insertBefore(letter, cursor);
                i++;
            } else {
                clearInterval(timer);
                setTimeout(() => {
                    if (cursor.parentNode) {
                        cursor.remove();
                    }
                    resolve();
                }, 150);
            }
        }, speed);
    });
}

// Función para animar elementos con retraso escalonado
function staggeredAnimation(elements, animationClass, delay = 50) {
    elements.forEach((element, index) => {
        setTimeout(() => {
            element.classList.add(animationClass);
        }, index * delay);
    });
}