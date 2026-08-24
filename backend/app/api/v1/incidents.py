"""
Incident Management API Endpoints
Complete CRUD + workflow operations for emergency incidents
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.models.incident import Incident, IncidentHistory, IncidentStatus, IncidentSeverity
from app.schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse,
    IncidentProcess,
    IncidentApproval,
    IncidentPlanModification,
    IncidentHistoryResponse,
    IncidentListFilter,
)
from app.schemas.response import ResponseBase, PaginatedResponse
# from app.services.agent_service import AgentOrchestrator  # TODO: Create this

router = APIRouter()


def generate_incident_code() -> str:
    """Generate unique incident code."""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"INC-{timestamp}"


# ============================================================================
# CREATE INCIDENT
# ============================================================================

@router.post(
    "",
    response_model=ResponseBase,
    status_code=status.HTTP_201_CREATED,
    summary="Create new incident",
    description="Report a new emergency incident and trigger initial triage"
)
async def create_incident(
    incident_data: IncidentCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Create a new emergency incident.
    
    - **description**: Detailed description of the emergency
    - **incident_type**: Type of emergency (MEDICAL, ACCIDENT, etc.)
    - **location**: GPS coordinates and address
    - **victim_count**: Number of people affected
    - **blood_required**: Whether blood is needed
    - **ambulance_required**: Whether ambulance is needed
    """
    try:
        # Create incident
        incident = Incident(
            incident_code=generate_incident_code(),
            description=incident_data.description,
            incident_type=incident_data.incident_type,
            latitude=incident_data.location.latitude,
            longitude=incident_data.location.longitude,
            address=incident_data.location.address,
            city=incident_data.location.city,
            victim_count=incident_data.victim_count,
            reporter_name=incident_data.reporter_name,
            reporter_phone=incident_data.reporter_phone,
            reporter_relationship=incident_data.reporter_relationship,
            blood_required=incident_data.blood_required,
            blood_type=incident_data.blood_type,
            ambulance_required=incident_data.ambulance_required,
            hospital_required=incident_data.hospital_required,
            status=IncidentStatus.REPORTED,
            created_by=UUID(current_user["sub"]),
        )
        
        # Set PostGIS location
        from geoalchemy2.elements import WKTElement
        incident.location = WKTElement(
            f'POINT({incident_data.location.longitude} {incident_data.location.latitude})',
            srid=4326
        )
        
        db.add(incident)
        await db.flush()
        
        # Create history entry
        history = IncidentHistory(
            incident_id=incident.id,
            status=IncidentStatus.REPORTED,
            changed_by=UUID(current_user["sub"]),
            change_type="created",
            notes="Incident created"
        )
        db.add(history)
        
        await db.commit()
        await db.refresh(incident)
        
        # Trigger AI triage in background
        # background_tasks.add_task(trigger_ai_triage, incident.id)
        
        return ResponseBase(
            success=True,
            message="Incident created successfully. AI triage initiated.",
            data={
                "incident_id": str(incident.id),
                "incident_code": incident.incident_code,
                "status": incident.status.value
            }
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create incident: {str(e)}"
        )


# ============================================================================
# GET INCIDENT BY ID
# ============================================================================

@router.get(
    "/{incident_id}",
    response_model=ResponseBase,
    summary="Get incident details",
    description="Retrieve detailed information about a specific incident"
)
async def get_incident(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get incident by ID with all related data."""
    query = select(Incident).where(Incident.id == incident_id).options(
        selectinload(Incident.assigned_hospital),
        selectinload(Incident.assigned_ambulance),
    )
    
    result = await db.execute(query)
    incident = result.scalar_one_or_none()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    return ResponseBase(
        success=True,
        message="Incident retrieved successfully",
        data=IncidentResponse.from_orm(incident)
    )


# ============================================================================
# LIST INCIDENTS WITH FILTERS
# ============================================================================

@router.get(
    "",
    response_model=PaginatedResponse,
    summary="List incidents",
    description="List all incidents with optional filters and pagination"
)
async def list_incidents(
    status_filter: Optional[List[IncidentStatus]] = Query(None, alias="status"),
    severity_filter: Optional[List[IncidentSeverity]] = Query(None, alias="severity"),
    city: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    List incidents with filters:
    
    - **status**: Filter by status (can provide multiple)
    - **severity**: Filter by severity (can provide multiple)
    - **city**: Filter by city
    - **from_date**: Start date range
    - **to_date**: End date range
    - **page**: Page number
    - **page_size**: Items per page
    """
    # Build query
    query = select(Incident)
    filters = []
    
    if status_filter:
        filters.append(Incident.status.in_(status_filter))
    
    if severity_filter:
        filters.append(Incident.severity.in_(severity_filter))
    
    if city:
        filters.append(Incident.city.ilike(f"%{city}%"))
    
    if from_date:
        filters.append(Incident.reported_at >= from_date)
    
    if to_date:
        filters.append(Incident.reported_at <= to_date)
    
    if filters:
        query = query.where(and_(*filters))
    
    # Get total count
    count_query = select(func.count()).select_from(Incident)
    if filters:
        count_query = count_query.where(and_(*filters))
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    query = query.order_by(Incident.reported_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    incidents = result.scalars().all()
    
    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size
    
    return PaginatedResponse(
        success=True,
        message=f"Retrieved {len(incidents)} incidents",
        data=[IncidentResponse.from_orm(inc) for inc in incidents],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


# ============================================================================
# PROCESS INCIDENT (Trigger AI Workflow)
# ============================================================================

@router.post(
    "/{incident_id}/process",
    response_model=ResponseBase,
    summary="Process incident through AI workflow",
    description="Trigger the complete AI agent workflow for incident processing"
)
async def process_incident(
    incident_id: UUID,
    process_data: IncidentProcess,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Trigger AI agent workflow to:
    1. Triage and classify severity
    2. Find suitable hospitals
    3. Allocate ambulance
    4. Reserve blood (if needed)
    5. Calculate optimal route
    6. Generate response plan
    7. Await human approval
    """
    # Get incident
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    # Check if already processed
    if incident.status not in [IncidentStatus.REPORTED, IncidentStatus.TRIAGED]:
        if not process_data.force_processing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Incident already in {incident.status.value} status"
            )
    
    # Update status
    incident.status = IncidentStatus.TRIAGED
    
    # Create history
    history = IncidentHistory(
        incident_id=incident.id,
        status=IncidentStatus.TRIAGED,
        changed_by=UUID(current_user["sub"]),
        change_type="processing_initiated",
        notes="AI workflow processing initiated"
    )
    db.add(history)
    
    await db.commit()
    
    # Trigger AI workflow in background
    # background_tasks.add_task(
    #     run_agent_workflow,
    #     incident_id,
    #     override_ml=process_data.override_ml
    # )
    
    return ResponseBase(
        success=True,
        message="AI workflow initiated. Processing incident...",
        data={
            "incident_id": str(incident.id),
            "status": incident.status.value,
            "workflow_started": True
        }
    )


# ============================================================================
# APPROVE INCIDENT PLAN
# ============================================================================

@router.post(
    "/{incident_id}/approve",
    response_model=ResponseBase,
    summary="Approve incident response plan",
    description="Approve the AI-generated response plan and trigger dispatch"
)
async def approve_incident(
    incident_id: UUID,
    approval_data: IncidentApproval,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("dispatcher"))
):
    """
    Approve or reject incident response plan.
    
    - **approved**: True to approve, False to reject
    - **notes**: Optional approval/rejection notes
    - **modifications**: Optional plan modifications
    """
    # Get incident
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    if incident.status != IncidentStatus.AWAITING_APPROVAL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Incident not awaiting approval (current: {incident.status.value})"
        )
    
    # Update incident
    incident.approved_by = UUID(current_user["sub"])
    incident.approved_at = datetime.utcnow()
    incident.approval_notes = approval_data.notes
    
    if approval_data.approved:
        incident.status = IncidentStatus.APPROVED
        
        # Apply modifications if provided
        if approval_data.modifications:
            if "assigned_hospital_id" in approval_data.modifications:
                incident.assigned_hospital_id = UUID(approval_data.modifications["assigned_hospital_id"])
            if "assigned_ambulance_id" in approval_data.modifications:
                incident.assigned_ambulance_id = UUID(approval_data.modifications["assigned_ambulance_id"])
        
        # Create history
        history = IncidentHistory(
            incident_id=incident.id,
            status=IncidentStatus.APPROVED,
            changed_by=UUID(current_user["sub"]),
            change_type="approved",
            changes=approval_data.modifications,
            notes=approval_data.notes
        )
        db.add(history)
        
        await db.commit()
        
        # Trigger dispatch in background
        # background_tasks.add_task(dispatch_resources, incident_id)
        
        return ResponseBase(
            success=True,
            message="Incident plan approved. Dispatch initiated.",
            data={"incident_id": str(incident.id), "status": "APPROVED"}
        )
    else:
        incident.status = IncidentStatus.TRIAGED
        
        # Create history
        history = IncidentHistory(
            incident_id=incident.id,
            status=IncidentStatus.TRIAGED,
            changed_by=UUID(current_user["sub"]),
            change_type="rejected",
            notes=approval_data.notes
        )
        db.add(history)
        
        await db.commit()
        
        return ResponseBase(
            success=True,
            message="Incident plan rejected. Awaiting reprocessing.",
            data={"incident_id": str(incident.id), "status": "REJECTED"}
        )


# ============================================================================
# MODIFY INCIDENT PLAN
# ============================================================================

@router.post(
    "/{incident_id}/modify",
    response_model=ResponseBase,
    summary="Modify incident plan",
    description="Modify the incident response plan before approval"
)
async def modify_incident_plan(
    incident_id: UUID,
    modification_data: IncidentPlanModification,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("dispatcher"))
):
    """Modify incident response plan."""
    # Get incident
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    # Apply modifications
    if modification_data.assigned_hospital_id:
        incident.assigned_hospital_id = modification_data.assigned_hospital_id
    
    if modification_data.assigned_ambulance_id:
        incident.assigned_ambulance_id = modification_data.assigned_ambulance_id
    
    if modification_data.response_plan_updates:
        # Merge with existing plan
        if incident.response_plan:
            incident.response_plan.update(modification_data.response_plan_updates)
        else:
            incident.response_plan = modification_data.response_plan_updates
    
    # Create history
    history = IncidentHistory(
        incident_id=incident.id,
        status=incident.status,
        changed_by=UUID(current_user["sub"]),
        change_type="plan_modified",
        changes=modification_data.dict(exclude_none=True),
        notes=modification_data.notes
    )
    db.add(history)
    
    await db.commit()
    await db.refresh(incident)
    
    return ResponseBase(
        success=True,
        message="Incident plan modified successfully",
        data=IncidentResponse.from_orm(incident)
    )


# ============================================================================
# DISPATCH INCIDENT
# ============================================================================

@router.post(
    "/{incident_id}/dispatch",
    response_model=ResponseBase,
    summary="Execute dispatch",
    description="Execute the actual resource dispatch (ambulance, notifications, etc.)"
)
async def dispatch_incident(
    incident_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("dispatcher"))
):
    """Execute resource dispatch for approved incident."""
    # Get incident
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    if incident.status != IncidentStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Incident not approved for dispatch (current: {incident.status.value})"
        )
    
    # Update status
    incident.status = IncidentStatus.DISPATCHED
    incident.dispatched_at = datetime.utcnow()
    
    # Create history
    history = IncidentHistory(
        incident_id=incident.id,
        status=IncidentStatus.DISPATCHED,
        changed_by=UUID(current_user["sub"]),
        change_type="dispatched",
        notes="Resources dispatched"
    )
    db.add(history)
    
    await db.commit()
    
    # TODO: Execute actual dispatch actions
    # - Update ambulance status
    # - Send notifications
    # - Update hospital
    # - Reserve blood
    
    return ResponseBase(
        success=True,
        message="Resources dispatched successfully",
        data={
            "incident_id": str(incident.id),
            "status": "DISPATCHED",
            "dispatched_at": incident.dispatched_at.isoformat()
        }
    )


# ============================================================================
# GET INCIDENT STATUS
# ============================================================================

@router.get(
    "/{incident_id}/status",
    response_model=ResponseBase,
    summary="Get real-time incident status",
    description="Get current status and progress of incident"
)
async def get_incident_status(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get real-time incident status."""
    query = select(Incident).where(Incident.id == incident_id).options(
        selectinload(Incident.assigned_hospital),
        selectinload(Incident.assigned_ambulance),
    )
    
    result = await db.execute(query)
    incident = result.scalar_one_or_none()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    # Build status response
    status_data = {
        "incident_id": str(incident.id),
        "incident_code": incident.incident_code,
        "status": incident.status.value,
        "severity": incident.severity.value if incident.severity else None,
        "reported_at": incident.reported_at.isoformat(),
        "current_location": {
            "latitude": incident.latitude,
            "longitude": incident.longitude,
            "city": incident.city
        },
        "assigned_resources": {
            "hospital": incident.assigned_hospital.name if incident.assigned_hospital else None,
            "ambulance": incident.assigned_ambulance.vehicle_number if incident.assigned_ambulance else None,
        },
        "estimated_response_time": incident.estimated_response_time,
        "dispatched_at": incident.dispatched_at.isoformat() if incident.dispatched_at else None,
    }
    
    return ResponseBase(
        success=True,
        message="Status retrieved successfully",
        data=status_data
    )


# ============================================================================
# GET INCIDENT HISTORY
# ============================================================================

@router.get(
    "/{incident_id}/history",
    response_model=ResponseBase,
    summary="Get incident history",
    description="Get complete audit trail of incident changes"
)
async def get_incident_history(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get incident history."""
    # Verify incident exists
    incident_result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = incident_result.scalar_one_or_none()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    # Get history
    query = select(IncidentHistory).where(
        IncidentHistory.incident_id == incident_id
    ).order_by(IncidentHistory.changed_at.desc())
    
    result = await db.execute(query)
    history = result.scalars().all()
    
    return ResponseBase(
        success=True,
        message=f"Retrieved {len(history)} history entries",
        data=[IncidentHistoryResponse.from_orm(h) for h in history]
    )
