// src/store/slices/incidentsSlice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { incidentsApi } from '../../api/incidents.api';
import { Incident, IncidentFilters } from '../../types';

interface IncidentsState {
  items:       Incident[];
  selected:    Incident | null;
  total:       number;
  page:        number;
  per_page:    number;
  loading:     boolean;
  error:       string | null;
  filters:     IncidentFilters;
}

const initialState: IncidentsState = {
  items:    [],
  selected: null,
  total:    0,
  page:     1,
  per_page: 20,
  loading:  false,
  error:    null,
  filters:  {},
};

export const fetchIncidents = createAsyncThunk(
  'incidents/fetchAll',
  async (filters: IncidentFilters | undefined, { rejectWithValue }) => {
    try {
      const res = await incidentsApi.getAll(filters);
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
      const res = await incidentsApi.getById(id);
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
    setFilters(state, action: PayloadAction<IncidentFilters>) {
      state.filters = action.payload;
      state.page    = 1;
    },
    clearSelected(state) {
      state.selected = null;
    },
    upsertIncident(state, action: PayloadAction<Incident>) {
      const idx = state.items.findIndex((i) => i.id === action.payload.id);
      if (idx >= 0) {
        state.items[idx] = action.payload;
      } else {
        state.items.unshift(action.payload);
        state.total += 1;
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchIncidents.pending, (state) => {
        state.loading = true;
        state.error   = null;
      })
      .addCase(fetchIncidents.fulfilled, (state, action) => {
        state.loading  = false;
        state.items    = action.payload.data;
        state.total    = action.payload.total;
        state.page     = action.payload.page;
        state.per_page = action.payload.per_page;
      })
      .addCase(fetchIncidents.rejected, (state, action) => {
        state.loading = false;
        state.error   = action.payload as string;
      })
      .addCase(fetchIncidentById.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchIncidentById.fulfilled, (state, action) => {
        state.loading  = false;
        state.selected = action.payload;
      })
      .addCase(fetchIncidentById.rejected, (state, action) => {
        state.loading = false;
        state.error   = action.payload as string;
      });
  },
});

export const { setFilters, clearSelected, upsertIncident } =
  incidentsSlice.actions;
export default incidentsSlice.reducer;
