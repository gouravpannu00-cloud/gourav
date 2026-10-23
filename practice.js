// English Tutor - Practice JavaScript

let currentTab = 'speaking';

async function loadPracticeContent() {
    await Promise.all([
        loadSpeakingScenarios(),
        loadWritingPrompts(),
        loadInterviewQuestions(),
        loadReadingArticles()
    ]);
}

async function loadSpeakingScenarios() {
    try {
        const data = await apiRequest('/practice/speaking');
        const list = document.getElementById('scenarioList');
        if (!list) return;

        list.innerHTML = data.scenarios.map(scenario => `
            <div class="scenario-card" data-id="${scenario.id}">
                <h3>${scenario.title}</h3>
                <p class="scenario-text">${scenario.scenario}</p>
                <button class="reveal-btn" data-target="answer-${scenario.id}">Show Sample Answer</button>
                <div class="sample-answer hidden" id="answer-${scenario.id}">
                    <h4>Sample Response:</h4>
                    <p>${scenario.sample_response}</p>
                    <p class="tips"><strong>Tips:</strong> ${scenario.tips}</p>
                </div>
            </div>
        `).join('');

        // Add reveal handlers
        list.querySelectorAll('.reveal-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const target = document.getElementById(this.dataset.target);
                if (target) {
                    target.classList.toggle('hidden');
                    this.textContent = target.classList.contains('hidden') ? 'Show Sample Answer' : 'Hide Sample Answer';
                }
            });
        });
    } catch (error) {
        console.error('Failed to load speaking scenarios:', error);
    }
}

async function loadWritingPrompts() {
    try {
        const data = await apiRequest('/practice/writing/prompts');
        const container = document.getElementById('writingPrompts');
        if (!container) return;

        container.innerHTML = data.prompts.map(prompt => `
            <div class="prompt-card" data-id="${prompt.id}" data-type="${prompt.type}" data-prompt="${encodeURIComponent(prompt.prompt)}">
                <span class="prompt-type">${prompt.type}</span>
                <p>${prompt.prompt}</p>
            </div>
        `).join('');

        // Add click handlers
        container.querySelectorAll('.prompt-card').forEach(card => {
            card.addEventListener('click', function() {
                const promptText = decodeURIComponent(this.dataset.prompt);
                const promptType = this.dataset.type;
                showWritingArea(promptText, promptType);
            });
        });
    } catch (error) {
        console.error('Failed to load writing prompts:', error);
    }
}

function showWritingArea(promptText, promptType) {
    const writingArea = document.getElementById('writingArea');
    const promptTitle = document.getElementById('writingPromptTitle');
    const promptDisplay = document.getElementById('writingPromptText');

    if (writingArea) writingArea.classList.remove('hidden');
    if (promptTitle) promptTitle.textContent = `Writing Practice: ${promptType}`;
    if (promptDisplay) promptText;

    // Store current prompt for submission
    writingArea.dataset.prompt = promptText;
    writingArea.dataset.type = promptType;
}

async function submitWriting() {
    const writingArea = document.getElementById('writingArea');
    const submission = document.getElementById('writingSubmission');

    if (!writingArea || !submission) return;

    const prompt = writingArea.dataset.prompt;
    const type = writingArea.dataset.type;
    const text = submission.value.trim();

    if (!text) {
        alert('Please write your response before submitting.');
        return;
    }

    try {
        await apiRequest('/practice/writing/submit', {
            method: 'POST',
            body: JSON.stringify({
                prompt: prompt,
                submission: text,
                type: type
            })
        });

        alert('Your submission has been received! Practice reviewing it with the AI Tutor for feedback.');
        submission.value = '';
    } catch (error) {
        console.error('Failed to submit writing:', error);
        alert('Failed to submit. Please try again.');
    }
}

async function loadInterviewQuestions() {
    try {
        const data = await apiRequest('/interview/questions');
        const list = document.getElementById('interviewList');
        if (!list) return;

        list.innerHTML = data.questions.map(q => `
            <div class="interview-card" data-id="${q.id}">
                <h3>${q.question}</h3>
                <p class="lesson-meta">
                    <span class="lesson-category">${q.category}</span>
                    <span class="lesson-difficulty ${q.difficulty}">${q.difficulty}</span>
                </p>
                <button class="reveal-btn" data-target="interview-${q.id}">Show Sample Answer</button>
                <div class="sample-answer hidden" id="interview-${q.id}">
                    <h4>Sample Answer:</h4>
                    <p>${q.sample_answer}</p>
                    <p class="tips"><strong>Tips:</strong> ${q.tips}</p>
                </div>
            </div>
        `).join('');

        // Add reveal handlers
        list.querySelectorAll('.reveal-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const target = document.getElementById(this.dataset.target);
                if (target) {
                    target.classList.toggle('hidden');
                    this.textContent = target.classList.contains('hidden') ? 'Show Sample Answer' : 'Hide Sample Answer';
                }
            });
        });
    } catch (error) {
        console.error('Failed to load interview questions:', error);
    }
}

async function loadReadingArticles() {
    try {
        const data = await apiRequest('/reading/articles');
        const list = document.getElementById('articleList');
        if (!list) return;

        list.innerHTML = data.articles.map(article => `
            <div class="article-card" data-id="${article.id}">
                <h3>${article.title}</h3>
                <p class="lesson-meta">
                    <span class="lesson-category">${article.category}</span>
                    <span class="lesson-difficulty ${article.difficulty}">${article.difficulty}</span>
                    <span class="lesson-category">${article.reading_time_minutes} min read</span>
                </p>
                <button class="reveal-btn" data-target="article-${article.id}">Read Article</button>
                <div class="sample-answer hidden" id="article-${article.id}">
                    <p style="white-space: pre-wrap;">${article.content}</p>
                </div>
            </div>
        `).join('');

        // Add reveal handlers
        list.querySelectorAll('.reveal-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const target = document.getElementById(this.dataset.target);
                if (target) {
                    target.classList.toggle('hidden');
                    this.textContent = target.classList.contains('hidden') ? 'Read Article' : 'Hide Article';
                }
            });
        });
    } catch (error) {
        console.error('Failed to load reading articles:', error);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const tab = this.dataset.tab;
            currentTab = tab;

            // Update active tab
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            // Show/hide tab content
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.add('hidden');
            });
            const tabContent = document.getElementById(`${tab}Tab`);
            if (tabContent) tabContent.classList.remove('hidden');
        });
    });

    // Submit writing button
    const submitBtn = document.getElementById('submitWritingBtn');
    if (submitBtn) {
        submitBtn.addEventListener('click', submitWriting);
    }
});
