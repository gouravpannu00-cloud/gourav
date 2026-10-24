// English Tutor - Vocabulary JavaScript

let allVocabulary = [];
let reviewQueue = [];
let currentReviewIndex = 0;

async function loadVocabulary() {
    try {
        const data = await apiRequest('/vocabulary');
        allVocabulary = data.vocabulary;
        renderVocabulary(allVocabulary);
    } catch (error) {
        console.error('Failed to load vocabulary:', error);
        const list = document.getElementById('vocabList');
        if (list) list.innerHTML = '<p class="loading">Failed to load vocabulary.</p>';
    }
}

function renderVocabulary(vocabList) {
    const list = document.getElementById('vocabList');
    if (!list) return;

    if (vocabList.length === 0) {
        list.innerHTML = '<p class="empty-state">No vocabulary found.</p>';
        return;
    }

    list.innerHTML = vocabList.map(vocab => {
        const mastery = vocab.mastery;
        let masteryClass = 'new';
        let masteryText = 'New';

        if (mastery) {
            if (mastery.mastery_level >= 3) {
                masteryClass = 'mastered';
                masteryText = 'Mastered';
            } else if (mastery.mastery_level > 0) {
                masteryClass = 'learning';
                masteryText = 'Learning';
            }
        }

        return `
            <div class="vocab-card" data-id="${vocab.id}">
                <div class="vocab-word">${vocab.word}</div>
                <div class="vocab-definition">${vocab.definition}</div>
                ${vocab.example ? `<div class="vocab-example">"${vocab.example}"</div>` : ''}
                <div class="vocab-meta">
                    <span class="lesson-category">${vocab.category}</span>
                    <span class="mastery-badge ${masteryClass}">${masteryText}</span>
                </div>
            </div>
        `;
    }).join('');
}

function filterVocabulary(category) {
    if (category === 'all') {
        renderVocabulary(allVocabulary);
    } else {
        renderVocabulary(allVocabulary.filter(v => v.category === category));
    }
}

function searchVocabulary(query) {
    const lowerQuery = query.toLowerCase();
    const filtered = allVocabulary.filter(v =>
        v.word.toLowerCase().includes(lowerQuery) ||
        v.definition.toLowerCase().includes(lowerQuery)
    );
    renderVocabulary(filtered);
}

function startReviewSession() {
    // Get vocabulary that needs review (low mastery or new)
    reviewQueue = allVocabulary
        .filter(v => !v.mastery || v.mastery.mastery_level < 3)
        .sort(() => Math.random() - 0.5)
        .slice(0, 10);

    if (reviewQueue.length === 0) {
        alert('Great job! You have mastered all vocabulary. Check back later for new words.');
        return;
    }

    currentReviewIndex = 0;
    showReviewCard();
}

function showReviewCard() {
    if (currentReviewIndex >= reviewQueue.length) {
        completeReviewSession();
        return;
    }

    const vocab = reviewQueue[currentReviewIndex];
    const modal = document.getElementById('reviewModal');
    const word = document.getElementById('reviewWord');
    const definition = document.getElementById('reviewDefinition');
    const example = document.getElementById('reviewExample');

    if (word) word.textContent = vocab.word;
    if (definition) definition.textContent = vocab.definition;
    if (example) example.textContent = vocab.example ? `"${vocab.example}"` : '';

    if (modal) modal.classList.remove('hidden');
}

async function reviewVocabulary(correct) {
    const vocab = reviewQueue[currentReviewIndex];

    try {
        await apiRequest(`/vocabulary/${vocab.id}/review`, {
            method: 'POST',
            body: JSON.stringify({ correct: correct })
        });

        // Update local state
        const vocabIndex = allVocabulary.findIndex(v => v.id === vocab.id);
        if (vocabIndex !== -1) {
            if (!allVocabulary[vocabIndex].mastery) {
                allVocabulary[vocabIndex].mastery = { mastery_level: 0 };
            }
            if (correct) {
                allVocabulary[vocabIndex].mastery.mastery_level = Math.min(
                    allVocabulary[vocabIndex].mastery.mastery_level + 1,
                    5
                );
            }
        }

        currentReviewIndex++;
        showReviewCard();
    } catch (error) {
        console.error('Failed to record review:', error);
        currentReviewIndex++;
        showReviewCard();
    }
}

function completeReviewSession() {
    const modal = document.getElementById('reviewModal');
    if (modal) modal.classList.add('hidden');

    alert(`Review session complete! You reviewed ${reviewQueue.length} words.`);
    renderVocabulary(allVocabulary);
}

function closeReviewModal() {
    const modal = document.getElementById('reviewModal');
    if (modal) modal.classList.add('hidden');
}

document.addEventListener('DOMContentLoaded', function() {
    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            filterVocabulary(this.dataset.category);
        });
    });

    // Search
    const searchInput = document.getElementById('vocabSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            searchVocabulary(this.value);
        });
    }

    // Start review button
    const reviewBtn = document.getElementById('startReviewBtn');
    if (reviewBtn) {
        reviewBtn.addEventListener('click', startReviewSession);
    }

    // Review modal buttons
    const reviewClose = document.getElementById('reviewClose');
    if (reviewClose) {
        reviewClose.addEventListener('click', closeReviewModal);
    }

    const reviewAgainBtn = document.getElementById('reviewAgainBtn');
    if (reviewAgainBtn) {
        reviewAgainBtn.addEventListener('click', () => reviewVocabulary(false));
    }

    const reviewKnownBtn = document.getElementById('reviewKnownBtn');
    if (reviewKnownBtn) {
        reviewKnownBtn.addEventListener('click', () => reviewVocabulary(true));
    }
});
