import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { incidentsApi } from '../../api/incidents';
import { Incident } from '../../types';

interface IncidentsState {
  incidents:   Incident[];
  selected:    Incident | null;
  total:       number;
  page:        number;
  per_page:    number;
  isLoading:   boolean;
  error:       string | null;
  filters:     any;
}

const initialState: IncidentsState = {
  incidents: [],
  selected: null,
  total:    0,
  page:     1,
  per_page: 20,
  isLoading:false,
  error:    null,
  filters:  {},
};

export const fetchIncidents = createAsyncThunk(
  'incidents/fetchAll',
  async (filters: any | undefined, { rejectWithValue }) => {
    try {
      const res = await incidentsApi.getIncidents(filters);
      return res.data;
    } catch (err: unknown) {
      return rejectWithValue(
        (err as { response?: { data?: { message?: string } } })?.response?.data?.message ||
          'Failed to fetch incidents'
      );
    }
  }
);

export const fetchIncidentById = createAsyncThunk(
  'incidents/fetchById',
  async (id: string, { rejectWithValue }) => {
    try {
      const res = await incidentsApi.getIncidentById(id);
      return res.data.data;
    } catch (err: unknown) {
      return rejectWithValue(
        (err as { response?: { data?: { message?: string } } })?.response?.data?.message ||
          'Failed to fetch incident'
      );
    }
  }
);

const incidentsSlice = createSlice({
  name: 'incidents',
  initialState,
  reducers: {
    setFilters(state, action: PayloadAction<any>) {
      state.filters = action.payload;
      state.page    = 1;
    },
    clearSelected(state) {
      state.selected = null;
    },
    upsertIncident(state, action: PayloadAction<Incident>) {
      const idx = state.incidents.findIndex((i) => i.id === action.payload.id);
      if (idx >= 0) {
        state.incidents[idx] = action.payload;
      } else {
        state.incidents.unshift(action.payload);
        state.total += 1;
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchIncidents.pending, (state) => {
        state.isLoading = true;
        state.error   = null;
      })
      .addCase(fetchIncidents.fulfilled, (state, action) => {
        state.isLoading  = false;
        state.incidents  = action.payload.data;
        state.total    = action.payload.total;
        state.page     = action.payload.page;
        state.per_page = action.payload.per_page;
      })
      .addCase(fetchIncidents.rejected, (state, action) => {
        state.isLoading = false;
        state.error   = action.payload as string;
      })
      .addCase(fetchIncidentById.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(fetchIncidentById.fulfilled, (state, action) => {
        state.isLoading  = false;
        state.selected = action.payload;
      })
      .addCase(fetchIncidentById.rejected, (state, action) => {
        state.isLoading = false;
        state.error   = action.payload as string;
      });
  },
});

export const { setFilters, clearSelected, upsertIncident } =
  incidentsSlice.actions;
export default incidentsSlice.reducer;
