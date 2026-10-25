// English Tutor - Progress JavaScript

async function loadProgress() {
    try {
        const data = await apiRequest('/progress');
        updateProgressUI(data);
    } catch (error) {
        console.error('Failed to load progress:', error);
    }
}

function updateProgressUI(data) {
    // Update lessons progress
    const lessonsPercent = document.getElementById('lessonsPercent');
    const lessonsDetail = document.getElementById('lessonsDetail');
    const lessonsCircle = document.getElementById('lessonsCircle');

    if (lessonsPercent) lessonsPercent.textContent = `${data.lessons.percentage}%`;
    if (lessonsDetail) lessonsDetail.textContent = `${data.lessons.completed} of ${data.lessons.total} completed`;

    // Update circular progress (stroke-dashoffset: 283 is empty, 0 is full)
    if (lessonsCircle) {
        const offset = 283 - (283 * data.lessons.percentage / 100);
        lessonsCircle.style.strokeDashoffset = offset;
    }

    // Update quiz stats
    const quizAttempts = document.getElementById('quizAttempts');
    const quizAvg = document.getElementById('quizAvg');
    const quizBest = document.getElementById('quizBest');

    if (quizAttempts) quizAttempts.textContent = data.quizzes.attempts;
    if (quizAvg) quizAvg.textContent = `${data.quizzes.average_score}%`;
    if (quizBest) quizBest.textContent = `${data.quizzes.best_score}%`;

    // Update vocabulary progress
    const vocabPercent = document.getElementById('vocabPercent');
    const vocabDetail = document.getElementById('vocabDetail');
    const vocabCircle = document.getElementById('vocabCircle');

    if (vocabPercent) vocabPercent.textContent = `${data.vocabulary.percentage}%`;
    if (vocabDetail) vocabDetail.textContent = `${data.vocabulary.mastered} of ${data.vocabulary.total} mastered`;

    if (vocabCircle) {
        const offset = 283 - (283 * data.vocabulary.percentage / 100);
        vocabCircle.style.strokeDashoffset = offset;
    }

    // Update quiz history table
    const historyBody = document.getElementById('historyBody');
    if (historyBody && data.recent_quizzes && data.recent_quizzes.length > 0) {
        historyBody.innerHTML = data.recent_quizzes.map(quiz => {
            const date = new Date(quiz.completed_at).toLocaleDateString();
            return `
                <tr>
                    <td>Quiz #${quiz.quiz_id}</td>
                    <td>${quiz.score}%</td>
                    <td>${date}</td>
                </tr>
            `;
        }).join('');
    }
}
