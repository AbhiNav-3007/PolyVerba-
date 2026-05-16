/**
 * PolyVerba — Client-Side Logic (Continuous Flow Paragraph)
 *
 * Design: ONE flowing paragraph element (#caption-flow).
 * - Confirmed chunks append inline as <span class="chunk-N"> — natural CSS word-wrap
 * - Draft words appear at the end as grey italic spans
 * - No artificial line breaks between Whisper chunks
 * - No _stream_words delay needed; CSS word-fade-in handles visual pacing
 * - Max 40 confirmed chunks kept → auto-prune old ones
 *
 * Message protocol:
 *   {type:"word",  text}         → append grey word inline
 *   {type:"final", text, latency}→ replace draft with confirmed white chunk
 *   {type:"error", text}         → toast + stop state
 */

// ═══════════════════════════════════════════════════════════════════════════
//  STATE
// ═══════════════════════════════════════════════════════════════════════════

let ws             = null;
let isConnected    = false;
let isStreaming    = false;
let targetLang     = 'English (Latin)';   // synced from dropdown on init

const isHost       = location.hostname === 'localhost' || location.hostname === '127.0.0.1';

let draftSpans     = [];          // current grey draft word spans
let confirmedCount = 0;           // number of confirmed chunks in flow
let userScrolledUp = false;
let scrollTimeout  = null;

// ═══════════════════════════════════════════════════════════════════════════
//  DOM REFERENCES
// ═══════════════════════════════════════════════════════════════════════════

const captionFlow   = document.getElementById('caption-flow');
const flowCursor    = document.getElementById('flow-cursor');
const listenRing    = document.getElementById('listen-ring');
const welcomeState  = document.getElementById('welcome-state');
const captionsScroll= document.getElementById('captions-scroll');

const btnStart      = document.getElementById('btn-start');
const btnStop       = document.getElementById('btn-stop');
const langSelect    = document.getElementById('lang-select');
const sourceSelect  = document.getElementById('source-select');
const modelBadgeText= document.getElementById('model-badge-text');
const statusDot     = document.getElementById('status-dot');
const statusLabel   = document.getElementById('status-label');
const latencyValue  = document.getElementById('latency-value');

// ═══════════════════════════════════════════════════════════════════════════
//  WEBSOCKET
// ═══════════════════════════════════════════════════════════════════════════

function connectWebSocket() {
    const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${proto}//${location.host}/ws/captions`);
    ws.onopen  = () => {
        isConnected = true;
        updateConnectionUI();
        updateButtons();
        ws.send(JSON.stringify({ type: 'subscribe', language: targetLang }));
    };
    ws.onclose = () => { isConnected = false; updateConnectionUI(); updateButtons(); setTimeout(connectWebSocket, 3000); };
    ws.onerror = () => {};
    ws.onmessage = (ev) => {
        try { handleMessage(JSON.parse(ev.data)); }
        catch (e) { console.error('[WS]', e); }
    };
}

// ═══════════════════════════════════════════════════════════════════════════
//  MESSAGE HANDLING
// ═══════════════════════════════════════════════════════════════════════════

let _wordAnimTimer = null;  // timer handle for current word animation

function handleMessage(msg) {
    if (msg.type === 'word') {
        hideWelcome();
        hideListening();
        appendWord(msg.text);
    } else if (msg.type === 'final') {
        hideWelcome();
        if (targetLang === 'English (Latin)') {
            // English: server already streamed grey words; just confirm the chunk
            confirmChunk(msg.text, msg.latency);
        } else {
            // Translated language: server sends full sentence at once.
            // Animate it word-by-word on the client so we get the same grey→white effect.
            animateTranslatedWords(msg.text, msg.latency);
        }
    } else if (msg.type === 'error') {
        showToast(msg.text, 'error');
        isStreaming = false;
        updateButtons();
    }
}

// ═══════════════════════════════════════════════════════════════════════════
//  TRANSLATED WORD ANIMATION (client-side grey → white for non-English)
// ═══════════════════════════════════════════════════════════════════════════

function animateTranslatedWords(text, latency) {
    if (!text || !text.trim()) return;

    // Cancel any previous animation that hasn't finished yet
    if (_wordAnimTimer !== null) {
        clearTimeout(_wordAnimTimer);
        _wordAnimTimer = null;
        // Immediately clear leftover draft words from previous chunk
        draftSpans.forEach(s => s.remove());
        draftSpans = [];
    }

    const words = text.trim().split(/\s+/);
    let i = 0;

    function showNext() {
        if (!isStreaming) return;   // stopped mid-animation
        if (i < words.length) {
            hideListening();
            appendWord(words[i]);
            i++;
            _wordAnimTimer = setTimeout(showNext, 40);
        } else {
            _wordAnimTimer = null;
            confirmChunk(text, latency);
        }
    }
    showNext();
}

// ═══════════════════════════════════════════════════════════════════════════
//  CONTINUOUS FLOW — append one word at a time
// ═══════════════════════════════════════════════════════════════════════════

function appendWord(word) {
    word = word.trim();
    if (!word) return;

    captionFlow.style.display = 'block';

    const span = document.createElement('span');
    span.className   = 'word-draft';
    // Prepend space if not the very first element in flow
    span.textContent = (captionFlow.children.length > 1 ? ' ' : '') + word;
    // Insert before the cursor
    captionFlow.insertBefore(span, flowCursor);
    draftSpans.push(span);

    scrollToBottom();
}

// ═══════════════════════════════════════════════════════════════════════════
//  CONFIRM CHUNK — grey draft → white confirmed inline span
// ═══════════════════════════════════════════════════════════════════════════

function confirmChunk(text, latency) {
    captionFlow.style.display = 'block';

    // Remove all draft spans (replaced by the confirmed text span below)
    draftSpans.forEach(s => s.remove());
    draftSpans = [];

    if (!text || !text.trim()) return;

    // Create confirmed span — brightness set by updateChunkAges()
    const span = document.createElement('span');
    span.className   = 'chunk-confirmed chunk-age-0';
    // Space before unless this is the very first element
    span.textContent = (captionFlow.children.length > 1 ? ' ' : '') + text.trim();
    captionFlow.insertBefore(span, flowCursor);
    confirmedCount++;

    // Age all confirmed chunks (newest = bright, old = dim)
    updateChunkAges();

    // Prune oldest confirmed chunks to prevent DOM bloat
    pruneOldChunks(40);

    updateLatency(latency);
    scrollToBottom();
}

function updateChunkAges() {
    const chunks = Array.from(captionFlow.querySelectorAll('.chunk-confirmed'));
    const total  = chunks.length;
    chunks.forEach((c, i) => {
        const age = total - 1 - i;   // 0 = newest
        c.className = `chunk-confirmed chunk-age-${Math.min(age, 4)}`;
    });
}

function pruneOldChunks(maxChunks) {
    const chunks = Array.from(captionFlow.querySelectorAll('.chunk-confirmed'));
    // Only prune when significantly over limit (by 20 words ≈ 1 full sentence)
    // Drops in one batch → prevents constant word-by-word line-shifting jitter
    if (chunks.length > maxChunks + 20) {
        chunks.slice(0, chunks.length - maxChunks).forEach(c => c.remove());
    }
}

// ═══════════════════════════════════════════════════════════════════════════
//  SCROLL
// ═══════════════════════════════════════════════════════════════════════════

function scrollToBottom() {
    if (userScrolledUp) return;
    document.getElementById('scroll-anchor')?.scrollIntoView({ behavior: 'smooth' });
}

captionsScroll.addEventListener('scroll', () => {
    const atBottom = captionsScroll.scrollHeight - captionsScroll.scrollTop - captionsScroll.clientHeight < 80;
    if (atBottom) {
        userScrolledUp = false;
    } else {
        userScrolledUp = true;
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => { userScrolledUp = false; }, 6000);
    }
});

// ═══════════════════════════════════════════════════════════════════════════
//  SHOW / HIDE
// ═══════════════════════════════════════════════════════════════════════════

function hideWelcome() { if (welcomeState) welcomeState.style.display = 'none'; }
function showWelcome()  { if (welcomeState) welcomeState.style.display = 'flex'; }
function hideListening(){ if (listenRing)   listenRing.style.display   = 'none'; }
function showListening(){ if (listenRing)   listenRing.style.display   = 'flex'; }

// ═══════════════════════════════════════════════════════════════════════════
//  TOAST
// ═══════════════════════════════════════════════════════════════════════════

function showToast(message, type = 'info') {
    document.getElementById('polyverba-toast')?.remove();
    const toast = document.createElement('div');
    toast.id = 'polyverba-toast';
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('toast-visible'));
    setTimeout(() => { toast.classList.remove('toast-visible'); setTimeout(() => toast.remove(), 400); }, 3000);
}

// ═══════════════════════════════════════════════════════════════════════════
//  CONTROLS
// ═══════════════════════════════════════════════════════════════════════════

async function startCaption() {
    if (isStreaming || !isConnected) return;

    // Clear previous session
    captionFlow.innerHTML = '';
    captionFlow.appendChild(flowCursor); // restore cursor
    captionFlow.style.display = 'none';
    draftSpans     = [];
    confirmedCount = 0;
    userScrolledUp = false;

    hideWelcome();
    isStreaming = true;
    updateButtons();
    showListening();

    if (!isHost) return; // Viewers cannot start the server

    try {
        const captureMode = sourceSelect ? sourceSelect.value : 'loopback';
        const res = await fetch('/api/start', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                target_lang:  targetLang,
                capture_mode: captureMode
            })
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            isStreaming = false; updateButtons(); hideListening(); showWelcome();
            showToast('Failed: ' + (err.message || 'Unknown error'), 'error');
        } else {
            showToast(`▶ Starting → ${targetLang}`, 'info');
        }
    } catch {
        isStreaming = false; updateButtons();
        showToast('Cannot reach server.', 'error');
    }
}

async function stopCaption() {
    if (!isHost) return;
    
    isStreaming = false;
    draftSpans.forEach(s => s.remove());
    draftSpans = [];
    hideListening();
    updateButtons();
    showToast('⏹ Stopped', 'info');
    try { await fetch('/api/stop', { method: 'POST' }); } catch(e) { console.error(e); }
}

// ── Language selector ────────────────────────────────────────────────────
langSelect.addEventListener('change', async (e) => {
    const prev = targetLang;
    targetLang = e.target.value;

    if (targetLang === 'English (Latin)') {
        showToast('Showing original English — no translation', 'info');
    } else {
        showToast(`Translating to ${targetLang}`, 'info');
    }

    if (isStreaming && prev !== targetLang) {
        // Break the flow paragraph: insert a block-level language switch label
        // Force line break before it by ending the current inline context
        const br = document.createElement('br');
        captionFlow.insertBefore(br, flowCursor);

        const marker = document.createElement('div');
        marker.className = 'flow-lang-switch';
        if (targetLang === 'English (Latin)') {
            marker.textContent = '\u2014 Back to English \u2014';
        } else {
            marker.textContent = `Translating to ${targetLang}`;
        }
        captionFlow.insertBefore(marker, flowCursor);

        scrollToBottom();
        
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'subscribe', language: targetLang }));
        }
    } else {
        // Even if not streaming, we want to subscribe so that when stream starts, we get the right language
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'subscribe', language: targetLang }));
        }
    }
});

if (sourceSelect) {
    sourceSelect.addEventListener('change', (e) => {
        showToast(`Audio Source set to: ${e.target.options[e.target.selectedIndex].text}`, 'info');
    });
}

// ── Button clicks ────────────────────────────────────────────────────────
btnStart.addEventListener('click', startCaption);
btnStop.addEventListener('click',  stopCaption);

// ── Space = toggle ───────────────────────────────────────────────────────
document.addEventListener('keydown', (e) => {
    const tag = e.target.tagName;
    if (e.code === 'Space' && tag !== 'SELECT' && tag !== 'INPUT' && tag !== 'BUTTON') {
        e.preventDefault();
        isStreaming ? stopCaption() : startCaption();
    }
});

// ═══════════════════════════════════════════════════════════════════════════
//  UI STATE
// ═══════════════════════════════════════════════════════════════════════════

function updateConnectionUI() {
    statusDot.classList.toggle('connected', isConnected);
    statusLabel.textContent = isConnected ? 'CONNECTED' : 'OFFLINE';
}

function updateButtons() {
    if (btnStart) {
        btnStart.disabled = isStreaming || !isConnected;
        btnStart.innerHTML = isStreaming
            ? `<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg> Running`
            : `<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg> Start`;
    }
    if (btnStop) {
        btnStop.disabled = !isStreaming;
        btnStop.classList.toggle('active', isStreaming);
    }
    
    if (sourceSelect) sourceSelect.disabled = isStreaming;
}

function updateLatency(s) {
    if (s != null && latencyValue) latencyValue.textContent = s + 's';
}

// ═══════════════════════════════════════════════════════════════════════════
//  INIT
// ═══════════════════════════════════════════════════════════════════════════

// Sync default language from HTML
targetLang = langSelect.value || 'English (Latin)';
connectWebSocket();

// ═══════════════════════════════════════════════════════════════════════════
//  MOBILE VIEWER BAR
// ═══════════════════════════════════════════════════════════════════════════

const mobileBar      = document.getElementById('mobile-viewer-bar');
const mobileLangSel  = document.getElementById('mobile-lang-select');
const mobileBtnPlay  = document.getElementById('mobile-btn-play');
const mobileBtnPause = document.getElementById('mobile-btn-pause');

let isLocallyPaused = false;  // Viewer-local pause — doesn't affect server

function updateMobileBar() {
    if (!mobileBar) return;
    const hostRunning = isStreaming;
    mobileBtnPlay.disabled  = hostRunning && !isLocallyPaused ? true : !hostRunning;
    mobileBtnPause.disabled = !hostRunning;
    mobileBtnPause.classList.toggle('active-pause', isLocallyPaused);
    // Show button means: host is running AND we are currently paused
    mobileBtnPlay.disabled = !hostRunning || !isLocallyPaused;
}

if (mobileLangSel) {
    mobileLangSel.addEventListener('change', () => {
        targetLang = mobileLangSel.value;
        // Keep navbar dropdown in sync
        if (langSelect) langSelect.value = targetLang;
        showToast(`🌐 ${targetLang}`, 'info');
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'subscribe', language: targetLang }));
        }
    });
}

if (mobileBtnPlay) {
    mobileBtnPlay.addEventListener('click', () => {
        isLocallyPaused = false;
        showToast('▶ Captions resumed', 'info');
        showListening();
        updateMobileBar();
    });
}

if (mobileBtnPause) {
    mobileBtnPause.addEventListener('click', () => {
        isLocallyPaused = true;
        hideListening();
        showToast('⏸ Captions paused on your device', 'info');
        updateMobileBar();
    });
}

// Override handleMessage so paused viewers skip rendering
const _origHandleMessage = handleMessage;
window.handleMessage = function(msg) {
    if (isLocallyPaused && msg.type !== 'error') return;
    _origHandleMessage(msg);
};
// Re-bind WebSocket to use overridden handler
function _patchWsMessage() {
    if (!ws) return;
    ws.onmessage = (ev) => {
        try { window.handleMessage(JSON.parse(ev.data)); }
        catch(e) { console.error('[WS]', e); }
    };
}

// ── Host vs Viewer UI Separation ─────────────────────────────────────────
if (!isHost) {
    document.body.classList.add('viewer-mode');
    // Hide laptop-only controls from the navbar
    if (btnStart) btnStart.style.display = 'none';
    if (btnStop)  btnStop.style.display  = 'none';
    const audioSourceWrapper = document.getElementById('audio-source-wrapper');
    if (audioSourceWrapper) audioSourceWrapper.style.display = 'none';

    // Show the mobile bar
    if (mobileBar) mobileBar.style.display = 'block';

    // Welcome message for viewers
    const wTitle = document.querySelector('#welcome-state h3');
    if (wTitle) wTitle.textContent = '📱 Waiting for Host...';
    const wDesc  = document.querySelector('#welcome-state p');
    if (wDesc)  wDesc.textContent  = 'Select your language below. Captions will appear here automatically when the event begins.';
    
    // Sync mobile lang dropdown with navbar lang
    if (mobileLangSel && langSelect) mobileLangSel.value = langSelect.value;
    updateMobileBar();
}

// Auto-sync Viewer State
async function checkStatus() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();
        if (data.running && !isStreaming) {
            // Host just started — switch viewer to running state
            isStreaming = true;
            hideWelcome();
        if (!isLocallyPaused) showListening();
            updateButtons();
            updateMobileBar();
            // CRITICAL: re-send our language subscription
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: 'subscribe', language: targetLang }));
            }
        } else if (!data.running && isStreaming) {
            isStreaming = false;
            isLocallyPaused = false;
            updateButtons();
            updateMobileBar();
            showWelcome();
            hideListening();
        }
    } catch(e) {}
}
if (!isHost) {
    setInterval(checkStatus, 2000);
}
