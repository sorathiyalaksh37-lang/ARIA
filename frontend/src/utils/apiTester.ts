/**
 * API Testing Utility
 * Comprehensive testing tool for all 32+ API endpoints
 */
import apiClient from './apiClient';
import { errorHandler } from './errorHandler';

// ============================================================================
// TEST RESULTS INTERFACE
// ============================================================================

export interface TestResult {
  endpoint: string;
  method: string;
  status: 'success' | 'failure' | 'skipped';
  statusCode?: number;
  duration?: number;
  error?: string;
  response?: any;
}

export interface TestSuite {
  name: string;
  tests: TestResult[];
  totalTests: number;
  passed: number;
  failed: number;
  skipped: number;
  duration: number;
}

// ============================================================================
// API TESTER CLASS
// ============================================================================

class APITester {
  private results: TestResult[] = [];
  private startTime: number = 0;
  private authToken: string | null = null;

  /**
   * Run all API tests
   */
  async runAllTests(): Promise<TestSuite> {
    this.results = [];
    this.startTime = Date.now();

    console.log('🚀 Starting ARIA API Integration Tests...\n');

    // Authentication Tests
    await this.testAuthEndpoints();

    // Incident Tests
    await this.testIncidentEndpoints();

    // Hospital Tests
    await this.testHospitalEndpoints();

    // Ambulance Tests
    await this.testAmbulanceEndpoints();

    // Dashboard Tests
    await this.testDashboardEndpoints();

    // Resource Allocation Tests
    await this.testResourceEndpoints();

    // WebSocket Tests
    await this.testWebSocketConnection();

    return this.generateReport();
  }

  // ============================================================================
  // AUTHENTICATION TESTS
  // ============================================================================

  private async testAuthEndpoints() {
    console.log('🔐 Testing Authentication Endpoints...');

    // Test login
    await this.test('POST /api/v1/auth/login', async () => {
      const response = await apiClient.post('/api/v1/auth/login', {
        username: 'admin',
        password: 'admin123',
      });
      
      if (response.access_token) {
        this.authToken = response.access_token;
        apiClient.setAuthTokens(response.access_token, response.refresh_token);
      }
      
      return response;
    });

    // Test get current user
    await this.test('GET /api/v1/auth/me', async () => {
      return await apiClient.get('/api/v1/auth/me');
    });

    // Test token refresh
    await this.test('POST /api/v1/auth/refresh', async () => {
      const refreshToken = localStorage.getItem('refresh_token');
      return await apiClient.post('/api/v1/auth/refresh', {
        refresh_token: refreshToken,
      });
    });
  }

  // ============================================================================
  // INCIDENT TESTS
  // ============================================================================

  private async testIncidentEndpoints() {
    console.log('🚨 Testing Incident Endpoints...');

    let incidentId: string | undefined;

    // Create incident
    await this.test('POST /api/v1/incidents', async () => {
      const response = await apiClient.post('/api/v1/incidents', {
        title: 'Test Road Accident',
        description: 'Multiple vehicle collision on Highway 101',
        incident_type: 'road_accident',
        severity: 'high',
        location: 'Highway 101, San Francisco',
        latitude: 37.7749,
        longitude: -122.4194,
        victim_count: 3,
        caller_phone: '+1234567890',
      });
      incidentId = response.id;
      return response;
    });

    // Get all incidents
    await this.test('GET /api/v1/incidents', async () => {
      return await apiClient.get('/api/v1/incidents');
    });

    // Get incident by ID
    if (incidentId) {
      await this.test(`GET /api/v1/incidents/${incidentId}`, async () => {
        return await apiClient.get(`/api/v1/incidents/${incidentId}`);
      });

      // Approve incident plan
      await this.test(`POST /api/v1/incidents/${incidentId}/approve`, async () => {
        return await apiClient.post(`/api/v1/incidents/${incidentId}/approve`, {
          approved_by: 'Test User',
        });
      });

      // Dispatch incident
      await this.test(`POST /api/v1/incidents/${incidentId}/dispatch`, async () => {
        return await apiClient.post(`/api/v1/incidents/${incidentId}/dispatch`);
      });

      // Update incident status
      await this.test(`PATCH /api/v1/incidents/${incidentId}/status`, async () => {
        return await apiClient.patch(`/api/v1/incidents/${incidentId}/status`, {
          status: 'in_progress',
        });
      });
    }
  }

  // ============================================================================
  // HOSPITAL TESTS
  // ============================================================================

  private async testHospitalEndpoints() {
    console.log('🏥 Testing Hospital Endpoints...');

    // Get all hospitals
    await this.test('GET /api/v1/hospitals', async () => {
      return await apiClient.get('/api/v1/hospitals');
    });

    // Get nearby hospitals
    await this.test('GET /api/v1/hospitals/nearby', async () => {
      return await apiClient.get('/api/v1/hospitals/nearby', {
        params: {
          latitude: 37.7749,
          longitude: -122.4194,
          radius: 10,
        },
      });
    });

    // Rank hospitals (ML)
    await this.test('POST /api/v1/hospitals/rank', async () => {
      return await apiClient.post('/api/v1/hospitals/rank', {
        latitude: 37.7749,
        longitude: -122.4194,
        severity: 'high',
        required_specialties: ['trauma', 'orthopedic'],
      });
    });

    // Check bed availability (ML)
    await this.test('POST /api/v1/hospitals/availability', async () => {
      return await apiClient.post('/api/v1/hospitals/availability', {
        hospital_ids: [1, 2, 3],
        required_beds: 2,
        urgency: 'high',
      });
    });
  }

  // ============================================================================
  // AMBULANCE TESTS
  // ============================================================================

  private async testAmbulanceEndpoints() {
    console.log('🚑 Testing Ambulance Endpoints...');

    // Get all ambulances
    await this.test('GET /api/v1/ambulances', async () => {
      return await apiClient.get('/api/v1/ambulances');
    });

    // Get available ambulances
    await this.test('GET /api/v1/ambulances/available', async () => {
      return await apiClient.get('/api/v1/ambulances/available');
    });

    // Find nearest ambulance (ML)
    await this.test('POST /api/v1/ambulances/nearest', async () => {
      return await apiClient.post('/api/v1/ambulances/nearest', {
        latitude: 37.7749,
        longitude: -122.4194,
        required_type: 'ALS',
      });
    });

    // Update ambulance location
    await this.test('PATCH /api/v1/ambulances/1/location', async () => {
      return await apiClient.patch('/api/v1/ambulances/1/location', {
        latitude: 37.7750,
        longitude: -122.4195,
      });
    });

    // Update ambulance status
    await this.test('PATCH /api/v1/ambulances/1/status', async () => {
      return await apiClient.patch('/api/v1/ambulances/1/status', {
        status: 'available',
      });
    });
  }

  // ============================================================================
  // DASHBOARD TESTS
  // ============================================================================

  private async testDashboardEndpoints() {
    console.log('📊 Testing Dashboard Endpoints...');

    // Get dashboard stats
    await this.test('GET /api/v1/dashboard/stats', async () => {
      return await apiClient.get('/api/v1/dashboard/stats');
    });

    // Get active incidents
    await this.test('GET /api/v1/dashboard/active-incidents', async () => {
      return await apiClient.get('/api/v1/dashboard/active-incidents');
    });

    // Get agent status
    await this.test('GET /api/v1/dashboard/agent-status', async () => {
      return await apiClient.get('/api/v1/dashboard/agent-status');
    });

    // Get hotspots (ML)
    await this.test('GET /api/v1/dashboard/hotspots', async () => {
      return await apiClient.get('/api/v1/dashboard/hotspots');
    });
  }

  // ============================================================================
  // RESOURCE ALLOCATION TESTS
  // ============================================================================

  private async testResourceEndpoints() {
    console.log('🎯 Testing Resource Allocation Endpoints...');

    // Allocate resources
    await this.test('POST /api/v1/resource-allocation/allocate', async () => {
      return await apiClient.post('/api/v1/resource-allocation/allocate', {
        incident_id: 1,
        required_ambulances: 2,
        required_hospitals: 1,
      });
    });

    // Get allocation history
    await this.test('GET /api/v1/resource-allocation/history', async () => {
      return await apiClient.get('/api/v1/resource-allocation/history', {
        params: { limit: 10 },
      });
    });
  }

  // ============================================================================
  // WEBSOCKET TESTS
  // ============================================================================

  private async testWebSocketConnection() {
    console.log('🔌 Testing WebSocket Connection...');

    await this.test('WebSocket Connection', async () => {
      return new Promise((resolve, reject) => {
        const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/api/v1/ws';
        const token = this.authToken || localStorage.getItem('access_token');
        
        const ws = new WebSocket(`${wsUrl}?token=${token}`);
        
        const timeout = setTimeout(() => {
          ws.close();
          reject(new Error('WebSocket connection timeout'));
        }, 5000);

        ws.onopen = () => {
          clearTimeout(timeout);
          ws.close();
          resolve({ status: 'connected' });
        };

        ws.onerror = (error) => {
          clearTimeout(timeout);
          reject(error);
        };
      });
    });
  }

  // ============================================================================
  // TEST HELPERS
  // ============================================================================

  private async test(
    name: string,
    fn: () => Promise<any>
  ): Promise<void> {
    const startTime = Date.now();
    
    try {
      const response = await fn();
      const duration = Date.now() - startTime;
      
      this.results.push({
        endpoint: name,
        method: name.split(' ')[0],
        status: 'success',
        statusCode: 200,
        duration,
        response,
      });
      
      console.log(`✅ ${name} (${duration}ms)`);
    } catch (error: any) {
      const duration = Date.now() - startTime;
      const apiError = errorHandler.handle(error);
      
      this.results.push({
        endpoint: name,
        method: name.split(' ')[0],
        status: 'failure',
        statusCode: error.response?.status,
        duration,
        error: apiError.message,
      });
      
      console.log(`❌ ${name} - ${apiError.message}`);
    }
  }

  private generateReport(): TestSuite {
    const duration = Date.now() - this.startTime;
    const passed = this.results.filter((r) => r.status === 'success').length;
    const failed = this.results.filter((r) => r.status === 'failure').length;
    const skipped = this.results.filter((r) => r.status === 'skipped').length;

    const report: TestSuite = {
      name: 'ARIA API Integration Tests',
      tests: this.results,
      totalTests: this.results.length,
      passed,
      failed,
      skipped,
      duration,
    };

    // Print summary
    console.log('\n' + '='.repeat(50));
    console.log('📋 TEST SUMMARY');
    console.log('='.repeat(50));
    console.log(`Total Tests: ${report.totalTests}`);
    console.log(`✅ Passed: ${passed}`);
    console.log(`❌ Failed: ${failed}`);
    console.log(`⏭️  Skipped: ${skipped}`);
    console.log(`⏱️  Duration: ${(duration / 1000).toFixed(2)}s`);
    console.log('='.repeat(50) + '\n');

    return report;
  }

  /**
   * Export test results to JSON
   */
  exportResults(): string {
    return JSON.stringify(this.generateReport(), null, 2);
  }
}

// ============================================================================
// EXPORT SINGLETON
// ============================================================================

export const apiTester = new APITester();
export default apiTester;
