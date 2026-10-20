// English Tutor - Lessons JavaScript

let allLessons = [];
let currentLesson = null;

async function loadLessons() {
    try {
        const data = await apiRequest('/lessons');
        allLessons = data.lessons;
        renderLessons(allLessons);
    } catch (error) {
        console.error('Failed to load lessons:', error);
        const list = document.getElementById('lessonsList');
        if (list) list.innerHTML = '<p class="loading">Failed to load lessons. Please try again.</p>';
    }
}

function renderLessons(lessons) {
    const list = document.getElementById('lessonsList');
    if (!list) return;

    if (lessons.length === 0) {
        list.innerHTML = '<p class="empty-state">No lessons found.</p>';
        return;
    }

    list.innerHTML = lessons.map(lesson => `
        <div class="lesson-card ${lesson.user_progress && lesson.user_progress.completed ? 'completed' : ''}" 
             data-id="${lesson.id}">
            <h3>${lesson.title}</h3>
            <div class="lesson-meta">
                <span class="lesson-category">${lesson.category}</span>
                <span class="lesson-difficulty ${lesson.difficulty}">${lesson.difficulty}</span>
                ${lesson.user_progress && lesson.user_progress.completed ? '<span class="lesson-category" style="background: #dcfce7; color: #166534;">Completed</span>' : ''}
            </div>
        </div>
    `).join('');

    // Add click handlers
    document.querySelectorAll('.lesson-card').forEach(card => {
        card.addEventListener('click', () => openLesson(card.dataset.id));
    });
}

function openLesson(lessonId) {
    const lesson = allLessons.find(l => l.id == lessonId);
    if (!lesson) return;

    currentLesson = lesson;
    const modal = document.getElementById('lessonModal');
    const modalBody = document.getElementById('modalBody');

    if (modalBody) {
        modalBody.innerHTML = `
            <h2>${lesson.title}</h2>
            <div class="lesson-meta">
                <span class="lesson-category">${lesson.category}</span>
                <span class="lesson-difficulty ${lesson.difficulty}">${lesson.difficulty}</span>
            </div>
            ${lesson.content}
        `;
    }

    if (modal) modal.classList.remove('hidden');
}

function closeModal() {
    const modal = document.getElementById('lessonModal');
    if (modal) modal.classList.add('hidden');
    currentLesson = null;
}

async function completeLesson() {
    if (!currentLesson) return;

    try {
        await apiRequest(`/lessons/${currentLesson.id}/complete`, {
            method: 'POST'
        });

        // Update local state
        const lessonIndex = allLessons.findIndex(l => l.id === currentLesson.id);
        if (lessonIndex !== -1) {
            allLessons[lessonIndex].user_progress = { completed: true };
        }

        closeModal();
        renderLessons(allLessons);
    } catch (error) {
        console.error('Failed to complete lesson:', error);
        alert('Failed to mark lesson as complete. Please try again.');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            const category = this.dataset.category;
            if (category === 'all') {
                renderLessons(allLessons);
            } else {
                renderLessons(allLessons.filter(l => l.category === category));
            }
        });
    });

    // Modal close
    const modalClose = document.getElementById('modalClose');
    if (modalClose) {
        modalClose.addEventListener('click', closeModal);
    }

    const modal = document.getElementById('lessonModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) closeModal();
        });
    }

    // Complete lesson button
    const completeBtn = document.getElementById('completeLessonBtn');
    if (completeBtn) {
        completeBtn.addEventListener('click', completeLesson);
    }
});
