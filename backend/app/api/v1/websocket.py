"""
WebSocket Real-Time Updates
Live updates for dashboard, ambulance tracking, agent status, incidents
"""
import json
import logging
from typing import Dict, Set, Optional, Any
from datetime import datetime
from uuid import UUID
import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from fastapi.websockets import WebSocketState

from app.core.security import decode_token

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# CONNECTION MANAGER
# ============================================================================

class ConnectionManager:
    """
    Manages WebSocket connections with authentication, broadcasting, and heartbeat.
    """
    
    def __init__(self):
        # Active connections: {user_id: {websocket, channels}}
        self.active_connections: Dict[str, Dict] = {}
        
        # Channel subscriptions: {channel: set of user_ids}
        self.channels: Dict[str, Set[str]] = {
            "dashboard": set(),
            "incidents": set(),
            "ambulances": set(),
            "agents": set(),
            "hospitals": set(),
        }
        
        # Heartbeat task
        self.heartbeat_task = None
        
        logger.info("WebSocket ConnectionManager initialized")
    
    async def connect(
        self,
        websocket: WebSocket,
        user_id: str,
        username: str,
        channels: Set[str]
    ):
        """Accept and register WebSocket connection."""
        await websocket.accept()
        
        # Store connection
        self.active_connections[user_id] = {
            "websocket": websocket,
            "username": username,
            "channels": channels,
            "connected_at": datetime.utcnow().isoformat(),
            "last_heartbeat": datetime.utcnow(),
        }
        
        # Subscribe to channels
        for channel in channels:
            if channel in self.channels:
                self.channels[channel].add(user_id)
        
        logger.info(f"✅ User {username} ({user_id}) connected to channels: {channels}")
        
        # Send welcome message
        await self.send_personal_message(
            user_id,
            {
                "type": "connection.established",
                "data": {
                    "message": "Connected to ARIA real-time updates",
                    "user_id": user_id,
                    "channels": list(channels),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            }
        )
        
        # Send current stats
        await self._send_initial_data(user_id, channels)
    
    def disconnect(self, user_id: str):
        """Remove WebSocket connection."""
        if user_id in self.active_connections:
            conn_data = self.active_connections[user_id]
            username = conn_data["username"]
            channels = conn_data["channels"]
            
            # Unsubscribe from channels
            for channel in channels:
                if channel in self.channels:
                    self.channels[channel].discard(user_id)
            
            # Remove connection
            del self.active_connections[user_id]
            
            logger.info(f"❌ User {username} ({user_id}) disconnected")
    
    async def send_personal_message(self, user_id: str, message: Dict):
        """Send message to specific user."""
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]["websocket"]
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to {user_id}: {e}")
                self.disconnect(user_id)
    
    async def broadcast_to_channel(self, channel: str, message: Dict):
        """Broadcast message to all users in a channel."""
        if channel not in self.channels:
            logger.warning(f"Invalid channel: {channel}")
            return
        
        # Add timestamp if not present
        if "timestamp" not in message.get("data", {}):
            message["data"]["timestamp"] = datetime.utcnow().isoformat()
        
        disconnected_users = []
        
        for user_id in self.channels[channel]:
            if user_id in self.active_connections:
                websocket = self.active_connections[user_id]["websocket"]
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to broadcast to {user_id}: {e}")
                    disconnected_users.append(user_id)
        
        # Clean up disconnected users
        for user_id in disconnected_users:
            self.disconnect(user_id)
        
        logger.debug(f"📡 Broadcasted to {channel}: {len(self.channels[channel])} users")
    
    async def broadcast_to_all(self, message: Dict):
        """Broadcast message to all connected users."""
        for channel in self.channels.keys():
            await self.broadcast_to_channel(channel, message)
    
    async def start_heartbeat(self, interval: int = 30):
        """Start heartbeat to keep connections alive."""
        while True:
            await asyncio.sleep(interval)
            
            heartbeat_message = {
                "type": "heartbeat",
                "data": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "active_connections": len(self.active_connections)
                }
            }
            
            disconnected_users = []
            
            for user_id, conn_data in self.active_connections.items():
                websocket = conn_data["websocket"]
                
                try:
                    await websocket.send_json(heartbeat_message)
                    conn_data["last_heartbeat"] = datetime.utcnow()
                except Exception:
                    disconnected_users.append(user_id)
            
            # Clean up disconnected users
            for user_id in disconnected_users:
                self.disconnect(user_id)
            
            if len(self.active_connections) > 0:
                logger.debug(f"💓 Heartbeat sent to {len(self.active_connections)} users")
    
    async def _send_initial_data(self, user_id: str, channels: Set[str]):
        """Send initial data when user connects."""
        # Send connection stats
        await self.send_personal_message(
            user_id,
            {
                "type": "stats.initial",
                "data": {
                    "active_connections": len(self.active_connections),
                    "channels": {
                        channel: len(users)
                        for channel, users in self.channels.items()
                        if channel in channels
                    }
                }
            }
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        return {
            "total_connections": len(self.active_connections),
            "channels": {
                channel: len(users)
                for channel, users in self.channels.items()
            },
            "connections": [
                {
                    "user_id": user_id,
                    "username": conn["username"],
                    "channels": list(conn["channels"]),
                    "connected_at": conn["connected_at"],
                }
                for user_id, conn in self.active_connections.items()
            ]
        }


# Global connection manager
manager = ConnectionManager()


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token"),
    channels: str = Query("dashboard,incidents", description="Comma-separated channel names")
):
    """
    WebSocket endpoint for real-time updates.
    
    **Authentication:** Pass JWT token as query parameter
    
    **Channels:**
    - dashboard: Overall statistics and status
    - incidents: Incident updates (created, updated, dispatched)
    - ambulances: Ambulance location and status
    - agents: AI agent execution status
    - hospitals: Hospital availability updates
    
    **Usage:**
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/api/v1/ws?token=YOUR_JWT&channels=dashboard,incidents');
    
    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        console.log(message.type, message.data);
    };
    ```
    
    **Message Types:**
    - connection.established
    - heartbeat
    - incident.created
    - incident.updated
    - incident.dispatched
    - ambulance.location_updated
    - ambulance.status_changed
    - agent.started
    - agent.completed
    - agent.failed
    - hospital.availability_changed
    - plan.generated
    - plan.approved
    """
    try:
        # Authenticate
        try:
            payload = decode_token(token)
            user_id = payload.get("sub")
            username = payload.get("username")
            
            if not user_id or not username:
                await websocket.close(code=1008, reason="Invalid token")
                return
                
        except Exception as e:
            logger.error(f"WebSocket authentication failed: {e}")
            await websocket.close(code=1008, reason="Authentication failed")
            return
        
        # Parse channels
        channel_list = {ch.strip() for ch in channels.split(",")}
        valid_channels = channel_list & set(manager.channels.keys())
        
        if not valid_channels:
            await websocket.close(code=1008, reason="No valid channels specified")
            return
        
        # Connect
        await manager.connect(websocket, user_id, username, valid_channels)
        
        try:
            # Listen for client messages
            while True:
                data = await websocket.receive_text()
                
                try:
                    message = json.loads(data)
                    message_type = message.get("type")
                    
                    # Handle client messages
                    if message_type == "ping":
                        await manager.send_personal_message(
                            user_id,
                            {"type": "pong", "data": {"timestamp": datetime.utcnow().isoformat()}}
                        )
                    
                    elif message_type == "subscribe":
                        # Subscribe to additional channels
                        new_channels = set(message.get("channels", []))
                        valid_new = new_channels & set(manager.channels.keys())
                        
                        for channel in valid_new:
                            manager.channels[channel].add(user_id)
                            manager.active_connections[user_id]["channels"].add(channel)
                        
                        await manager.send_personal_message(
                            user_id,
                            {
                                "type": "subscribed",
                                "data": {"channels": list(valid_new)}
                            }
                        )
                    
                    elif message_type == "unsubscribe":
                        # Unsubscribe from channels
                        remove_channels = set(message.get("channels", []))
                        
                        for channel in remove_channels:
                            if channel in manager.channels:
                                manager.channels[channel].discard(user_id)
                            if channel in manager.active_connections[user_id]["channels"]:
                                manager.active_connections[user_id]["channels"].remove(channel)
                        
                        await manager.send_personal_message(
                            user_id,
                            {
                                "type": "unsubscribed",
                                "data": {"channels": list(remove_channels)}
                            }
                        )
                    
                    else:
                        logger.warning(f"Unknown message type: {message_type}")
                
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON from user {user_id}")
                except Exception as e:
                    logger.error(f"Error handling message from {user_id}: {e}")
        
        except WebSocketDisconnect:
            manager.disconnect(user_id)
        
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close(code=1011, reason="Internal error")


# ============================================================================
# EVENT BROADCASTING FUNCTIONS
# ============================================================================

async def broadcast_incident_created(incident_data: Dict):
    """Broadcast when new incident is created."""
    await manager.broadcast_to_channel(
        "incidents",
        {
            "type": "incident.created",
            "data": incident_data
        }
    )


async def broadcast_incident_updated(incident_id: str, incident_data: Dict):
    """Broadcast when incident is updated."""
    await manager.broadcast_to_channel(
        "incidents",
        {
            "type": "incident.updated",
            "data": {
                "incident_id": incident_id,
                **incident_data
            }
        }
    )


async def broadcast_incident_dispatched(incident_id: str, dispatch_data: Dict):
    """Broadcast when incident is dispatched."""
    await manager.broadcast_to_channel(
        "incidents",
        {
            "type": "incident.dispatched",
            "data": {
                "incident_id": incident_id,
                **dispatch_data
            }
        }
    )


async def broadcast_ambulance_location(ambulance_id: str, location_data: Dict):
    """Broadcast ambulance location update."""
    await manager.broadcast_to_channel(
        "ambulances",
        {
            "type": "ambulance.location_updated",
            "data": {
                "ambulance_id": ambulance_id,
                **location_data
            }
        }
    )


async def broadcast_ambulance_status(ambulance_id: str, status_data: Dict):
    """Broadcast ambulance status change."""
    await manager.broadcast_to_channel(
        "ambulances",
        {
            "type": "ambulance.status_changed",
            "data": {
                "ambulance_id": ambulance_id,
                **status_data
            }
        }
    )


async def broadcast_agent_status(agent_name: str, status: str, details: Dict):
    """Broadcast AI agent execution status."""
    await manager.broadcast_to_channel(
        "agents",
        {
            "type": f"agent.{status}",
            "data": {
                "agent": agent_name,
                "status": status,
                **details
            }
        }
    )


async def broadcast_plan_generated(incident_id: str, plan_data: Dict):
    """Broadcast when response plan is generated."""
    await manager.broadcast_to_channel(
        "incidents",
        {
            "type": "plan.generated",
            "data": {
                "incident_id": incident_id,
                **plan_data
            }
        }
    )


async def broadcast_plan_approved(incident_id: str, approval_data: Dict):
    """Broadcast when plan is approved."""
    await manager.broadcast_to_channel(
        "incidents",
        {
            "type": "plan.approved",
            "data": {
                "incident_id": incident_id,
                **approval_data
            }
        }
    )


async def broadcast_hospital_availability(hospital_id: str, availability_data: Dict):
    """Broadcast hospital availability update."""
    await manager.broadcast_to_channel(
        "hospitals",
        {
            "type": "hospital.availability_changed",
            "data": {
                "hospital_id": hospital_id,
                **availability_data
            }
        }
    )


async def broadcast_dashboard_stats(stats_data: Dict):
    """Broadcast dashboard statistics update."""
    await manager.broadcast_to_channel(
        "dashboard",
        {
            "type": "dashboard.stats_updated",
            "data": stats_data
        }
    )


# ============================================================================
# CONNECTION STATS ENDPOINT
# ============================================================================

@router.get("/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics."""
    return {
        "success": True,
        "data": manager.get_stats()
    }


# Start heartbeat on module import
import asyncio
try:
    loop = asyncio.get_event_loop()
    if not manager.heartbeat_task:
        manager.heartbeat_task = loop.create_task(manager.start_heartbeat())
except Exception as e:
    logger.warning(f"Could not start heartbeat task: {e}")
