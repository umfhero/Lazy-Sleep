const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  // Config
  getConfig: () => ipcRenderer.invoke('get-config'),
  saveConfig: (config) => ipcRenderer.invoke('save-config', config),

  // User
  getUsername: () => ipcRenderer.invoke('get-username'),

  // Shutdown
  scheduleShutdown: (seconds) => ipcRenderer.invoke('schedule-shutdown', seconds),
  cancelShutdown: () => ipcRenderer.invoke('cancel-shutdown'),

  // Invisibility
  setInvisibility: (enabled) => ipcRenderer.invoke('set-invisibility', enabled),

  // Dialogs
  confirm: (title, message) => ipcRenderer.invoke('confirm-dialog', title, message),
  showInfo: (title, message) => ipcRenderer.invoke('show-info', title, message),
  showError: (title, message) => ipcRenderer.invoke('show-error', title, message),

  // Window controls
  minimize: () => ipcRenderer.send('window-minimize'),
  close: () => ipcRenderer.send('window-close'),

  // Timer mode
  setTimerMode: (enabled) => ipcRenderer.invoke('set-timer-mode', enabled),
});
