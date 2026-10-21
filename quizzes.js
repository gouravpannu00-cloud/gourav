// English Tutor - Quizzes JavaScript

let allQuizzes = [];
let currentQuiz = null;
let currentQuestionIndex = 0;
let userAnswers = [];
let quizQuestions = [];

async function loadQuizzes() {
    try {
        const data = await apiRequest('/quizzes');
        allQuizzes = data.quizzes;
        renderQuizzes(allQuizzes);
    } catch (error) {
        console.error('Failed to load quizzes:', error);
        const list = document.getElementById('quizList');
        if (list) list.innerHTML = '<p class="loading">Failed to load quizzes.</p>';
    }
}

function renderQuizzes(quizzes) {
    const list = document.getElementById('quizList');
    if (!list) return;

    if (quizzes.length === 0) {
        list.innerHTML = '<p class="empty-state">No quizzes available yet.</p>';
        return;
    }

    list.innerHTML = quizzes.map(quiz => `
        <div class="quiz-card" data-id="${quiz.id}">
            <div class="quiz-info">
                <h3>${quiz.title}</h3>
                <p>${quiz.category} - ${quiz.difficulty} - ${quiz.question_count} questions</p>
            </div>
            <button class="btn btn-primary start-quiz-btn" data-id="${quiz.id}">Start Quiz</button>
        </div>
    `).join('');

    // Add start quiz handlers
    list.querySelectorAll('.start-quiz-btn').forEach(btn => {
        btn.addEventListener('click', () => startQuiz(btn.dataset.id));
    });
}

async function startQuiz(quizId) {
    try {
        const data = await apiRequest(`/quizzes/${quizId}`);
        currentQuiz = data.quiz;
        quizQuestions = data.quiz.questions;
        currentQuestionIndex = 0;
        userAnswers = [];

        // Hide quiz list, show quiz container
        document.getElementById('quizList').classList.add('hidden');
        document.getElementById('quizContainer').classList.remove('hidden');
        document.getElementById('quizResults').classList.add('hidden');

        // Update quiz title
        document.getElementById('quizTitle').textContent = currentQuiz.title;

        // Show first question
        showQuestion();
    } catch (error) {
        console.error('Failed to start quiz:', error);
        alert('Failed to load quiz. Please try again.');
    }
}

function showQuestion() {
    if (currentQuestionIndex >= quizQuestions.length) {
        submitQuiz();
        return;
    }

    const question = quizQuestions[currentQuestionIndex];
    const questionCounter = document.getElementById('questionCounter');
    const questionText = document.getElementById('questionText');
    const questionOptions = document.getElementById('questionOptions');
    const questionInput = document.getElementById('questionInput');
    const fillBlankInput = document.getElementById('fillBlankInput');
    const nextBtn = document.getElementById('nextQuestionBtn');
    const submitBtn = document.getElementById('submitQuizBtn');

    // Update counter
    if (questionCounter) {
        questionCounter.textContent = `Question ${currentQuestionIndex + 1} of ${quizQuestions.length}`;
    }

    // Update question text
    if (questionText) {
        questionText.textContent = question.question;
    }

    // Clear previous selections
    userAnswers[currentQuestionIndex] = undefined;

    // Show appropriate input based on question type
    if (question.question_type === 'multiple_choice') {
        if (questionOptions) {
            questionOptions.classList.remove('hidden');
            questionOptions.innerHTML = question.options.map((option, index) => `
                <button class="option-btn" data-value="${option}">${String.fromCharCode(65 + index)}. ${option}</button>
            `).join('');

            // Add selection handlers
            questionOptions.querySelectorAll('.option-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    questionOptions.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));
                    this.classList.add('selected');
                    userAnswers[currentQuestionIndex] = this.dataset.value;
                });
            });
        }
        if (questionInput) questionInput.classList.add('hidden');
    } else if (question.question_type === 'fill_blank' || question.question_type === 'sentence_correction') {
        if (questionOptions) questionOptions.classList.add('hidden');
        if (questionInput) questionInput.classList.remove('hidden');
        if (fillBlankInput) {
            fillBlankInput.value = '';
            fillBlankInput.oninput = function() {
                userAnswers[currentQuestionIndex] = this.value;
            };
        }
    }

    // Update button visibility
    if (nextBtn && submitBtn) {
        if (currentQuestionIndex === quizQuestions.length - 1) {
            nextBtn.classList.add('hidden');
            submitBtn.classList.remove('hidden');
        } else {
            nextBtn.classList.remove('hidden');
            submitBtn.classList.add('hidden');
        }
    }
}

function nextQuestion() {
    if (userAnswers[currentQuestionIndex] === undefined) {
        alert('Please select or enter an answer before continuing.');
        return;
    }
    currentQuestionIndex++;
    showQuestion();
}

async function submitQuiz() {
    // Check all questions answered
    const unanswered = userAnswers.filter(a => a === undefined).length;
    if (unanswered > 0) {
        if (!confirm(`You have ${unanswered} unanswered questions. Submit anyway?`)) {
            return;
        }
    }

    try {
        const answers = {};
        userAnswers.forEach((answer, index) => {
            if (answer !== undefined) {
                answers[quizQuestions[index].id] = answer;
            }
        });

        const data = await apiRequest(`/quizzes/${currentQuiz.id}/submit`, {
            method: 'POST',
            body: JSON.stringify({ answers: answers })
        });

        showResults(data);
    } catch (error) {
        console.error('Failed to submit quiz:', error);
        alert('Failed to submit quiz. Please try again.');
    }
}

function showResults(data) {
    // Hide quiz container, show results
    document.getElementById('quizContainer').classList.add('hidden');
    document.getElementById('quizResults').classList.remove('hidden');

    // Update score display
    const resultScore = document.getElementById('resultScore');
    const resultLabel = document.getElementById('resultLabel');

    if (resultScore) resultScore.textContent = `${data.score}%`;
    if (resultLabel) resultLabel.textContent = `${data.correct} / ${data.total} correct`;

    // Show detailed results
    const resultsDetails = document.getElementById('resultsDetails');
    if (resultsDetails) {
        resultsDetails.innerHTML = data.results.map((result, index) => `
            <div class="result-item ${result.is_correct ? 'correct' : 'incorrect'}">
                <strong>Q${index + 1}:</strong> ${quizQuestions[index].question.substring(0, 80)}...
                ${!result.is_correct ? `<br><strong>Correct:</strong> ${result.correct_answer}` : ''}
            </div>
        `).join('');
    }
}

function retryQuiz() {
    startQuiz(currentQuiz.id);
}

function backToQuizzes() {
    document.getElementById('quizContainer').classList.add('hidden');
    document.getElementById('quizResults').classList.add('hidden');
    document.getElementById('quizList').classList.remove('hidden');
}

document.addEventListener('DOMContentLoaded', function() {
    // Next question button
    const nextBtn = document.getElementById('nextQuestionBtn');
    if (nextBtn) {
        nextBtn.addEventListener('click', nextQuestion);
    }

    // Submit quiz button
    const submitBtn = document.getElementById('submitQuizBtn');
    if (submitBtn) {
        submitBtn.addEventListener('click', submitQuiz);
    }

    // Back to quizzes button
    const backBtn = document.getElementById('backToQuizzes');
    if (backBtn) {
        backBtn.addEventListener('click', backToQuizzes);
    }

    // Retry quiz button
    const retryBtn = document.getElementById('retryQuizBtn');
    if (retryBtn) {
        retryBtn.addEventListener('click', retryQuiz);
    }

    // Back to quizzes button (from results)
    const backToQuizzesBtn = document.getElementById('backToQuizzesBtn');
    if (backToQuizzesBtn) {
        backToQuizzesBtn.addEventListener('click', backToQuizzes);
    }
});
