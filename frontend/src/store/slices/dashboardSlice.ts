import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { dashboardApi } from '../../api/dashboard';
import { DashboardStats, ActiveIncident, ResourceStatus, Hotspot, AnalyticsData, AgentStatus } from '../../types';

interface DashboardState {
  stats: DashboardStats | null;
  activeIncidents: any[];
  resourceStatus: ResourceStatus | null;
  hotspots: Hotspot[];
  analytics: AnalyticsData | null;
  agentStatuses: Record<string, AgentStatus>;
  isLoading: boolean;
  error: string | null;
}

const initialState: DashboardState = {
  stats: null,
  activeIncidents: [],
  resourceStatus: null,
  hotspots: [],
  analytics: null,
  agentStatuses: {},
  isLoading: false,
  error: null,
};

export const fetchDashboardStats = createAsyncThunk('dashboard/fetchStats', async () => {
  const response = await dashboardApi.getStats();
  return response.data.data;
});

export const fetchHotspots = createAsyncThunk('dashboard/fetchHotspots', async () => {
  const response = await dashboardApi.getHotspots();
  return response.data.data;
});

const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState,
  reducers: {
    updateDashboardStats(state, action: PayloadAction<Partial<DashboardStats>>) {
      if (state.stats) {
        state.stats = { ...state.stats, ...action.payload };
      }
    },
    updateAgentStatus(state, action: PayloadAction<AgentStatus>) {
      state.agentStatuses[action.payload.agent_id] = action.payload;
    },
    clearError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchDashboardStats.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(fetchDashboardStats.fulfilled, (state, action) => {
        state.isLoading = false;
        state.stats = action.payload;
      })
      .addCase(fetchDashboardStats.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to fetch dashboard stats';
      })
      .addCase(fetchHotspots.fulfilled, (state, action) => {
        state.hotspots = action.payload;
      });
  },
});

export const { updateDashboardStats, updateAgentStatus, clearError } = dashboardSlice.actions;
export default dashboardSlice.reducer;
