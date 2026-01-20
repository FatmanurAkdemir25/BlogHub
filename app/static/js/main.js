// Flash mesajlarını otomatik kapatma
document.addEventListener('DOMContentLoaded', function() {
    // Flash mesajları için kapatma butonu
    const closeButtons = document.querySelectorAll('.close-alert');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.parentElement.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                this.parentElement.remove();
            }, 300);
        });
    });

    // Flash mesajlarını 5 saniye sonra otomatik kapat
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });

    // Görsel önizleme fonksiyonu
    const imageInputs = document.querySelectorAll('input[type="file"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    const preview = document.getElementById('imagePreview');
                    if (preview) {
                        preview.innerHTML = `<img src="${event.target.result}" alt="Önizleme">`;
                        preview.style.display = 'block';
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    });

    // Smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Navbar scroll efekti
    const navbar = document.querySelector('.navbar');
    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll > 100) {
            navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.15)';
        } else {
            navbar.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.08)';
        }

        lastScroll = currentScroll;
    });

    // Textarea otomatik boyutlandırma
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });

    // Form validasyonu
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredInputs = form.querySelectorAll('[required]');
            let isValid = true;

            requiredInputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.style.borderColor = '#ef4444';
                } else {
                    input.style.borderColor = '#e5e7eb';
                }
            });

            if (!isValid) {
                e.preventDefault();
                alert('Lütfen tüm gerekli alanları doldurun!');
            }
        });
    });

    // Görsel lazy loading
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));

    // Arama formu AJAX (opsiyonel)
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        const searchInput = searchForm.querySelector('.search-input');
        let searchTimeout;

        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                // Burada AJAX ile arama yapabilirsiniz
                console.log('Arama:', this.value);
            }, 500);
        });
    }

    // Karakter sayacı
    const summaryTextarea = document.querySelector('textarea[name="summary"]');
    if (summaryTextarea) {
        const maxLength = summaryTextarea.getAttribute('maxlength');
        const counter = document.createElement('small');
        counter.style.display = 'block';
        counter.style.marginTop = '0.5rem';
        counter.style.color = '#6b7280';
        summaryTextarea.parentNode.appendChild(counter);

        function updateCounter() {
            const remaining = maxLength - summaryTextarea.value.length;
            counter.textContent = `${remaining} karakter kaldı`;
            counter.style.color = remaining < 50 ? '#ef4444' : '#6b7280';
        }

        summaryTextarea.addEventListener('input', updateCounter);
        updateCounter();
    }

    // Paylaşım butonları
    const shareButtons = document.querySelectorAll('.share-btn');
    shareButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const url = encodeURIComponent(window.location.href);
            const title = encodeURIComponent(document.title);
            let shareUrl = '';

            if (this.classList.contains('twitter')) {
                shareUrl = `https://twitter.com/intent/tweet?url=${url}&text=${title}`;
            } else if (this.classList.contains('facebook')) {
                shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}`;
            } else if (this.classList.contains('linkedin')) {
                shareUrl = `https://www.linkedin.com/shareArticle?mini=true&url=${url}&title=${title}`;
            } else if (this.classList.contains('whatsapp')) {
                shareUrl = `https://wa.me/?text=${title}%20${url}`;
            }

            if (shareUrl) {
                window.open(shareUrl, '_blank', 'width=600,height=400');
            }
        });
    });

    // Animasyonlar
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const fadeInObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease forwards';
                fadeInObserver.unobserve(entry.target);
            }
        });
    }, observerOptions);

    const animatedElements = document.querySelectorAll('.post-card, .sidebar-widget');
    animatedElements.forEach(el => fadeInObserver.observe(el));
});

// Slideout animasyonu için CSS ekle
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100px);
        }
    }
`;
document.head.appendChild(style);