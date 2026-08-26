import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { hospitalsApi } from '../../api/hospitals';
import { Hospital, HospitalSearchFilters } from '../../types';

interface HospitalState {
  hospitals: Hospital[];
  currentHospital: Hospital | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: HospitalState = {
  hospitals: [],
  currentHospital: null,
  isLoading: false,
  error: null,
};

export const fetchHospitals = createAsyncThunk(
  'hospitals/fetchHospitals',
  async (filters?: HospitalSearchFilters) => {
    const response = await hospitalsApi.getHospitals(filters);
    return response.data.data;
  }
);

export const fetchHospitalById = createAsyncThunk(
  'hospitals/fetchHospitalById',
  async (id: string) => {
    const response = await hospitalsApi.getHospitalById(id);
    return response.data.data;
  }
);

export const findNearbyHospitals = createAsyncThunk(
  'hospitals/findNearby',
  async (data: { lat: number; lng: number; radius_km?: number }) => {
    const response = await hospitalsApi.findNearbyHospitals(data);
    return response.data.data;
  }
);

const hospitalSlice = createSlice({
  name: 'hospitals',
  initialState,
  reducers: {
    setCurrentHospital(state, action: PayloadAction<Hospital | null>) {
      state.currentHospital = action.payload;
    },
    clearError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchHospitals.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchHospitals.fulfilled, (state, action) => {
        state.isLoading = false;
        state.hospitals = action.payload;
      })
      .addCase(fetchHospitals.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to fetch hospitals';
      })
      .addCase(fetchHospitalById.fulfilled, (state, action) => {
        state.currentHospital = action.payload;
      })
      .addCase(findNearbyHospitals.fulfilled, (state, action) => {
        state.hospitals = action.payload;
      });
  },
});

export const { setCurrentHospital, clearError } = hospitalSlice.actions;
export default hospitalSlice.reducer;
