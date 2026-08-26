// src/store/index.ts
import { configureStore } from '@reduxjs/toolkit';
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
import authReducer      from './slices/authSlice';
import incidentsReducer from './slices/incidentsSlice';
import uiReducer        from './slices/uiSlice';

export const store = configureStore({
  reducer: {
    auth:      authReducer,
    incidents: incidentsReducer,
    ui:        uiReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({ serializableCheck: false }),
});

// Typed hooks
export type RootState   = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export const useAppDispatch: () => AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
