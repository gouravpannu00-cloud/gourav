// English Tutor - Dashboard JavaScript

async function loadDashboard() {
    try {
        const data = await apiRequest('/dashboard');
        updateDashboardUI(data);
    } catch (error) {
        console.error('Failed to load dashboard:', error);
        if (error.message.includes('Token')) {
            logout();
        }
    }
}

function updateDashboardUI(data) {
    const { user, stats, recent_activity } = data;

    // Update greeting
    const greeting = document.getElementById('greeting');
    if (greeting) {
        const name = user.full_name || user.username;
        greeting.textContent = `Welcome back, ${name}!`;
    }

    // Update date
    const dateDisplay = document.getElementById('dateDisplay');
    if (dateDisplay) {
        const today = new Date();
        dateDisplay.textContent = today.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    // Update stats
    const streakValue = document.getElementById('streakValue');
    if (streakValue) streakValue.textContent = stats.streak_days;

    const lessonsValue = document.getElementById('lessonsValue');
    if (lessonsValue) lessonsValue.textContent = `${stats.completed_lessons}/${stats.total_lessons}`;

    const quizScore = document.getElementById('quizScore');
    if (quizScore) quizScore.textContent = `${stats.average_score}%`;

    const wordsValue = document.getElementById('wordsValue');
    if (wordsValue) wordsValue.textContent = stats.words_learned;

    // Update daily progress
    const dailyProgressBar = document.getElementById('dailyProgressBar');
    const dailyGoalText = document.getElementById('dailyGoalText');
    if (dailyProgressBar && dailyGoalText) {
        const goalMinutes = stats.daily_goal_minutes || 30;
        const todayMinutes = stats.today_minutes || 0;
        const percentage = Math.min((todayMinutes / goalMinutes) * 100, 100);
        dailyProgressBar.style.width = `${percentage}%`;
        dailyGoalText.textContent = `${todayMinutes} / ${goalMinutes} minutes today`;
    }

    // Update recent activity
    const activityList = document.getElementById('activityList');
    if (activityList && recent_activity && recent_activity.length > 0) {
        activityList.innerHTML = recent_activity.map(chat => `
            <div class="activity-item">
                <strong>You:</strong> ${chat.user_message.substring(0, 60)}...
            </div>
        `).join('');
    }
}
