// src/store/slices/authSlice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { authApi } from '../../api/auth';
import { LS_KEYS } from '../../utils/constants';
import { User, LoginFormData } from '../../types';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  user:            JSON.parse(localStorage.getItem(LS_KEYS.USER) || 'null'),
  accessToken:     localStorage.getItem(LS_KEYS.ACCESS_TOKEN),
  isAuthenticated: !!localStorage.getItem(LS_KEYS.ACCESS_TOKEN),
  loading:         false,
  error:           null,
};

// ── Async thunks ──────────────────────────────────────────

export const login = createAsyncThunk(
  'auth/login',
  async (credentials: LoginFormData, { rejectWithValue }) => {
    try {
      const res = await authApi.login(credentials);
      const tokens = res.data.data;
      localStorage.setItem(LS_KEYS.ACCESS_TOKEN,  tokens.access_token);
      localStorage.setItem(LS_KEYS.REFRESH_TOKEN, tokens.refresh_token);
      // Fetch current user profile
      const userRes = await authApi.getCurrentUser();
      const user = userRes.data.data;
      localStorage.setItem(LS_KEYS.USER, JSON.stringify(user));
      return { tokens, user };
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { message?: string } } })?.response?.data?.message ||
        'Login failed';
      return rejectWithValue(msg);
    }
  }
);

export const logout = createAsyncThunk('auth/logout', async () => {
  try {
    await authApi.logout();
  } catch {
    // Ignore server errors on logout
  } finally {
    localStorage.removeItem(LS_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(LS_KEYS.REFRESH_TOKEN);
    localStorage.removeItem(LS_KEYS.USER);
  }
});

// ── Slice ─────────────────────────────────────────────────

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setUser(state, action: PayloadAction<User>) {
      state.user = action.payload;
    },
    clearError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // login
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error   = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading         = false;
        state.isAuthenticated = true;
        state.accessToken     = action.payload.tokens.access_token;
        state.user            = action.payload.user;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error   = action.payload as string;
      })
      // logout
      .addCase(logout.fulfilled, (state) => {
        state.user            = null;
        state.accessToken     = null;
        state.isAuthenticated = false;
      });
  },
});

export const { setUser, clearError } = authSlice.actions;
export default authSlice.reducer;
