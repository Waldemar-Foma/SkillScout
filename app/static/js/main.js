// app/static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navMenu = document.querySelector('.nav-menu');
    
    if (mobileMenuBtn && navMenu) {
        mobileMenuBtn.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            this.querySelector('i').classList.toggle('fa-times');
            this.querySelector('i').classList.toggle('fa-bars');
        });
    }

    const videoUpload = document.getElementById('video_resume');
    if (videoUpload) {
        videoUpload.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (!file) return;
            
            if (!file.type.match('video.*')) {
                showAlert('Пожалуйста, выберите видео файл (MP4, MOV, AVI)', 'error');
                this.value = '';
                return;
            }

            if (file.size > 100 * 1024 * 1024) {
                showAlert('Максимальный размер файла - 100MB', 'error');
                this.value = '';
                return;
            }

            const previewContainer = document.querySelector('.video-widget');
            const oldPreview = previewContainer.querySelector('.video-preview');
            if (oldPreview) oldPreview.remove();

            const preview = document.createElement('video');
            preview.controls = true;
            preview.className = 'video-preview';
            preview.innerHTML = 'Ваш браузер не поддерживает видео превью';

            const reader = new FileReader();
            reader.onload = function(e) {
                preview.src = e.target.result;
                previewContainer.insertBefore(preview, videoUpload.nextSibling);
                
                const info = document.createElement('div');
                info.className = 'video-info';
                info.innerHTML = `
                    <p>${file.name}</p>
                    <p>${(file.size / (1024 * 1024)).toFixed(1)} MB</p>
                `;
                previewContainer.appendChild(info);
            }
            reader.readAsDataURL(file);
        });
    }

    const mbtiSelects = document.querySelectorAll('select[name="mbti_type"]');
    mbtiSelects.forEach(select => {
        select.addEventListener('change', function() {
            const description = getMBTIDescription(this.value);
            if (description) {
                showMBTITooltip(this, description);
            }
        });

        if (select.value) {
            const description = getMBTIDescription(select.value);
            if (description) {
                showMBTITooltip(select, description);
            }
        }
    });

    const traitSliders = document.querySelectorAll('.trait-slider');
    traitSliders.forEach(slider => {
        slider.addEventListener('input', function() {
            const value = this.value;
            const traitId = this.dataset.trait;
            updateTraitValue(traitId, value);
        });
    });

    const ajaxForms = document.querySelectorAll('form.ajax-form');
    ajaxForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            submitFormViaAJAX(this);
        });
    });
});

function getMBTIDescription(type) {
    const descriptions = {
        'INTJ': {
            title: 'Стратег (INTJ)',
            desc: 'Аналитичный, решительный, независимый. Обладают богатым воображением и решительностью.',
            strengths: 'Стратегическое мышление, высокая компетентность, независимость',
            weaknesses: 'Высокомерие, пренебрежение эмоциями, перфекционизм'
        },
        'INTP': {
            title: 'Логик (INTP)',
            desc: 'Изобретательный, логичный, любознательный. Любят теорию и абстрактные концепции.',
            strengths: 'Аналитический ум, оригинальность, открытость',
            weaknesses: 'Непрактичность, замкнутость, излишняя критичность'
        },
        'ENTJ': {
            title: 'Командир (ENTJ)',
            desc: 'Решительный, общительный, целеустремленный. Прирожденные лидеры.',
            strengths: 'Эффективность, уверенность, стратегическое мышление',
            weaknesses: 'Нетерпимость, авторитарность, нетерпеливость'
        },
        'ENTP': {
            title: 'Полемист (ENTP)',
            desc: 'Умный, любознательный, изобретательный. Любят интеллектуальные вызовы.',
            strengths: 'Быстрота мышления, оригинальность, обаяние',
            weaknesses: 'Непоследовательность, нетерпеливость, несдержанность'
        },
        'INFJ': {
            title: 'Активист (INFJ)',
            desc: 'Проницательный, принципиальный, вдохновляющий. Редкий и духовно развитый тип.',
            strengths: 'Творчество, проницательность, принципиальность',
            weaknesses: 'Чувствительность к критике, перфекционизм, склонность к выгоранию'
        },
        'INFP': {
            title: 'Посредник (INFP)',
            desc: 'Поэтичный, добрый, альтруистичный. Всегда ищут гармонию.',
            strengths: 'Эмпатия, креативность, идеализм',
            weaknesses: 'Излишняя чувствительность, нерешительность, перфекционизм'
        },
        'ENFJ': {
            title: 'Тренер (ENFJ)',
            desc: 'Харизматичный, общительный, альтруистичный. Прирожденные наставники.',
            strengths: 'Лидерские качества, эмпатия, обаяние',
            weaknesses: 'Чрезмерная идеализация, навязчивость, чувствительность к критике'
        },
        'ENFP': {
            title: 'Борец (ENFP)',
            desc: 'Энергичный, творческий, общительный. Вдохновляют окружающих.',
            strengths: 'Энтузиазм, креативность, коммуникабельность',
            weaknesses: 'Неорганизованность, эмоциональная нестабильность, чрезмерная разговорчивость'
        },
        'ISTJ': {
            title: 'Администратор (ISTJ)',
            desc: 'Практичный, фактологичный, надежный. Ответственные и стабильные.',
            strengths: 'Надежность, практичность, организованность',
            weaknesses: 'Упрямство, негибкость, излишний консерватизм'
        },
        'ISFJ': {
            title: 'Защитник (ISFJ)',
            desc: 'Внимательный, надежный, заботливый. Защищают то, что важно для них.',
            strengths: 'Преданность, практичность, чуткость',
            weaknesses: 'Скромность, сопротивление изменениям, склонность к самопожертвованию'
        },
        'ESTJ': {
            title: 'Менеджер (ESTJ)',
            desc: 'Организованный, традиционный, ответственный. Отличные управленцы.',
            strengths: 'Организованность, надежность, практичность',
            weaknesses: 'Негибкость, нетерпимость, излишняя прямолинейность'
        },
        'ESFJ': {
            title: 'Консул (ESFJ)',
            desc: 'Заботливый, общительный, популярный. Всегда помогают другим.',
            strengths: 'Чуткость, практичность, надежность',
            weaknesses: 'Чрезмерная чувствительность, зависимость от признания, консерватизм'
        },
        'ISTP': {
            title: 'Виртуоз (ISTP)',
            desc: 'Смелый, практичный, экспериментатор. Мастера на все руки.',
            strengths: 'Оптимизм, спонтанность, практичность',
            weaknesses: 'Рискованность, непредсказуемость, сопротивление обязательствам'
        },
        'ISFP': {
            title: 'Артист (ISFP)',
            desc: 'Гибкий, очаровательный, чувствительный. Наслаждаются моментом.',
            strengths: 'Чуткость, креативность, адаптивность',
            weaknesses: 'Излишняя независимость, непредсказуемость, избегание конфликтов'
        },
        'ESTP': {
            title: 'Делец (ESTP)',
            desc: 'Энергичный, проницательный, общительный. Умеют находить возможности.',
            strengths: 'Энергичность, практичность, общительность',
            weaknesses: 'Импульсивность, нетерпеливость, склонность к риску'
        },
        'ESFP': {
            title: 'Развлекатель (ESFP)',
            desc: 'Спонтанный, энергичный, общительный. Любят быть в центре внимания.',
            strengths: 'Энергичность, практичность, общительность',
            weaknesses: 'Плохое планирование, чувствительность к критике, потребность во внимании'
        }
    };
    return descriptions[type] || null;
}

function showMBTITooltip(element, data) {
    const existingTooltip = document.getElementById('mbti-tooltip');
    if (existingTooltip) existingTooltip.remove();

    const tooltip = document.createElement('div');
    tooltip.id = 'mbti-tooltip';
    tooltip.className = 'mbti-tooltip';
    tooltip.innerHTML = `
        <div class="mbti-tooltip-header">
            <h4>${data.title}</h4>
            <button class="close-tooltip">&times;</button>
        </div>
        <div class="mbti-tooltip-body">
            <p>${data.desc}</p>
            <div class="mbti-traits">
                <div class="mbti-strengths">
                    <h5>Сильные стороны:</h5>
                    <p>${data.strengths}</p>
                </div>
                <div class="mbti-weaknesses">
                    <h5>Слабые стороны:</h5>
                    <p>${data.weaknesses}</p>
                </div>
            </div>
        </div>
    `;

    const rect = element.getBoundingClientRect();
    tooltip.style.position = 'absolute';
    tooltip.style.top = `${rect.bottom + window.scrollY + 10}px`;
    tooltip.style.left = `${rect.left + window.scrollX}px`;

    tooltip.querySelector('.close-tooltip').addEventListener('click', function() {
        tooltip.remove();
    });

    document.body.appendChild(tooltip);

    setTimeout(() => {
        document.addEventListener('click', function closeTooltip(e) {
            if (!tooltip.contains(e.target) && e.target !== element) {
                tooltip.remove();
                document.removeEventListener('click', closeTooltip);
            }
        });
    }, 100);
}

function updateTraitValue(traitId, value) {
    const valueElement = document.querySelector(`.trait-value[data-trait="${traitId}"]`);
    if (valueElement) {
        valueElement.textContent = `${value}%`;
        
        const progressBar = document.querySelector(`.trait-progress[data-trait="${traitId}"]`);
        if (progressBar) {
            progressBar.style.width = `${value}%`;
            
            if (value < 30) {
                progressBar.style.backgroundColor = 'var(--error)';
            } else if (value < 70) {
                progressBar.style.backgroundColor = 'var(--accent-green)';
            } else {
                progressBar.style.backgroundColor = 'var(--primary-blue)';
            }
        }
    }
}

function showAlert(message, type = 'info') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    document.body.appendChild(alert);
    
    setTimeout(() => {
        alert.classList.add('fade-out');
        setTimeout(() => alert.remove(), 500);
    }, 3000);
}

function submitFormViaAJAX(form) {
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Отправка...';
    
    fetch(form.action, {
        method: form.method,
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(data.message || 'Успешно сохранено', 'success');
            if (data.redirect) {
                window.location.href = data.redirect;
            }
        } else {
            showAlert(data.message || 'Произошла ошибка', 'error');
        }
    })
    .catch(error => {
        showAlert('Ошибка сети. Попробуйте позже.', 'error');
        console.error('Error:', error);
    })
    .finally(() => {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    });
}

function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(el => {
        el.addEventListener('mouseenter', showTooltip);
        el.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    const tooltipText = this.dataset.tooltip;
    const tooltip = document.createElement('div');
    tooltip.className = 'custom-tooltip';
    tooltip.textContent = tooltipText;
    
    document.body.appendChild(tooltip);
    
    const rect = this.getBoundingClientRect();
    tooltip.style.left = `${rect.left + rect.width / 2 - tooltip.offsetWidth / 2}px`;
    tooltip.style.top = `${rect.top - tooltip.offsetHeight - 10}px`;
    
    this.tooltip = tooltip;
}

function hideTooltip() {
    if (this.tooltip) {
        this.tooltip.remove();
        this.tooltip = null;
    }
}