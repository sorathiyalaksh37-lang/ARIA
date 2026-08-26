import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { ambulancesApi } from '../../api/ambulances';
import { Ambulance, AmbulanceUpdate } from '../../types';

interface AmbulanceState {
  ambulances: Ambulance[];
  currentAmbulance: Ambulance | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: AmbulanceState = {
  ambulances: [],
  currentAmbulance: null,
  isLoading: false,
  error: null,
};

export const fetchAmbulances = createAsyncThunk(
  'ambulances/fetchAmbulances',
  async (params?: any) => {
    const response = await ambulancesApi.getAmbulances(params);
    return response.data.data;
  }
);

export const fetchAmbulanceById = createAsyncThunk(
  'ambulances/fetchAmbulanceById',
  async (id: string) => {
    const response = await ambulancesApi.getAmbulanceById(id);
    return response.data.data;
  }
);

export const fetchAvailableAmbulances = createAsyncThunk(
  'ambulances/fetchAvailable',
  async () => {
    const response = await ambulancesApi.getAvailableAmbulances();
    return response.data.data;
  }
);

const ambulanceSlice = createSlice({
  name: 'ambulances',
  initialState,
  reducers: {
    setCurrentAmbulance(state, action: PayloadAction<Ambulance | null>) {
      state.currentAmbulance = action.payload;
    },
    updateAmbulanceOptimistically(state, action: PayloadAction<AmbulanceUpdate>) {
      const { current_incident_id, ...rest } = action.payload;
      const cleanPayload = {
        ...rest,
        ...(current_incident_id !== undefined ? { current_incident_id: current_incident_id || undefined } : {})
      };

      const index = state.ambulances.findIndex(a => a.id === action.payload.id);
      if (index !== -1) {
        state.ambulances[index] = {
          ...state.ambulances[index],
          ...cleanPayload,
        };
      }
      if (state.currentAmbulance?.id === action.payload.id) {
        state.currentAmbulance = {
          ...state.currentAmbulance,
          ...cleanPayload,
        };
      }
    },
    clearError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAmbulances.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchAmbulances.fulfilled, (state, action) => {
        state.isLoading = false;
        state.ambulances = action.payload;
      })
      .addCase(fetchAmbulances.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to fetch ambulances';
      })
      .addCase(fetchAmbulanceById.fulfilled, (state, action) => {
        state.currentAmbulance = action.payload;
      });
  },
});

export const { setCurrentAmbulance, updateAmbulanceOptimistically, clearError } = ambulanceSlice.actions;
export default ambulanceSlice.reducer;
