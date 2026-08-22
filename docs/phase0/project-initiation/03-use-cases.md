# ARIA — Use Case Documentation
## Comprehensive Use Case Analysis

**Project:** ARIA (AI Rescue Assistance)  
**Full Name:** ARIA — AI Rescue Assistance Emergency Response Platform  
**Date:** August 22, 2026  
**Version:** 1.0  
**Status:** Draft

---

## 1. System Actors

### 1.1 Primary Actors

| Actor | Description | Access Level | Primary Goals |
|-------|-------------|--------------|---------------|
| **Dispatcher** | Receives emergency calls, enters incident reports into system | Standard User | Submit accurate incident reports quickly |
| **Emergency Coordinator** | Reviews AI-generated plans, approves/modifies/rejects, oversees incident execution | Power User | Ensure optimal response plans, monitor execution |
| **Hospital Admin** | Manages hospital capacity, receives patient notifications, updates availability | Resource Provider | Maintain accurate capacity data, prepare for incoming patients |
| **Ambulance Crew** | Receives dispatch orders, updates location/status, accesses patient information | Field User | Receive clear orders, navigate efficiently, update status |
| **Blood Bank Staff** | Manages inventory, receives blood requests, confirms availability | Resource Provider | Fulfill blood requests accurately and quickly |

### 1.2 Secondary Actors

| Actor | Description | Access Level | Primary Goals |
|-------|-------------|--------------|---------------|
| **System Admin** | Manages users, roles, system configuration, monitoring | Administrator | Ensure system reliability, manage access control |
| **Patient/Family** | Receives updates on incident status and response (optional feature) | Limited Read | Stay informed about response progress |

### 1.3 External System Actors

| Actor | Description | Integration Type | Purpose |
|-------|-------------|------------------|---------|
| **Maps API** | Google Maps / OSRM | REST API | Route calculation, traffic data, ETA estimation |
| **SMS Gateway** | Twilio | REST API | Send SMS notifications to all stakeholders |
| **Email Service** | SendGrid / AWS SES | REST API | Send email notifications and reports |
| **LLM Service** | OpenAI GPT-4 | REST API | Natural language understanding, plan generation |
| **Speech-to-Text** | OpenAI Whisper | REST API | Voice recording transcription |
| **Vision API** | OpenAI GPT-4 Vision | REST API | Scene image analysis |

---

## 2. Use Case Catalog

### 2.1 Use Cases by Actor

#### **Dispatcher Use Cases**
1. UC-01: Submit Emergency Incident (Text)
2. UC-02: Submit Emergency Incident (Voice Recording)
3. UC-03: Submit Emergency Incident (Image Upload)
4. UC-04: Submit Emergency Incident (GPS Location)
5. UC-05: Update Incident Details
6. UC-06: View Incident Status

#### **Emergency Coordinator Use Cases**
7. UC-07: View Active Incidents
8. UC-08: View Incident Details
9. UC-09: Review AI-Generated Response Plan
10. UC-10: Approve Response Plan
11. UC-11: Modify Response Plan
12. UC-12: Reject Response Plan
13. UC-13: Manually Create Response Plan
14. UC-14: Dispatch Response Plan
15. UC-15: Monitor Incident Execution (Real-Time)
16. UC-16: Communicate with Field Resources
17. UC-17: Escalate Incident
18. UC-18: Close Incident
19. UC-19: View Analytics Dashboard
20. UC-20: Generate Incident Reports

#### **Hospital Admin Use Cases**
21. UC-21: Update Hospital Availability
22. UC-22: Update Bed Capacity
23. UC-23: Update Specialist Availability
24. UC-24: View Incoming Patient Pipeline
25. UC-25: Acknowledge Patient Notification
26. UC-26: Provide Patient Outcome Feedback

#### **Ambulance Crew Use Cases**
27. UC-27: Receive Dispatch Order
28. UC-28: View Patient Details
29. UC-29: Navigate to Incident Location
30. UC-30: Update Ambulance Status
31. UC-31: Update Location (GPS Tracking)
32. UC-32: Report Delays or Issues
33. UC-33: Confirm Patient Handoff

#### **Blood Bank Staff Use Cases**
34. UC-34: View Blood Requests
35. UC-35: Update Blood Inventory
36. UC-36: Confirm Blood Availability
37. UC-37: Reserve Blood Units
38. UC-38: Track Blood Delivery

#### **System Admin Use Cases**
39. UC-39: Create User Account
40. UC-40: Assign User Roles
41. UC-41: Configure System Settings
42. UC-42: View System Logs
43. UC-43: Monitor System Performance
44. UC-44: Manage API Integrations

---

## 3. Detailed Use Cases (Top 20 Critical)

### UC-01: Submit Emergency Incident (Text)

**ID:** UC-01  
**Actor:** Dispatcher  
**Priority:** P0 (Must Have)  
**Frequency:** High (100+ times/day)

**Description:**  
Dispatcher enters emergency incident information via text form to initiate AI-powered coordination.

**Preconditions:**
- Dispatcher is authenticated
- Dispatcher has "Submit Incident" permission
- System is operational

**Basic Flow:**
1. Dispatcher clicks "New Incident" button
2. System displays incident submission form
3. Dispatcher enters incident details:
   - Location (address or GPS coordinates)
   - Incident type (accident, medical emergency, fire, etc.)
   - Severity (if known)
   - Number of victims
   - Additional notes
4. Dispatcher clicks "Submit"
5. System validates input data
6. System creates incident record with unique ID
7. System triggers AI agent processing
8. System displays confirmation with incident ID
9. System shows real-time agent execution status

**Alternative Flows:**
- **A1: Auto-Fill Location (GPS)**
  - 3a. Dispatcher clicks "Use Current Location"
  - 3b. System captures GPS coordinates automatically
  - 3c. System reverse-geocodes to address
  - 3d. Continue from step 4

- **A2: Voice Dictation**
  - 3a. Dispatcher clicks microphone icon
  - 3b. System captures voice input
  - 3c. System transcribes using Whisper API
  - 3d. System populates form fields
  - 3e. Continue from step 4

**Exception Flows:**
- **E1: Invalid Location**
  - 5a. System detects invalid address/coordinates
  - 5b. System displays error: "Invalid location. Please verify address."
  - 5c. Return to step 3

- **E2: Required Fields Missing**
  - 5a. System detects missing required fields
  - 5b. System highlights fields in red
  - 5c. Return to step 3

- **E3: System Overload**
  - 6a. System detects >100 active incidents
  - 6b. System displays warning: "High system load. Incident queued."
  - 6c. System creates incident with "Queued" status
  - 6d. System processes when capacity available

**Postconditions:**
- Incident record created in database
- AI agent processing initiated
- Incident visible in coordinator dashboard
- Audit log entry created

**Business Rules:**
- BR-01: All incidents must have location (address or GPS)
- BR-02: Incident type is required
- BR-03: Incident ID format: INC-YYYYMMDD-NNNN
- BR-04: Processing must start within 5 seconds of submission

**Non-Functional Requirements:**
- NFR-01: Form submission must complete within 2 seconds
- NFR-02: System must support 50 concurrent incident submissions
- NFR-03: All input fields must be validated client-side and server-side

---

### UC-09: Review AI-Generated Response Plan

**ID:** UC-09  
**Actor:** Emergency Coordinator  
**Priority:** P0 (Must Have)  
**Frequency:** High (every incident)

**Description:**  
Coordinator reviews the AI-generated response plan, evaluates recommendations, and decides whether to approve, modify, or reject.

**Preconditions:**
- Coordinator is authenticated
- Incident exists with status "Plan Ready"
- AI agent processing completed successfully
- Response plan generated

**Basic Flow:**
1. Coordinator receives notification: "Plan ready for Incident #XXXX"
2. Coordinator clicks notification or navigates to incident
3. System displays comprehensive response plan:
   - **Summary Section:**
     - Incident severity
     - Estimated victim count
     - Total response time
     - Resources allocated
   - **Resource Allocation:**
     - Hospitals (ranked with rationale)
     - Ambulances (assigned with routes)
     - Blood banks (pre-coordinated supplies)
   - **Timeline:**
     - Estimated dispatch time
     - Ambulance ETAs
     - Hospital arrival times
   - **Map Visualization:**
     - Incident location
     - Selected hospitals highlighted
     - Ambulance routes drawn
     - Real-time traffic overlay
   - **AI Confidence Scores:**
     - Overall plan confidence: 87%
     - Hospital matching: 92%
     - Ambulance selection: 85%
     - ETA accuracy: 89%
   - **Alternative Options:**
     - Alternative hospital choices (click to view rationale)
     - Alternative ambulance assignments
4. Coordinator reviews each component
5. Coordinator examines AI reasoning and confidence scores
6. Coordinator evaluates against domain expertise
7. Coordinator decides: Approve, Modify, or Reject

**Alternative Flows:**
- **A1: View Agent Execution Details**
  - 4a. Coordinator clicks "View Agent Details"
  - 4b. System displays agent execution log:
    - Each agent's input/output
    - Processing time
    - Decision rationale
    - Data sources used
  - 4c. Continue from step 5

- **A2: View Alternative Options**
  - 5a. Coordinator clicks "Alternatives" for hospital
  - 5b. System displays next 3 ranked hospitals with scores
  - 5c. Coordinator compares alternatives
  - 5d. Continue from step 6

- **A3: Simulate Plan Changes**
  - 6a. Coordinator clicks "What If" mode
  - 6b. Coordinator changes one parameter (e.g., different hospital)
  - 6c. System re-runs affected agents
  - 6d. System shows impact on overall plan
  - 6e. Continue from step 7

**Exception Flows:**
- **E1: Low Confidence Plan**
  - 3a. System detects overall confidence <70%
  - 3b. System displays warning banner: "Low confidence plan. Review carefully."
  - 3c. System highlights components with low confidence in yellow
  - 3d. Continue from step 4

- **E2: Resource Unavailable**
  - 3a. Hospital/ambulance becomes unavailable after plan generation
  - 3b. System displays alert: "Resource unavailable. Plan outdated."
  - 3c. System offers to regenerate plan
  - 3d. If coordinator accepts, system re-runs agents
  - 3e. Continue from step 3

- **E3: Plan Expired**
  - 2a. >5 minutes elapsed since plan generation
  - 2b. System displays warning: "Plan may be outdated. Refresh recommended."
  - 2c. System offers refresh option
  - 2d. Continue from step 3

**Postconditions:**
- Coordinator has reviewed plan
- Decision recorded (approve/modify/reject)
- Audit log entry created with review time
- If approved: Proceed to UC-10 (Approve Response Plan)
- If modified: Proceed to UC-11 (Modify Response Plan)
- If rejected: Proceed to UC-12 (Reject Response Plan)

**Business Rules:**
- BR-05: Coordinator must review plan within 10 minutes
- BR-06: Confidence scores must be clearly displayed
- BR-07: All AI decisions must have explainable rationale
- BR-08: Alternative options must be available for top 3 resources

**Non-Functional Requirements:**
- NFR-04: Plan visualization must load within 1 second
- NFR-05: Map must render within 2 seconds
- NFR-06: Real-time traffic overlay must update every 30 seconds
- NFR-07: Interface must be usable on tablets (responsive design)

---

### UC-10: Approve Response Plan

**ID:** UC-10  
**Actor:** Emergency Coordinator  
**Priority:** P0 (Must Have)  
**Frequency:** High (90%+ of plans)

**Description:**  
Coordinator approves AI-generated response plan, triggering automatic dispatch to all involved resources.

**Preconditions:**
- Coordinator has reviewed plan (UC-09 completed)
- Plan status is "Pending Approval"
- All allocated resources are still available
- Coordinator has "Approve Plan" permission

**Basic Flow:**
1. Coordinator clicks "Approve Plan" button
2. System displays confirmation dialog:
   - Plan summary
   - Resources to be notified
   - Confirmation question: "Dispatch this response plan?"
3. Coordinator clicks "Confirm Dispatch"
4. System changes incident status to "Dispatched"
5. System activates Communication Agent
6. Communication Agent sends notifications in parallel:
   - **Ambulances:** SMS with dispatch order, patient details, route link
   - **Hospitals:** Email + SMS with incoming patient details, ETA, preparation checklist
   - **Blood Banks:** Email with blood request details, quantity, pickup arrangement
7. System updates dashboard with "Dispatched" status
8. System starts real-time tracking:
   - Ambulance GPS tracking
   - Hospital preparation status
   - Blood bank fulfillment status
9. System displays success message: "Plan dispatched. Tracking active."
10. Monitoring Agent begins execution monitoring

**Alternative Flows:**
- **A1: Add Custom Instructions**
  - 3a. Coordinator clicks "Add Instructions" before confirming
  - 3b. Coordinator enters additional instructions (e.g., "Be cautious: hazardous materials present")
  - 3c. System appends instructions to all notifications
  - 3d. Continue from step 4

- **A2: Schedule Delayed Dispatch**
  - 1a. Coordinator clicks "Schedule Dispatch"
  - 1b. Coordinator sets dispatch time (e.g., +5 minutes)
  - 1c. System schedules dispatch for specified time
  - 1d. System confirms: "Plan scheduled for dispatch at [time]"
  - 1e. When time arrives, continue from step 4

**Exception Flows:**
- **E1: Resource Became Unavailable**
  - 4a. System detects ambulance/hospital just became unavailable
  - 4b. System cancels approval
  - 4c. System displays alert: "Resource unavailable. Plan needs regeneration."
  - 4d. System offers to regenerate plan
  - 4e. Return to UC-09

- **E2: Communication Failure**
  - 6a. SMS/Email service fails to send notification
  - 6b. System logs failure
  - 6c. System retries 3 times (exponential backoff)
  - 6d. If still failing, system marks notification as "Failed"
  - 6e. System alerts coordinator: "Some notifications failed. Verify manually."
  - 6f. Continue from step 7 (dispatch still successful, manual follow-up needed)

- **E3: System Overload**
  - 5a. System detects CPU >95% or memory >90%
  - 5b. System queues dispatch
  - 5c. System displays: "System busy. Dispatch queued."
  - 5d. System processes when resources available
  - 5e. Continue from step 6

**Postconditions:**
- Plan status changed to "Dispatched"
- All notifications sent successfully (or failures logged)
- Real-time tracking activated
- Audit log entry: "Plan approved by [Coordinator] at [timestamp]"
- Dashboard updated with dispatched status
- Monitoring Agent actively tracking execution

**Business Rules:**
- BR-09: Approval must complete within 30 seconds
- BR-10: All notifications sent within 10 seconds of approval
- BR-11: Failed notifications must be retried automatically
- BR-12: Coordinator must be notified of any notification failures
- BR-13: Plan cannot be approved if critical resource unavailable

**Non-Functional Requirements:**
- NFR-08: Approval action must respond within 500ms
- NFR-09: Notification sending must be asynchronous (non-blocking)
- NFR-10: System must handle 100 simultaneous dispatches
- NFR-11: All notifications must include incident ID for tracking

---

### UC-15: Monitor Incident Execution (Real-Time)

**ID:** UC-15  
**Actor:** Emergency Coordinator  
**Priority:** P0 (Must Have)  
**Frequency:** Continuous (for all active incidents)

**Description:**  
Coordinator monitors real-time execution of dispatched response plan, tracking ambulances, hospital preparation, and incident resolution.

**Preconditions:**
- Incident status is "Dispatched"
- Real-time tracking is active
- WebSocket connection established
- Coordinator has "Monitor Incidents" permission

**Basic Flow:**
1. Coordinator opens incident monitoring dashboard
2. System displays real-time map with:
   - Incident location (red marker)
   - Dispatched ambulances (blue vehicle icons with IDs)
   - Destination hospitals (green hospital icons with names)
   - Planned routes (dashed lines)
3. System displays incident timeline:
   - ✅ Incident reported: [timestamp]
   - ✅ Plan generated: [timestamp]
   - ✅ Plan dispatched: [timestamp]
   - 🔄 Ambulance A47 en route: ETA 8 min
   - 🔄 Ambulance B23 on scene: loading patient
   - 🔄 Hospital E preparing: trauma team ready, awaiting CT scanner
   - ⏳ Blood Bank M: preparing AB- units
4. System updates in real-time via WebSocket:
   - Ambulance GPS positions refresh every 10 seconds
   - Status changes appear instantly
   - ETA recalculated based on current speed and traffic
5. System displays status indicators:
   - 🟢 On Schedule (within 5% of ETA)
   - 🟡 Minor Delay (5-15% over ETA)
   - 🔴 Major Delay (>15% over ETA) - triggers alert
6. Coordinator monitors without intervention (if all on track)

**Alternative Flows:**
- **A1: Drill Down into Resource**
  - 2a. Coordinator clicks ambulance icon
  - 2b. System displays detailed ambulance status:
    - Current location (address)
    - Speed & heading
    - Distance remaining
    - Crew members
    - Equipment available
    - Patient details (if loaded)
  - 2c. Continue monitoring

- **A2: View Hospital Preparation**
  - 2a. Coordinator clicks hospital icon
  - 2b. System displays hospital preparation checklist:
    - ✅ Trauma team notified: [timestamp]
    - ✅ Bed prepared: Trauma Bay 3
    - ✅ CT scanner reserved: [timestamp]
    - ✅ Blood received from bank: [timestamp]
    - ⏳ Specialist en route: ETA 5 min
  - 2c. Continue monitoring

- **A3: Communicate with Field Resource**
  - 5a. Coordinator identifies need to communicate
  - 5b. Coordinator clicks "Send Message" on ambulance
  - 5c. Coordinator types message: "Road blocked at Highway 12. Take alternate route."
  - 5d. System sends SMS to ambulance crew
  - 5e. System logs communication in timeline
  - 5f. Continue monitoring

**Exception Flows:**
- **E1: Major Delay Detected**
  - 4a. System detects ambulance >15% over ETA
  - 4b. System triggers alert: "Ambulance A47 delayed. Current ETA: 18 min (was 12 min)"
  - 4c. System highlights ambulance icon in red
  - 4d. System displays reason (if available): "Heavy traffic on route"
  - 4e. Coordinator reviews situation
  - 4f. Options:
    - Accept delay (do nothing)
    - Dispatch backup ambulance
    - Reroute to different hospital
  - 4g. Continue monitoring

- **E2: Resource Becomes Unavailable**
  - 4a. Ambulance reports mechanical issue
  - 4b. System receives status update: "Vehicle Disabled"
  - 4c. System triggers critical alert: "Ambulance A47 disabled. Backup needed."
  - 4d. System automatically recommends nearest available ambulance
  - 4e. Coordinator reviews recommendation
  - 4f. Coordinator approves backup dispatch
  - 4g. System updates plan and notifies backup ambulance
  - 4h. Continue monitoring

- **E3: Hospital Capacity Changed**
  - 4a. Hospital reports trauma bay occupied by another emergency
  - 4b. System receives capacity update
  - 4c. System triggers alert: "Hospital E capacity changed. Reroute needed."
  - 4d. System automatically recommends alternative hospital
  - 4e. Coordinator reviews (time-critical decision)
  - 4f. Coordinator approves reroute
  - 4g. System updates ambulance destination
  - 4h. System notifies ambulance crew and new hospital
  - 4i. Continue monitoring

- **E4: WebSocket Connection Lost**
  - 4a. System detects WebSocket disconnect
  - 4b. System displays banner: "Real-time connection lost. Reconnecting..."
  - 4c. System attempts reconnection (5 retries, exponential backoff)
  - 4d. If successful: Resume real-time updates
  - 4e. If failed: System falls back to 30-second polling
  - 4f. Continue monitoring (degraded mode)

**Postconditions:**
- Coordinator has up-to-date view of incident execution
- All status changes logged in timeline
- Any alerts or interventions recorded in audit log
- Dashboard reflects current real-time status

**Business Rules:**
- BR-14: GPS positions must update ≤30 seconds
- BR-15: Status changes must appear within 2 seconds
- BR-16: Delays >15% must trigger alerts
- BR-17: Critical events (resource unavailable) must trigger immediate alerts
- BR-18: All communications must be logged

**Non-Functional Requirements:**
- NFR-12: WebSocket latency <500ms
- NFR-13: Map rendering must handle 100+ icons smoothly
- NFR-14: Status updates must not overwhelm UI (max 1 update/sec per resource)
- NFR-15: Dashboard must work on tablets (responsive)
- NFR-16: System must handle 100 concurrent WebSocket connections

---

### UC-21: Update Hospital Availability

**ID:** UC-21  
**Actor:** Hospital Admin  
**Priority:** P0 (Must Have)  
**Frequency:** High (multiple times per hour)

**Description:**  
Hospital administrator updates real-time availability information (beds, specialists, equipment) to ensure AI makes accurate recommendations.

**Preconditions:**
- Hospital admin is authenticated
- Admin has "Update Availability" permission
- Admin's hospital is registered in system

**Basic Flow:**
1. Hospital admin logs into hospital portal
2. System displays current availability dashboard:
   - **Bed Capacity:**
     - Total beds: 120
     - Available beds: 18
     - By type: ER (5), ICU (2), General (11)
   - **Specialists On Duty:**
     - Cardiologist: ✅ Available
     - Neurosurgeon: ❌ Not Available
     - Orthopedic Surgeon: ✅ Available (in surgery, available in 45 min)
     - Trauma Surgeon: ✅ Available
   - **Equipment Status:**
     - CT Scanner: ✅ Available
     - MRI: ❌ Occupied (available in 2 hours)
     - X-Ray: ✅ Available
     - Operating Rooms: 2 available of 6
3. Admin clicks "Update Availability"
4. Admin modifies data:
   - Changes ICU beds from 2 to 1 (patient just admitted)
   - Changes Neurosurgeon to "Available" (surgeon just arrived)
   - Changes MRI to "Available in 30 min" (scan finishing early)
5. Admin clicks "Save Changes"
6. System validates data (capacity within limits)
7. System updates database immediately
8. System broadcasts availability update via Redis pub/sub
9. System confirms: "Availability updated. AI will use new data immediately."
10. AI agents automatically use updated data in next incident processing

**Alternative Flows:**
- **A1: Bulk Status Update**
  - 4a. Admin clicks "Quick Update: All Busy"
  - 4b. System sets all bed types to "Fully Occupied"
  - 4c. System displays confirmation dialog
  - 4d. Admin confirms
  - 4e. Continue from step 7

- **A2: Scheduled Availability**
  - 4a. Admin clicks "Schedule Future Availability"
  - 4b. Admin sets: "MRI available in 30 minutes"
  - 4c. System schedules automatic update
  - 4d. System confirms: "Scheduled update for [time]"
  - 4e. Continue from step 5

- **A3: Emergency Closure**
  - 1a. Admin clicks "Emergency: Close Hospital"
  - 1b. System displays warning: "This will stop all incoming patients. Confirm?"
  - 1c. Admin confirms and provides reason: "Power outage"
  - 1d. System sets all availability to zero
  - 1e. System notifies all active coordinators
  - 1f. System flags hospital as "Unavailable - Emergency" in AI agents

**Exception Flows:**
- **E1: Invalid Capacity Values**
  - 6a. System detects available beds > total beds
  - 6b. System displays error: "Available beds cannot exceed total capacity."
  - 6c. Return to step 4

- **E2: Network Failure During Save**
  - 7a. Network request fails
  - 7b. System displays error: "Update failed. Retrying..."
  - 7c. System retries automatically (3 attempts)
  - 7d. If successful: Continue from step 8
  - 7e. If failed: System caches update locally, syncs when connection restored

- **E3: Conflicting Update**
  - 7a. Another admin updated availability simultaneously
  - 7b. System detects conflict
  - 7c. System displays: "Data changed by another user. Reload?"
  - 7d. Admin clicks "Reload"
  - 7e. System refreshes with latest data
  - 7f. Return to step 3

**Postconditions:**
- Hospital availability updated in database
- AI agents immediately use new data
- All active coordinators see updated availability in real-time
- Audit log entry: "Availability updated by [Admin] at [timestamp]"
- Any active incidents being processed use updated availability

**Business Rules:**
- BR-19: Availability must update within 2 seconds
- BR-20: Updates must broadcast to all coordinators in real-time
- BR-21: Historical availability must be logged for analytics
- BR-22: Emergency closures must trigger immediate notifications

**Non-Functional Requirements:**
- NFR-17: Update latency <2 seconds (save to broadcast)
- NFR-18: System must support 1000+ hospital simultaneous updates
- NFR-19: Mobile-responsive for tablet use in hospital
- NFR-20: Offline-first: cache updates if network unavailable

---

### UC-27: Receive Dispatch Order

**ID:** UC-27  
**Actor:** Ambulance Crew  
**Priority:** P0 (Must Have)  
**Frequency:** High (per dispatch)

**Description:**  
Ambulance crew receives digital dispatch order with incident details, patient information, destination hospital, and optimized route.

**Preconditions:**
- Ambulance crew has mobile device with app installed
- Crew is authenticated
- Ambulance status is "Available"
- Incident plan has been dispatched by coordinator

**Basic Flow:**
1. System dispatches plan (triggered by UC-10)
2. Communication Agent identifies assigned ambulance (e.g., A47)
3. System sends push notification to ambulance crew's mobile device
4. Crew taps notification
5. App opens dispatch order screen:
   - **Incident Summary:**
     - Incident ID: INC-20260822-0147
     - Type: Multi-vehicle accident
     - Severity: Critical
     - Location: Highway 101, Mile 42
     - GPS coordinates: 37.7749° N, 122.4194° W
   - **Assignment:**
     - Assigned ambulance: A47
     - Assigned patient: Patient #1 (Critical - Head trauma, internal bleeding)
     - Destination: Memorial Hospital, 2.5 km
   - **Route:**
     - Interactive map with turn-by-turn directions
     - Estimated time: 6 minutes to scene, 12 minutes to hospital
     - Traffic: Moderate (alternate route suggested)
   - **Hospital Preparation:**
     - Trauma team ready
     - CT scanner reserved
     - Blood: AB- (12 units available)
   - **Action Buttons:**
     - [Start Navigation] — Opens map with GPS navigation
     - [Confirm Receipt] — Acknowledges dispatch
     - [Report Issue] — Report delay or problem
6. Crew member clicks "Confirm Receipt"
7. System updates ambulance status to "Dispatched"
8. System logs acknowledgment with timestamp
9. Coordinator dashboard shows ambulance status change
10. Crew clicks "Start Navigation"
11. App launches turn-by-turn GPS navigation

**Alternative Flows:**
- **A1: Multiple Patients Assigned**
  - 5a. Dispatch order shows multiple patients (e.g., 2 patients)
  - 5b. App displays patient priorities: Patient #1 (Critical), Patient #3 (Serious)
  - 5c. App shows transport sequence: Scene → Hospital E (Patient #1) → Return to scene → Hospital F (Patient #3)
  - 5d. Continue from step 6

- **A2: Special Instructions**
  - 5a. Dispatch includes coordinator's custom instructions: "Hazmat present. Decontamination required."
  - 5b. App highlights special instructions in yellow banner
  - 5c. Crew reviews instructions
  - 5d. Continue from step 6

- **A3: Equipment Requirements**
  - 5a. Dispatch specifies required equipment: "Bring backboard, cervical collar"
  - 5b. App displays equipment checklist
  - 5c. Crew checks off items as loaded
  - 5d. Continue from step 6

**Exception Flows:**
- **E1: Crew Not Available**
  - 3a. Crew member marks status "On Break" or "Off Duty"
  - 3b. System does not dispatch to this ambulance
  - 3c. System selects next best available ambulance
  - 3d. Alternative crew receives dispatch

- **E2: Notification Not Received**
  - 3a. Push notification fails (device offline, app closed)
  - 3b. System falls back to SMS: "DISPATCH: Incident INC-20260822-0147. Open app immediately."
  - 3c. Crew receives SMS
  - 3d. Crew opens app manually
  - 3e. Continue from step 5

- **E3: Crew Rejects Dispatch**
  - 6a. Crew clicks "Report Issue" instead of "Confirm Receipt"
  - 6b. App displays issue options: "Ambulance Mechanical Issue", "Crew Medical Emergency", "Wrong Assignment", "Other"
  - 6c. Crew selects issue
  - 6d. App prompts for details
  - 6e. System notifies coordinator immediately
  - 6f. System marks ambulance as "Unavailable"
  - 6g. Coordinator dispatches backup ambulance (UC-15 Exception E2)

- **E4: GPS Navigation Unavailable**
  - 10a. Device has no GPS signal or maps unavailable
  - 10b. App displays fallback: written turn-by-turn directions
  - 10c. App shows address for manual navigation
  - 10d. Crew navigates manually

**Postconditions:**
- Crew has received and reviewed dispatch order
- Ambulance status updated to "Dispatched" or "En Route"
- Coordinator aware of dispatch acknowledgment
- GPS navigation active (if available)
- Audit log: "Dispatch received by Crew [ID] at [timestamp]"

**Business Rules:**
- BR-23: Dispatch must reach crew within 10 seconds
- BR-24: Crew must acknowledge within 2 minutes (or auto-escalate)
- BR-25: Dispatch must include all critical information (incident, route, hospital)
- BR-26: System must fallback to SMS if push fails

**Non-Functional Requirements:**
- NFR-21: Push notification latency <5 seconds
- NFR-22: App must work offline (cache dispatch data)
- NFR-23: Map and navigation must load within 3 seconds
- NFR-24: App must support Android and iOS
- NFR-25: UI must be usable with gloves (large touch targets)

---

## 4. Use Case Relationships

### Include Relationships

- UC-01, UC-02, UC-03, UC-04 **include** → UC-06 (View Incident Status)
  - After submitting incident, dispatcher always views status

- UC-10 (Approve Plan) **includes** → UC-15 (Monitor Execution)
  - Approving plan automatically starts monitoring

- UC-11 (Modify Plan) **includes** → UC-09 (Review Plan)
  - Modifying requires reviewing current plan first

- UC-27 (Receive Dispatch) **includes** → UC-30 (Update Status)
  - Receiving dispatch triggers status update

### Extend Relationships

- UC-09 (Review Plan) **extends** → UC-17 (Escalate Incident)
  - If plan is complex/concerning, coordinator may escalate

- UC-15 (Monitor Execution) **extends** → UC-16 (Communicate with Field)
  - During monitoring, coordinator may need to communicate

- UC-21 (Update Availability) **extends** → UC-24 (View Incoming Pipeline)
  - After updating, admin often checks incoming patients

- UC-32 (Report Issues) **extends** → UC-15 (Monitor Execution)
  - Field issues trigger coordinator monitoring

### Generalization Relationships

- UC-01, UC-02, UC-03, UC-04 are **specializations of** → Generic "Submit Incident"
  - All are variations of incident submission with different input types

- UC-10, UC-11, UC-12 are **specializations of** → Generic "Handle Plan Decision"
  - All are coordinator responses to AI-generated plan

---

## 5. Use Case Priority Matrix

| Priority | Use Cases | Justification |
|----------|-----------|---------------|
| **P0 (Must Have)** | UC-01, UC-02, UC-03, UC-04, UC-07, UC-08, UC-09, UC-10, UC-11, UC-15, UC-21, UC-27, UC-30 | Core incident workflow: submit → review → approve → monitor. Critical path. |
| **P1 (Should Have)** | UC-05, UC-06, UC-12, UC-13, UC-14, UC-16, UC-17, UC-18, UC-22, UC-23, UC-24, UC-28, UC-29, UC-32, UC-34, UC-35, UC-36 | Important features enhancing usability and flexibility. |
| **P2 (Nice to Have)** | UC-19, UC-20, UC-25, UC-26, UC-31, UC-33, UC-37, UC-38, UC-39, UC-40, UC-41, UC-42, UC-43, UC-44 | Analytics, reporting, admin features. Can be delivered post-MVP. |

---

## 6. Use Case Traceability Matrix

| Use Case | Functional Requirements | Non-Functional Requirements | Test Scenarios |
|----------|------------------------|----------------------------|----------------|
| UC-01 | FR-001, FR-002, FR-003 | NFR-01, NFR-02, NFR-03 | TS-001, TS-002 |
| UC-09 | FR-015, FR-016, FR-017 | NFR-04, NFR-05, NFR-06, NFR-07 | TS-009, TS-010 |
| UC-10 | FR-018, FR-019, FR-020 | NFR-08, NFR-09, NFR-10, NFR-11 | TS-011, TS-012 |
| UC-15 | FR-025, FR-026, FR-027 | NFR-12, NFR-13, NFR-14, NFR-15, NFR-16 | TS-015, TS-016 |
| UC-21 | FR-035, FR-036, FR-037 | NFR-17, NFR-18, NFR-19, NFR-20 | TS-021, TS-022 |
| UC-27 | FR-045, FR-046, FR-047 | NFR-21, NFR-22, NFR-23, NFR-24, NFR-25 | TS-027, TS-028 |

*(Full traceability matrix to be expanded in detailed requirements document)*

---

## 7. Use Case Narrative (Top 5 Critical)

### Narrative 1: Complete Incident Workflow

**Actors:** Dispatcher, Emergency Coordinator, Ambulance Crew, Hospital Admin

**Scenario:** Multi-vehicle accident with 3 victims

1. **Dispatcher submits incident** (UC-01):
   - Receives 911 call at 2:47 PM
   - Opens ARIA dashboard
   - Enters: "Multi-vehicle accident, Highway 101 Mile 42, 3 victims, injuries unknown"
   - Uploads scene photo from first responder
   - Submits incident

2. **AI processes incident** (System):
   - Triage Agent analyzes text + image → "2 critical, 1 serious"
   - Hospital Agent queries 28 hospitals → ranks top 3
   - Ambulance Agent queries 47 ambulances → selects 2 optimal
   - Route Agent calculates traffic-adjusted routes
   - Plan Agent synthesizes comprehensive response plan
   - Processing time: 8 seconds

3. **Coordinator reviews plan** (UC-09):
   - Receives notification: "Plan ready for INC-20260822-0147"
   - Opens plan, sees:
     - 2 ambulances assigned
     - Hospital A for critical patients (trauma team + AB- blood ready)
     - Hospital B for serious patient
   - Reviews AI confidence scores: 89% overall
   - Evaluates: "Looks good, approve"

4. **Coordinator approves** (UC-10):
   - Clicks "Approve Plan"
   - Confirms dispatch
   - System sends notifications to ambulances, hospitals

5. **Ambulance receives dispatch** (UC-27):
   - Crew receives push notification
   - Opens dispatch: Patient #1 critical, head trauma, destination Hospital A
   - Confirms receipt
   - Starts GPS navigation

6. **Hospital prepares** (UC-21 already updated):
   - Hospital A received notification
   - Trauma team assembling
   - Blood units brought to trauma bay
   - CT scanner reserved

7. **Coordinator monitors** (UC-15):
   - Dashboard shows ambulance A47 en route, ETA 10 min
   - Hospital A "Preparing - Ready in 5 min"
   - All on schedule (green indicators)

8. **Incident resolution:**
   - Ambulance arrives at hospital: 2:59 PM (12 minutes total)
   - Patient transferred to trauma team immediately
   - Treatment begins within 1 minute of arrival
   - **Total time from call to treatment: 13 minutes** (vs. 25-30 minutes manual)

---

**Document Control:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-08-22 | Business Analyst | Initial draft |

---

**End of Use Case Documentation**
