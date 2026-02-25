/* ────────────────────────────────────────────────────────────────────────────
   Lazy Sleep – Renderer logic
   ──────────────────────────────────────────────────────────────────────────── */

const MAX_MINUTES = 180;
const TICK_INTERVAL = 30;

// ── DOM refs ────────────────────────────────────────────────────────────────
const $greeting       = document.getElementById('greeting-text');
const $shutdownTime   = document.getElementById('shutdown-time');
const $slider         = document.getElementById('slider');
const $tickLabels     = document.getElementById('slider-tick-labels');
const $tickMarks      = document.getElementById('slider-tick-marks');
const $hourLabels     = document.getElementById('slider-hour-labels');
const $btnSchedule    = document.getElementById('btn-schedule');
const $btnCancel      = document.getElementById('btn-cancel');
const $btnInvisibility = document.getElementById('btn-invisibility');
const $btnToggleInput = document.getElementById('btn-toggle-input');
const $themeSelect    = document.getElementById('theme-select');
const $zoneSlider     = document.getElementById('zone-slider');
const $zoneCustom     = document.getElementById('zone-custom');
const $inputHours     = document.getElementById('input-hours');
const $inputMinutes   = document.getElementById('input-minutes');
const $invisHint      = document.getElementById('invisibility-hint');
const $btnMinimize    = document.getElementById('btn-minimize');
const $btnClose       = document.getElementById('btn-close');
const $countdownRow   = document.getElementById('countdown-row');
const $countdownTime  = document.getElementById('countdown-time');
const $btnCancelTimer = document.getElementById('btn-cancel-timer');

// ── State ───────────────────────────────────────────────────────────────────
let usingCustomTime = false;
let invisibilityEnabled = false;
let currentMinutes = 0;
let shutdownScheduled = false;
let promptTimeout = null;
let countdownInterval = null;
let shutdownTargetTime = null;
let previewInterval = null;

// ── Initialisation ──────────────────────────────────────────────────────────
(async function init() {
  // Greeting
  $greeting.textContent = 'Hello, Majid!';

  // Config / theme
  const config = await window.api.getConfig();
  applyTheme(config.theme || 'dark_grey');
  $themeSelect.value = config.theme || 'dark_grey';

  // Build slider ticks
  buildSliderTicks();

  // Snap slider to nearest TICK_INTERVAL and live update
  $slider.addEventListener('input', () => {
    const raw = parseInt($slider.value, 10);
    const snapped = Math.round(raw / TICK_INTERVAL) * TICK_INTERVAL;
    $slider.value = snapped;
    updateTimeDisplay(snapped);
  });

  // Custom inputs live update
  $inputHours.addEventListener('input', updateCustomTimeDisplay);
  $inputMinutes.addEventListener('input', updateCustomTimeDisplay);

  // Show time immediately on launch
  $slider.value = TICK_INTERVAL;
  updateTimeDisplay(TICK_INTERVAL);
})();

// ── Slider tick marks & labels ──────────────────────────────────────────────
function buildSliderTicks() {
  $tickLabels.innerHTML = '';
  $tickMarks.innerHTML = '';
  $hourLabels.innerHTML = '';

  // The range thumb center is offset by half-thumb-width at the extremes.
  // Chromium range inputs have an implicit padding of ~7px (half of 14px thumb).
  const thumbHalf = 7; // px, must match CSS thumb width / 2

  for (let m = 0; m <= MAX_MINUTES; m += TICK_INTERVAL) {
    const pct = m / MAX_MINUTES;

    // minute labels – absolutely positioned to align with slider track
    const lbl = document.createElement('span');
    lbl.textContent = m;
    lbl.style.position = 'absolute';
    lbl.style.left = `calc(${thumbHalf}px + ${pct} * (100% - ${thumbHalf * 2}px))`;
    lbl.style.transform = 'translateX(-50%)';
    $tickLabels.appendChild(lbl);

    // tick marks
    const tick = document.createElement('span');
    tick.className = 'tick';
    tick.style.position = 'absolute';
    tick.style.left = `calc(${thumbHalf}px + ${pct} * (100% - ${thumbHalf * 2}px))`;
    tick.style.transform = 'translateX(-50%)';
    $tickMarks.appendChild(tick);
  }

  // hour labels
  for (let h = 0; h <= MAX_MINUTES / 60; h++) {
    const pct = (h * 60) / MAX_MINUTES;
    const lbl = document.createElement('span');
    lbl.textContent = `${h} hour${h !== 1 ? 's' : ''}`;
    lbl.style.position = 'absolute';
    lbl.style.left = `calc(${thumbHalf}px + ${pct} * (100% - ${thumbHalf * 2}px))`;
    lbl.style.transform = 'translateX(-50%)';
    $hourLabels.appendChild(lbl);
  }
}

// ── Time display ────────────────────────────────────────────────────────────
function formatTime(date) {
  let h = date.getHours();
  const ampm = h >= 12 ? 'PM' : 'AM';
  h = h % 12 || 12; // convert 0→12, 13→1, etc.
  const m = String(date.getMinutes()).padStart(2, '0');
  const s = String(date.getSeconds()).padStart(2, '0');
  return `${h}:${m}:${s} ${ampm}`;
}

function updateTimeDisplay(minutes) {
  currentMinutes = minutes;
  if (minutes <= 0) {
    $shutdownTime.textContent = '--:--:-- --';
    stopPreviewTick();
    return;
  }
  // If shutdown is already scheduled, show the fixed target time
  if (shutdownTargetTime) {
    $shutdownTime.textContent = formatTime(new Date(shutdownTargetTime));
    return;
  }
  // Otherwise show a live preview that ticks with the clock
  const future = new Date(Date.now() + minutes * 60000);
  $shutdownTime.textContent = formatTime(future);
  startPreviewTick();
}

// Keep the preview ticking every second so the projected time stays current
function startPreviewTick() {
  if (previewInterval) return; // already running
  previewInterval = setInterval(() => {
    if (shutdownTargetTime || currentMinutes <= 0) { stopPreviewTick(); return; }
    const future = new Date(Date.now() + currentMinutes * 60000);
    $shutdownTime.textContent = formatTime(future);
  }, 1000);
}

function stopPreviewTick() {
  if (previewInterval) { clearInterval(previewInterval); previewInterval = null; }
}

function updateCustomTimeDisplay() {
  const h = parseInt($inputHours.value, 10) || 0;
  const m = parseInt($inputMinutes.value, 10) || 0;
  updateTimeDisplay(h * 60 + m);
}

// ── Toggle slider / custom ──────────────────────────────────────────────────
$btnToggleInput.addEventListener('click', () => {
  usingCustomTime = !usingCustomTime;
  if (usingCustomTime) {
    $zoneSlider.classList.add('hidden');
    $zoneCustom.classList.remove('hidden');
    $btnToggleInput.textContent = 'USE PRESET SLIDER TIME';
    $inputHours.value = 0;
    $inputMinutes.value = 0;
    $inputHours.focus();
    updateTimeDisplay(0);
  } else {
    $zoneCustom.classList.add('hidden');
    $zoneSlider.classList.remove('hidden');
    $btnToggleInput.textContent = 'USE CUSTOM TIME';
    updateTimeDisplay(parseInt($slider.value, 10));
  }
});

// ── Schedule shutdown ───────────────────────────────────────────────────────
$btnSchedule.addEventListener('click', async () => {
  let minutes;
  if (usingCustomTime) {
    const h = parseInt($inputHours.value, 10) || 0;
    const m = parseInt($inputMinutes.value, 10) || 0;
    minutes = h * 60 + m;
  } else {
    minutes = parseInt($slider.value, 10);
  }

  const totalSeconds = minutes * 60;

  if (totalSeconds === 0) {
    const ok = await window.api.confirm('Confirm', 'Shut down immediately?');
    if (!ok) return;
  }

  try {
    await window.api.scheduleShutdown(totalSeconds);
    shutdownScheduled = true;

    // Fix the target time and stop the preview ticker
    shutdownTargetTime = Date.now() + totalSeconds * 1000;
    stopPreviewTick();
    updateTimeDisplay(minutes);

    // Start live countdown
    startCountdown();

    // Enter timer mode & auto-enable invisibility
    enterTimerMode();

    $btnSchedule.disabled = true;
    $btnCancel.disabled = false;
    if (!usingCustomTime) $slider.disabled = true;

    // Prompt 3 min before if long enough
    if (totalSeconds > 180) {
      const delayMs = (totalSeconds - 180) * 1000;
      promptTimeout = setTimeout(async () => {
        const cancel = await window.api.confirm(
          'Cancel Shutdown?',
          'Shutdown is scheduled soon.\nDo you want to cancel it?'
        );
        if (cancel) doCancelShutdown();
      }, delayMs);
    }
  } catch (err) {
    await window.api.showError('Error', `Failed to schedule shutdown: ${err}`);
  }
});

// ── Cancel shutdown ─────────────────────────────────────────────────────────
$btnCancel.addEventListener('click', () => doCancelShutdown());

async function doCancelShutdown() {
  try {
    await window.api.cancelShutdown();
  } catch (err) {
    // Ignore – might not have a pending shutdown
  }
  shutdownScheduled = false;
  stopCountdown();
  exitTimerMode();
  if (promptTimeout) { clearTimeout(promptTimeout); promptTimeout = null; }
  $btnSchedule.disabled = false;
  $btnCancel.disabled = true;
  if (!usingCustomTime) $slider.disabled = false;
}

// ── Live countdown ──────────────────────────────────────────────────────────
function startCountdown() {
  $countdownRow.classList.remove('hidden');
  tickCountdown(); // immediate first tick
  countdownInterval = setInterval(tickCountdown, 1000);
}

function stopCountdown() {
  if (countdownInterval) { clearInterval(countdownInterval); countdownInterval = null; }
  shutdownTargetTime = null;
  $countdownRow.classList.add('hidden');
  $countdownTime.textContent = '';
}

function tickCountdown() {
  if (!shutdownTargetTime) return;
  const remaining = Math.max(0, shutdownTargetTime - Date.now());
  const totalSec = Math.floor(remaining / 1000);
  const h = Math.floor(totalSec / 3600);
  const m = Math.floor((totalSec % 3600) / 60);
  const s = totalSec % 60;
  $countdownTime.textContent = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  if (remaining <= 0) stopCountdown();
}

// ── Invisibility ────────────────────────────────────────────────────────────
$btnInvisibility.addEventListener('click', () => {
  invisibilityEnabled = !invisibilityEnabled;
  window.api.setInvisibility(invisibilityEnabled);
  if (invisibilityEnabled) {
    $btnInvisibility.textContent = 'DISABLE INVISIBILITY';
    $invisHint.textContent = 'Move your mouse away to make me invisible';
  } else {
    $btnInvisibility.textContent = 'ENABLE INVISIBILITY';
    $invisHint.textContent = '';
  }
});

// ── Theme ───────────────────────────────────────────────────────────────────
$themeSelect.addEventListener('change', () => {
  applyTheme($themeSelect.value);
  window.api.saveConfig({ theme: $themeSelect.value });
});

function applyTheme(theme) {
  document.body.className = '';
  document.body.classList.add(`theme-${theme}`);
}

// ── Window controls ─────────────────────────────────────────────────────────
$btnMinimize.addEventListener('click', () => window.api.minimize());
$btnClose.addEventListener('click', () => window.api.close());
// ── Timer mode (compact view) ──────────────────────────────────────────────
function enterTimerMode() {
  document.body.classList.add('timer-mode');
  $btnCancelTimer.classList.remove('hidden');
  window.api.setTimerMode(true);

  // Auto-enable invisibility
  if (!invisibilityEnabled) {
    invisibilityEnabled = true;
    window.api.setInvisibility(true);
    $btnInvisibility.textContent = 'DISABLE INVISIBILITY';
    $invisHint.textContent = 'Move your mouse away to make me invisible';
  }
}

function exitTimerMode() {
  document.body.classList.remove('timer-mode');
  $btnCancelTimer.classList.add('hidden');
  window.api.setTimerMode(false);

  // Disable invisibility on cancel
  if (invisibilityEnabled) {
    invisibilityEnabled = false;
    window.api.setInvisibility(false);
    $btnInvisibility.textContent = 'ENABLE INVISIBILITY';
    $invisHint.textContent = '';
  }
}

$btnCancelTimer.addEventListener('click', () => doCancelShutdown());