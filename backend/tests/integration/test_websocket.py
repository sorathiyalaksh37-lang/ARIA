"""
WebSocket Integration Test
Tests real-time updates and WebSocket connections
"""
import asyncio
import json
from datetime import datetime
import socketio

# Configuration
WS_URL = "http://localhost:8000"

class WebSocketTester:
    """Test WebSocket real-time updates"""
    
    def __init__(self):
        self.sio = socketio.AsyncClient()
        self.messages_received = []
        self.connected = False
        
    async def connect(self):
        """Connect to WebSocket server"""
        print(f"🔌 Connecting to WebSocket: {WS_URL}")
        
        @self.sio.event
        async def connect():
            self.connected = True
            print("✅ Connected to WebSocket server")
            print(f"   Session ID: {self.sio.sid}")
        
        @self.sio.event
        async def disconnect():
            self.connected = False
            print("❌ Disconnected from WebSocket server")
        
        @self.sio.event
        async def incident_created(data):
            print(f"📨 Received: incident_created")
            print(f"   Data: {json.dumps(data, indent=2)}")
            self.messages_received.append({
                "event": "incident_created",
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        @self.sio.event
        async def incident_updated(data):
            print(f"📨 Received: incident_updated")
            print(f"   Data: {json.dumps(data, indent=2)}")
            self.messages_received.append({
                "event": "incident_updated",
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        @self.sio.event
        async def ambulance_dispatched(data):
            print(f"📨 Received: ambulance_dispatched")
            print(f"   Data: {json.dumps(data, indent=2)}")
            self.messages_received.append({
                "event": "ambulance_dispatched",
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        @self.sio.event
        async def ambulance_location_update(data):
            print(f"📨 Received: ambulance_location_update")
            print(f"   Ambulance: {data.get('ambulance_id')}, Location: ({data.get('latitude')}, {data.get('longitude')})")
            self.messages_received.append({
                "event": "ambulance_location_update",
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        @self.sio.event
        async def agent_status_update(data):
            print(f"📨 Received: agent_status_update")
            print(f"   Data: {json.dumps(data, indent=2)}")
            self.messages_received.append({
                "event": "agent_status_update",
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        try:
            await self.sio.connect(WS_URL)
            return True
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            return False
    
    async def disconnect(self):
        """Disconnect from WebSocket"""
        if self.connected:
            await self.sio.disconnect()
    
    async def test_subscription(self):
        """Test event subscription"""
        print("\n📡 Testing event subscription...")
        
        # Subscribe to incidents
        await self.sio.emit('subscribe_incidents')
        print("   Subscribed to incidents")
        
        # Subscribe to ambulances
        await self.sio.emit('subscribe_ambulances')
        print("   Subscribed to ambulances")
        
        # Subscribe to agents
        await self.sio.emit('subscribe_agents')
        print("   Subscribed to agents")
        
        print("✅ Subscription test complete")
    
    async def test_ping(self):
        """Test ping/pong"""
        print("\n🏓 Testing ping...")
        
        response_received = False
        
        @self.sio.event
        async def pong(data):
            nonlocal response_received
            response_received = True
            print(f"✅ Received pong: {data}")
        
        await self.sio.emit('ping', {'message': 'test'})
        
        # Wait for response
        await asyncio.sleep(1)
        
        if not response_received:
            print("⚠️  No pong received")
        
        return response_received
    
    async def listen(self, duration: int = 30):
        """Listen for events for specified duration"""
        print(f"\n👂 Listening for events for {duration} seconds...")
        print("   (Create incidents or update resources to trigger events)")
        
        start_time = datetime.utcnow()
        
        while (datetime.utcnow() - start_time).total_seconds() < duration:
            await asyncio.sleep(1)
            remaining = duration - int((datetime.utcnow() - start_time).total_seconds())
            if remaining % 5 == 0:
                print(f"   {remaining}s remaining...")
        
        print(f"\n✅ Listening complete. Received {len(self.messages_received)} events.")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("WEBSOCKET TEST SUMMARY")
        print("="*70)
        print(f"Connection Status: {'✅ Connected' if self.connected else '❌ Disconnected'}")
        print(f"Events Received: {len(self.messages_received)}")
        
        if self.messages_received:
            print("\nEvent Breakdown:")
            event_counts = {}
            for msg in self.messages_received:
                event = msg["event"]
                event_counts[event] = event_counts.get(event, 0) + 1
            
            for event, count in event_counts.items():
                print(f"  • {event}: {count}")
        
        print("\n" + "="*70)


async def main():
    """Main test execution"""
    print("\n" + "="*70)
    print("ARIA WEBSOCKET INTEGRATION TEST")
    print("="*70 + "\n")
    
    tester = WebSocketTester()
    
    try:
        # Connect
        connected = await tester.connect()
        if not connected:
            print("\n❌ Failed to connect to WebSocket server")
            print("   Make sure the backend server is running at", WS_URL)
            return
        
        # Wait for connection to stabilize
        await asyncio.sleep(1)
        
        # Test subscription
        await tester.test_subscription()
        
        # Test ping
        await tester.test_ping()
        
        # Listen for events
        await tester.listen(duration=30)
        
        # Print summary
        tester.print_summary()
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
    finally:
        # Disconnect
        await tester.disconnect()
        print("\n👋 WebSocket test complete\n")


if __name__ == "__main__":
    asyncio.run(main())
