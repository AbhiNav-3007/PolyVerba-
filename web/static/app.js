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
let selectedModel  = 'base.en';
let targetLang     = 'English';   // synced from dropdown on init

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
const modelSelect   = document.getElementById('model-select');
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
    ws.onopen  = () => { isConnected = true;  updateConnectionUI(); updateButtons(); };
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

function handleMessage(msg) {
    if (msg.type === 'word') {
        hideWelcome();
        hideListening();
        appendWord(msg.text);
    } else if (msg.type === 'final') {
        hideWelcome();
        confirmChunk(msg.text, msg.latency);
    } else if (msg.type === 'error') {
        showToast(msg.text, 'error');
        isStreaming = false;
        updateButtons();
    }
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
    if (chunks.length > maxChunks) {
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

    try {
        const res = await fetch('/api/start', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                target_lang:  targetLang,
                model:        selectedModel,
                capture_mode: 'loopback'
            })
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            isStreaming = false; updateButtons(); hideListening(); showWelcome();
            showToast('Failed: ' + (err.message || 'Unknown error'), 'error');
        } else {
            const mLabel = selectedModel === 'base.en' ? 'EN-only' : 'Auto-detect';
            showToast(`▶ ${mLabel} → ${targetLang}`, 'info');
        }
    } catch {
        isStreaming = false; updateButtons();
        showToast('Cannot reach server.', 'error');
    }
}

async function stopCaption() {
    isStreaming = false;
    draftSpans.forEach(s => s.remove());
    draftSpans = [];
    hideListening();
    updateButtons();
    showToast('⏹ Stopped', 'info');
    try { await fetch('/api/stop', { method: 'POST' }); } catch(e) { console.error(e); }
}

// ── Model selector ───────────────────────────────────────────────────────
modelSelect.addEventListener('change', (e) => {
    if (isStreaming) {
        e.target.value = selectedModel;
        showToast('Stop captioning first to change model', 'error');
        return;
    }
    selectedModel = e.target.value;
    if (modelBadgeText) modelBadgeText.textContent = selectedModel;
    showToast(selectedModel === 'base.en' ? 'English Only (base.en)' : 'Auto-Detect (small)', 'info');
});

// ── Language selector ────────────────────────────────────────────────────
langSelect.addEventListener('change', async (e) => {
    const prev = targetLang;
    targetLang = e.target.value;

    if (targetLang === 'English') {
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
        if (targetLang === 'English') {
            marker.textContent = '\u2014 Back to English \u2014';
        } else {
            marker.textContent = `Translating to ${targetLang}`;
        }
        captionFlow.insertBefore(marker, flowCursor);

        scrollToBottom();
        try {
            await fetch('/api/update-target', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target_lang: targetLang })
            });
        } catch(err) { console.error(err); }
    }
});

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
    btnStart.disabled = isStreaming || !isConnected;
    btnStart.innerHTML = isStreaming
        ? `<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg> Running`
        : `<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg> Start`;
    btnStop.disabled = !isStreaming;
    btnStop.classList.toggle('active', isStreaming);
    modelSelect.disabled      = isStreaming;
    modelSelect.style.opacity = isStreaming ? '0.45' : '1';
    modelSelect.style.cursor  = isStreaming ? 'not-allowed' : 'pointer';
}

function updateLatency(s) {
    if (s != null && latencyValue) latencyValue.textContent = s + 's';
}

// ═══════════════════════════════════════════════════════════════════════════
//  INIT
// ═══════════════════════════════════════════════════════════════════════════

// Sync default language from HTML
targetLang = langSelect.value || 'English';
connectWebSocket();
