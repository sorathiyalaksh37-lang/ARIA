import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { WebSocketMessage } from '../../types';

interface WebSocketState {
  isConnected: boolean;
  lastMessage: WebSocketMessage | null;
  events: WebSocketMessage[];
}

const initialState: WebSocketState = {
  isConnected: false,
  lastMessage: null,
  events: [],
};

const websocketSlice = createSlice({
  name: 'websocket',
  initialState,
  reducers: {
    connect(state) {
      state.isConnected = true;
    },
    disconnect(state) {
      state.isConnected = false;
    },
    addEvent(state, action: PayloadAction<WebSocketMessage>) {
      state.lastMessage = action.payload;
      state.events.push(action.payload);
      // Keep only last 100 events to prevent memory leaks
      if (state.events.length > 100) {
        state.events.shift();
      }
    },
    clearEvents(state) {
      state.events = [];
      state.lastMessage = null;
    }
  },
});

export const { connect, disconnect, addEvent, clearEvents } = websocketSlice.actions;
export default websocketSlice.reducer;
