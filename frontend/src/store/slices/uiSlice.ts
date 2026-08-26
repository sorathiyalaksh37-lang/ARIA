// src/store/slices/uiSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { LS_KEYS } from '../../utils/constants';

type Theme = 'dark' | 'light';

interface UIState {
  theme:           Theme;
  sidebarOpen:     boolean;
  globalLoading:   boolean;
  notifications:   AppNotification[];
}

export interface AppNotification {
  id:      string;
  type:    'success' | 'error' | 'warning' | 'info';
  title:   string;
  message: string;
  read:    boolean;
  at:      string; // ISO timestamp
}

const savedTheme = (localStorage.getItem(LS_KEYS.THEME) as Theme) || 'dark';

const initialState: UIState = {
  theme:         savedTheme,
  sidebarOpen:   true,
  globalLoading: false,
  notifications: [],
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleTheme(state) {
      state.theme = state.theme === 'dark' ? 'light' : 'dark';
      localStorage.setItem(LS_KEYS.THEME, state.theme);
      document.documentElement.classList.toggle('dark', state.theme === 'dark');
    },
    setTheme(state, action: PayloadAction<Theme>) {
      state.theme = action.payload;
      localStorage.setItem(LS_KEYS.THEME, state.theme);
      document.documentElement.classList.toggle('dark', state.theme === 'dark');
    },
    toggleSidebar(state) {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setSidebarOpen(state, action: PayloadAction<boolean>) {
      state.sidebarOpen = action.payload;
    },
    setGlobalLoading(state, action: PayloadAction<boolean>) {
      state.globalLoading = action.payload;
    },
    addNotification(state, action: PayloadAction<Omit<AppNotification, 'id' | 'read' | 'at'>>) {
      state.notifications.unshift({
        ...action.payload,
        id:   Date.now().toString(),
        read: false,
        at:   new Date().toISOString(),
      });
      // Cap at 50 notifications
      state.notifications = state.notifications.slice(0, 50);
    },
    markAllRead(state) {
      state.notifications.forEach((n) => { n.read = true; });
    },
    clearNotifications(state) {
      state.notifications = [];
    },
  },
});

export const {
  toggleTheme,
  setTheme,
  toggleSidebar,
  setSidebarOpen,
  setGlobalLoading,
  addNotification,
  markAllRead,
  clearNotifications,
} = uiSlice.actions;
export default uiSlice.reducer;
