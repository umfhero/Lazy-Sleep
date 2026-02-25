const { app, BrowserWindow, ipcMain, dialog, screen } = require('electron');
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');
const os = require('os');

// ── Config persistence ──────────────────────────────────────────────────────
const CONFIG_PATH = path.join(app.getPath('userData'), 'config.json');

function loadConfig() {
  try {
    if (fs.existsSync(CONFIG_PATH)) {
      return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'));
    }
  } catch (e) {
    console.error('Config load error:', e);
  }
  return { theme: 'dark_grey' };
}

function saveConfig(config) {
  try {
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
  } catch (e) {
    console.error('Config save error:', e);
  }
}

// ── Window ──────────────────────────────────────────────────────────────────
let mainWindow;
let invisibilityEnabled = false;
let mouseCheckInterval = null;
const DETECTION_RADIUS = 200;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 700,
    height: 560,
    alwaysOnTop: true,
    frame: false,
    resizable: false,
    icon: path.join(__dirname, 'clock2_256.ico'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));

  // Start mouse-proximity check loop
  startMouseCheck();
}

// ── Mouse proximity → invisibility ──────────────────────────────────────────
function startMouseCheck() {
  mouseCheckInterval = setInterval(() => {
    if (!invisibilityEnabled || !mainWindow) return;
    const cursorPos = screen.getCursorScreenPoint();
    const bounds = mainWindow.getBounds();

    const inside =
      cursorPos.x >= bounds.x - DETECTION_RADIUS &&
      cursorPos.x <= bounds.x + bounds.width + DETECTION_RADIUS &&
      cursorPos.y >= bounds.y - DETECTION_RADIUS &&
      cursorPos.y <= bounds.y + bounds.height + DETECTION_RADIUS;

    mainWindow.setOpacity(inside ? 1.0 : 0.0);
  }, 300);
}

// ── IPC handlers ────────────────────────────────────────────────────────────

// Config
ipcMain.handle('get-config', () => loadConfig());
ipcMain.handle('save-config', (_e, config) => {
  saveConfig(config);
});

// Username
ipcMain.handle('get-username', () => {
  const info = os.userInfo();
  const name = info.username || 'User';
  // Capitalize first letter
  return name.charAt(0).toUpperCase() + name.slice(1);
});

// Shutdown
ipcMain.handle('schedule-shutdown', (_e, seconds) => {
  return new Promise((resolve, reject) => {
    exec(`shutdown -s -t ${seconds}`, (err) => {
      if (err) reject(err.message);
      else resolve(true);
    });
  });
});

ipcMain.handle('cancel-shutdown', () => {
  return new Promise((resolve, reject) => {
    exec('shutdown -a', (err) => {
      if (err) reject(err.message);
      else resolve(true);
    });
  });
});

// Invisibility
ipcMain.handle('set-invisibility', (_e, enabled) => {
  invisibilityEnabled = enabled;
  if (!enabled && mainWindow) {
    mainWindow.setOpacity(1.0);
  }
});

// Window controls (frameless)
ipcMain.on('window-minimize', () => mainWindow?.minimize());
ipcMain.on('window-close', () => mainWindow?.close());

// Timer mode – resize window
const FULL_SIZE = { width: 700, height: 560 };
const TIMER_SIZE = { width: 380, height: 240 };

ipcMain.handle('set-timer-mode', (_e, enabled) => {
  if (!mainWindow) return;
  const size = enabled ? TIMER_SIZE : FULL_SIZE;
  mainWindow.setMinimumSize(size.width, size.height);
  mainWindow.setSize(size.width, size.height, true);
  mainWindow.center();
});

// Confirm dialogs
ipcMain.handle('confirm-dialog', async (_e, title, message) => {
  const result = await dialog.showMessageBox(mainWindow, {
    type: 'question',
    buttons: ['Yes', 'No'],
    defaultId: 1,
    title,
    message,
  });
  return result.response === 0; // true if "Yes"
});

ipcMain.handle('show-info', async (_e, title, message) => {
  await dialog.showMessageBox(mainWindow, { type: 'info', title, message });
});

ipcMain.handle('show-error', async (_e, title, message) => {
  await dialog.showMessageBox(mainWindow, { type: 'error', title, message });
});

// ── Lifecycle ───────────────────────────────────────────────────────────────
app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (mouseCheckInterval) clearInterval(mouseCheckInterval);
  app.quit();
});
