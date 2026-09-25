document.addEventListener('DOMContentLoaded', function() {
    const API_BASE = '/api';
    let isListening = false;
    let recognition = null;
    let sessionStartTime = Date.now();
    let isProcessing = false;

    const micButton = document.getElementById('micButton');
    const micStatus = document.getElementById('micStatus');
    const waveform = document.getElementById('waveform');
    const conversation = document.getElementById('conversation');
    const assistantState = document.getElementById('assistantState');
    const themeToggle = document.getElementById('themeToggle');
    const toastContainer = document.getElementById('toastContainer');
    const greeting = document.getElementById('greeting');

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        toastContainer.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(50px)';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    function updateSessionTime() {
        const elapsed = Math.floor((Date.now() - sessionStartTime) / 1000);
        const minutes = Math.floor(elapsed / 60).toString().padStart(2, '0');
        const seconds = (elapsed % 60).toString().padStart(2, '0');
        const sessionTimeEl = document.getElementById('sessionTime');
        if (sessionTimeEl) sessionTimeEl.textContent = `${minutes}:${seconds}`;
    }
    setInterval(updateSessionTime, 1000);

    function setAssistantState(state) {
        micButton.classList.remove('listening', 'processing', 'speaking', 'error');
        if (state !== 'ready') {
            micButton.classList.add(state);
        }
        micStatus.textContent = state.toUpperCase();
        if (assistantState) assistantState.textContent = state.toUpperCase();

        const hour = new Date().getHours();
        if (state === 'ready') {
            if (greeting) {
                greeting.querySelector('h2').textContent = hour < 12 ? 'Good morning!' : hour < 18 ? 'Good afternoon!' : 'Good evening!';
            }
        }
    }

    function addMessage(text, isUser = false) {
        const welcomeMessage = conversation.querySelector('.welcome-message');
        if (welcomeMessage) welcomeMessage.remove();

        const wrapper = document.createElement('div');
        wrapper.className = `message-wrapper ${isUser ? 'user-message-wrapper' : ''}`;
        wrapper.style.animation = 'messageSlide 0.3s ease';

        const avatar = document.createElement('div');
        avatar.className = 'assistant-avatar';
        avatar.textContent = isUser ? '👤' : '🤖';

        const content = document.createElement('div');
        content.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
        content.innerHTML = `<p>${escapeHtml(text)}</p>`;

        wrapper.appendChild(avatar);
        wrapper.appendChild(content);
        conversation.appendChild(wrapper);

        conversation.scrollTop = conversation.scrollHeight;
    }

    function loadHistory() {
        fetch(`${API_BASE}/history`)
            .then(res => res.json())
            .then(history => {
                const container = document.getElementById('recentCommands');
                if (!container) return;
                if (history.length === 0) {
                    container.innerHTML = '<p class="empty-state">No commands yet. Start speaking!</p>';
                    return;
                }
                container.innerHTML = history.slice(0, 8).map(h =>
                    `<div class="command-item" data-command="${escapeHtml(h.command)}">${escapeHtml(h.command)}</div>`
                ).join('');
                container.querySelectorAll('.command-item').forEach(item => {
                    item.addEventListener('click', () => {
                        const cmd = item.dataset.command;
                        processCommand(cmd);
                    });
                });
            })
            .catch(() => {
                const container = document.getElementById('recentCommands');
                if (container) container.innerHTML = '<p class="empty-state">No commands yet.</p>';
            });
    }

    function loadNotes() {
        fetch(`${API_BASE}/notes`)
            .then(res => res.json())
            .then(notes => {
                const container = document.getElementById('savedNotes');
                if (!container) return;
                if (notes.length === 0) {
                    container.innerHTML = '<p class="empty-state">No notes saved yet.</p>';
                    return;
                }
                container.innerHTML = notes.slice(0, 5).map(n =>
                    `<div class="note-item" data-id="${n.id}">${escapeHtml(n.note)}</div>`
                ).join('');
                container.querySelectorAll('.note-item').forEach(item => {
                    item.addEventListener('click', () => {
                        const id = parseInt(item.dataset.id);
                        if (confirm('Delete this note?')) {
                            fetch(`${API_BASE}/notes/${id}`, { method: 'DELETE' })
                                .then(() => {
                                    showToast('Note deleted', 'success');
                                    loadNotes();
                                    loadStats();
                                });
                        }
                    });
                });
            })
            .catch(() => {
                const container = document.getElementById('savedNotes');
                if (container) container.innerHTML = '<p class="empty-state">No notes saved yet.</p>';
            });
    }

    function loadStats() {
        fetch(`${API_BASE}/stats`)
            .then(res => res.json())
            .then(stats => {
                const commandsToday = document.getElementById('commandsToday');
                const notesCount = document.getElementById('notesCount');
                const totalCommands = document.getElementById('totalCommands');
                if (commandsToday) commandsToday.textContent = stats.commands_today;
                if (notesCount) notesCount.textContent = stats.notes_count;
                if (totalCommands) totalCommands.textContent = stats.total_commands;
            })
            .catch(() => {});
    }

    function getHintForState(state) {
        if (state === 'listening') return 'Listening...';
        if (state === 'processing') return 'Thinking...';
        if (state === 'speaking') return 'Speaking...';
        if (state === 'error') return 'Something went wrong. Try again.';
        const hour = new Date().getHours();
        if (hour < 12) return 'Try saying: "What time is it?"';
        if (hour < 18) return 'Try saying: "Tell me a joke"';
        return 'Try saying: "Save note: Buy groceries"';
    }

    function processCommand(commandText) {
        if (!commandText || !commandText.trim()) return;
        if (isProcessing) return;

        isProcessing = true;
        addMessage(commandText, true);
        setAssistantState('processing');
        waveform.classList.add('active');

        console.log('[API] Sending command:', commandText);

        fetch(`${API_BASE}/process`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: commandText })
        })
        .then(res => {
            console.log('[API] Response status:', res.status);
            if (!res.ok) throw new Error('Server error');
            return res.json();
        })
        .then(data => {
            waveform.classList.remove('active');
            if (data.error) {
                setAssistantState('error');
                addMessage(data.error, false);
                showToast(data.error, 'error');
                setTimeout(() => {
                    setAssistantState('ready');
                    isProcessing = false;
                }, 2000);
                return;
            }

            console.log('[API] Response:', data.text);
            addMessage(data.text, false);
            setAssistantState('ready');
            showToast(data.text, 'success');

            if (data.action && data.action.type === 'open_url') {
                setTimeout(() => {
                    window.open(data.action.url, '_blank');
                }, 500);
            }

            if (data.action && data.action.type === 'delete_note') {
                setTimeout(() => {
                    fetch(`${API_BASE}/notes/${data.action.id}`, { method: 'DELETE' })
                        .then(() => {
                            loadNotes();
                            loadStats();
                        });
                }, 500);
            }

            fetch(`${API_BASE}/tts`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: data.text })
            })
            .then(res => res.json())
            .then(ttsData => {
                if (ttsData.audio) {
                    console.log('[VOICE] Playing TTS audio');
                    setAssistantState('speaking');
                    const audio = new Audio(`data:audio/mp3;base64,${ttsData.audio}`);
                    audio.onended = () => {
                        console.log('[VOICE] Audio playback ended');
                        setAssistantState('ready');
                        isProcessing = false;
                    };
                    audio.onerror = () => {
                        console.log('[VOICE] Audio playback error');
                        setAssistantState('ready');
                        isProcessing = false;
                    };
                    audio.play().catch(() => {
                        setAssistantState('ready');
                        isProcessing = false;
                    });
                } else {
                    console.log('[VOICE] No audio returned, skipping TTS');
                    setAssistantState('ready');
                    isProcessing = false;
                }
            })
            .catch(() => {
                setAssistantState('ready');
                isProcessing = false;
            });

            loadHistory();
            loadStats();
        })
        .catch(err => {
            waveform.classList.remove('active');
            console.error('[API ERROR]', err);
            setAssistantState('error');
            addMessage('Sorry, I encountered an error. Please try again.', false);
            showToast('Connection error. Is the server running?', 'error');
            setTimeout(() => {
                setAssistantState('ready');
                isProcessing = false;
            }, 2000);
        });
    }

    function initSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            showToast('Speech recognition is not supported in this browser. Try Chrome or Edge, or use the text input below.', 'error');
            const micState = document.getElementById('micState');
            if (micState) micState.textContent = 'Not supported';
            return false;
        }

        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = function() {
            console.log('[VOICE] Recognition started');
            isListening = true;
            setAssistantState('listening');
            waveform.classList.add('active');
        };

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            console.log('[VOICE] Transcript received:', transcript);
            if (transcript) {
                processCommand(transcript);
            }
        };

        recognition.onerror = function(event) {
            console.error('[VOICE ERROR]', event.error);
            isListening = false;
            waveform.classList.remove('active');

            let message = '';
            switch (event.error) {
                case 'no-speech':
                    message = 'No speech detected. Please try again.';
                    break;
                case 'not-allowed':
                    message = 'Microphone permission is required. Please allow microphone access in your browser settings.';
                    const micState = document.getElementById('micState');
                    if (micState) micState.textContent = 'Denied';
                    break;
                case 'network':
                    message = 'Speech recognition service is unavailable. Please check your internet connection and try again, or use the text input below.';
                    break;
                case 'aborted':
                    message = 'Speech recognition was cancelled.';
                    break;
                case 'service-not-allowed':
                    message = 'Speech recognition service is not allowed. Please check your browser settings.';
                    break;
                case 'audio-capture':
                    message = 'No microphone found. Please connect a microphone.';
                    break;
                default:
                    message = `Speech error: ${event.error}. Please try again, or use the text input below.`;
            }

            showToast(message, 'error');
            setAssistantState('error');
            setTimeout(() => {
                setAssistantState('ready');
                isProcessing = false;
            }, 2500);
        };

        recognition.onend = function() {
            console.log('[VOICE] Recognition ended');
            isListening = false;
            waveform.classList.remove('active');
            if (micButton.classList.contains('listening')) {
                setAssistantState('ready');
            }
        };

        const micState = document.getElementById('micState');
        if (micState) micState.textContent = 'Available';
        return true;
    }

    micButton.addEventListener('click', function() {
        if (!recognition) {
            const initialized = initSpeechRecognition();
            if (!initialized) return;
        }

        if (isListening) {
            recognition.stop();
            isListening = false;
            setAssistantState('ready');
            waveform.classList.remove('active');
            return;
        }

        if (isProcessing) return;

        try {
            recognition.start();
        } catch (e) {
            console.error('Recognition start error:', e);
            showToast('Could not start microphone. Please refresh and try again.', 'error');
        }
    });

    const textInput = document.getElementById('textCommand');
    const sendButton = document.getElementById('sendTextCommand');

    function sendTextCommand() {
        const text = textInput.value.trim();
        if (!text) return;
        textInput.value = '';
        console.log('[TEXT] Command typed:', text);
        processCommand(text);
    }

    if (sendButton && textInput) {
        sendButton.addEventListener('click', sendTextCommand);
        textInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendTextCommand();
            }
        });
    }

    document.addEventListener('keydown', function(e) {
        if (e.code === 'Space' && document.activeElement === document.body) {
            e.preventDefault();
            micButton.click();
        }
    });

    document.querySelectorAll('.quick-action-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const command = this.dataset.command;
            if (command) processCommand(command);
        });
    });

    document.getElementById('clearConversation').addEventListener('click', function() {
        if (confirm('Clear all conversation messages?')) {
            conversation.innerHTML = `
                <div class="welcome-message">
                    <div class="assistant-avatar">🤖</div>
                    <div class="message assistant-message">
                        <p>Conversation cleared. Click the microphone and start speaking!</p>
                    </div>
                </div>
            `;
            showToast('Conversation cleared', 'success');
        }
    });

    themeToggle.addEventListener('click', function() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', newTheme);
        const themeIcon = document.querySelector('.theme-icon');
        if (themeIcon) themeIcon.textContent = newTheme === 'light' ? '☀️' : '🌙';
        localStorage.setItem('voice-assistant-theme', newTheme);
    });

    const savedTheme = localStorage.getItem('voice-assistant-theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
        const themeIcon = document.querySelector('.theme-icon');
        if (themeIcon) themeIcon.textContent = savedTheme === 'light' ? '☀️' : '🌙';
    }

    const mobileTabs = document.querySelectorAll('.mobile-tab');
    const leftSidebar = document.getElementById('leftSidebar');
    const rightSidebar = document.getElementById('rightSidebar');

    if (mobileTabs.length > 0) {
        mobileTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                const target = this.dataset.target;
                if (target === 'left') {
                    leftSidebar.classList.toggle('mobile-open');
                    rightSidebar.classList.remove('mobile-open');
                } else if (target === 'right') {
                    rightSidebar.classList.toggle('mobile-open');
                    leftSidebar.classList.remove('mobile-open');
                }
            });
        });

        document.addEventListener('click', function(e) {
            if (!e.target.closest('.sidebar') && !e.target.closest('.mobile-tab')) {
                leftSidebar.classList.remove('mobile-open');
                rightSidebar.classList.remove('mobile-open');
            }
        });
    }

    const settingsBtn = document.getElementById('settingsBtn');
    if (settingsBtn) {
        settingsBtn.addEventListener('click', function() {
            showToast('Settings panel coming soon!', 'info');
        });
    }

    initSpeechRecognition();
    loadHistory();
    loadNotes();
    loadStats();
});
