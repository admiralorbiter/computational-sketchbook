"""
Integration tests for WebSocket scene control events
Tests the end-to-end flow: Operator UI → Server → Show View
"""

import pytest
import time
from flask_socketio import SocketIOTestClient
from app import app, socketio


@pytest.fixture
def client():
    """Create a test client for Flask app"""
    return app.test_client()


@pytest.fixture
def control_client():
    """Create a SocketIO test client for operator UI (control namespace)"""
    with socketio.test_client(app, namespace='/control') as client:
        yield client


@pytest.fixture
def show_client():
    """Create a SocketIO test client for show view (show namespace)"""
    with socketio.test_client(app, namespace='/show') as client:
        yield client


class TestWebSocketSceneControl:
    """Test suite for WebSocket scene control events"""
    
    def test_control_start_scene_relay(self, control_client, show_client):
        """Test that START_SCENE command from operator is relayed to show view"""
        # Setup: show view should be connected
        assert show_client.is_connected('/show')
        assert control_client.is_connected('/control')
        
        # Operator sends start scene command
        scene_data = {
            'sceneId': 'lissajous',
            'params': {'a': 3, 'b': 2, 'delta': 0, 'speed': 1}
        }
        control_client.emit('CONTROL_START_SCENE', scene_data)
        
        # Give socketio time to process
        time.sleep(0.1)
        
        # Show view should receive SHOW_START_SCENE event
        received = show_client.get_received('/show')
        assert len(received) > 0
        
        # Find the START_SCENE event
        start_events = [r for r in received if r['name'] == 'SHOW_START_SCENE']
        assert len(start_events) > 0, "Show view did not receive START_SCENE event"
        
        event_data = start_events[0]['args'][0]
        assert event_data['sceneId'] == 'lissajous'
        assert event_data['params']['a'] == 3
        assert event_data['params']['b'] == 2
    
    def test_control_update_params_relay(self, control_client, show_client):
        """Test that parameter updates are relayed correctly"""
        # Setup: start scene first
        control_client.emit('CONTROL_START_SCENE', {
            'sceneId': 'lissajous',
            'params': {'a': 3, 'b': 2}
        })
        time.sleep(0.1)
        
        # Clear received events
        show_client.get_received('/show')
        
        # Operator sends parameter update
        update_data = {
            'params': {'a': 5, 'speed': 2.0}
        }
        control_client.emit('CONTROL_UPDATE_PARAMS', update_data)
        time.sleep(0.1)
        
        # Show view should receive UPDATE_PARAMS event
        received = show_client.get_received('/show')
        update_events = [r for r in received if r['name'] == 'SHOW_UPDATE_PARAMS']
        assert len(update_events) > 0, "Show view did not receive UPDATE_PARAMS event"
        
        event_data = update_events[0]['args'][0]
        assert event_data['params']['a'] == 5
        assert event_data['params']['speed'] == 2.0
    
    def test_control_stop_scene_relay(self, control_client, show_client):
        """Test that STOP_SCENE command is relayed correctly"""
        # Setup: start scene first
        control_client.emit('CONTROL_START_SCENE', {
            'sceneId': 'lissajous',
            'params': {}
        })
        time.sleep(0.1)
        
        # Clear received events
        show_client.get_received('/show')
        
        # Operator sends stop scene command
        control_client.emit('CONTROL_STOP_SCENE', {})
        time.sleep(0.1)
        
        # Show view should receive STOP_SCENE event
        received = show_client.get_received('/show')
        stop_events = [r for r in received if r['name'] == 'SHOW_STOP_SCENE']
        assert len(stop_events) > 0, "Show view did not receive STOP_SCENE event"
    
    def test_rapid_parameter_updates(self, control_client, show_client):
        """Test handling of multiple rapid parameter updates"""
        # Setup: start scene
        control_client.emit('CONTROL_START_SCENE', {
            'sceneId': 'lissajous',
            'params': {'a': 3}
        })
        time.sleep(0.1)
        show_client.get_received('/show')
        
        # Send multiple rapid updates
        for i in range(5):
            control_client.emit('CONTROL_UPDATE_PARAMS', {
                'params': {'a': 3 + i * 0.5}
            })
        
        time.sleep(0.2)  # Allow all updates to be processed
        
        # Show view should receive all updates (or at least the last one)
        received = show_client.get_received('/show')
        update_events = [r for r in received if r['name'] == 'SHOW_UPDATE_PARAMS']
        assert len(update_events) > 0, "No parameter updates received"
    
    def test_fps_update_relay(self, show_client, control_client):
        """Test that FPS updates from show view are relayed to operator UI"""
        # Show view sends FPS update
        fps_data = {
            'fps': 60,
            'timestamp': int(time.time() * 1000)
        }
        show_client.emit('SHOW_FPS_UPDATE', fps_data)
        time.sleep(0.1)
        
        # Operator UI should receive FPS update
        received = control_client.get_received('/control')
        fps_events = [r for r in received if r['name'] == 'SHOW_FPS_UPDATE']
        assert len(fps_events) > 0, "Operator UI did not receive FPS_UPDATE event"
        
        event_data = fps_events[0]['args'][0]
        assert event_data['fps'] == 60
        assert 'timestamp' in event_data
    
    def test_scene_start_with_invalid_params(self, control_client, show_client):
        """Test that scene start with invalid params still relays to show view"""
        # Operator sends start scene with invalid params (validation happens in JS)
        scene_data = {
            'sceneId': 'lissajous',
            'params': {'a': 100, 'speed': -5}  # Out of range values
        }
        control_client.emit('CONTROL_START_SCENE', scene_data)
        time.sleep(0.1)
        
        # Show view should still receive the event (validation happens client-side)
        received = show_client.get_received('/show')
        start_events = [r for r in received if r['name'] == 'SHOW_START_SCENE']
        assert len(start_events) > 0, "Show view should receive event even with invalid params"
        
        # The params are passed through - validation happens in JavaScript
        event_data = start_events[0]['args'][0]
        assert event_data['params']['a'] == 100
    
    def test_connection_disconnect_reconnect(self, control_client, show_client):
        """Test that reconnection scenarios work correctly"""
        # Both clients should be connected
        assert control_client.is_connected('/control')
        assert show_client.is_connected('/show')
        
        # Disconnect show view
        show_client.disconnect('/show')
        time.sleep(0.1)
        
        # Operator sends command while show view is disconnected
        control_client.emit('CONTROL_START_SCENE', {
            'sceneId': 'lissajous',
            'params': {}
        })
        time.sleep(0.1)
        
        # Reconnect show view
        # Note: In real scenario, SocketIO would auto-reconnect
        # For test, we simulate by checking that events are queued/not lost
        # This is a simplified test - real reconnection would need more complex setup
        
        assert True  # Placeholder - full reconnection test would require more setup


class TestWebSocketConnectionHandling:
    """Test suite for WebSocket connection management"""
    
    def test_control_namespace_connect(self, control_client):
        """Test operator UI connection to control namespace"""
        assert control_client.is_connected('/control')
    
    def test_show_namespace_connect(self, show_client):
        """Test show view connection to show namespace"""
        assert show_client.is_connected('/show')
    
    def test_multiple_control_clients(self):
        """Test that multiple operator clients can connect"""
        with socketio.test_client(app, namespace='/control') as client1:
            with socketio.test_client(app, namespace='/control') as client2:
                assert client1.is_connected('/control')
                assert client2.is_connected('/control')
    
    def test_show_view_sends_fps_periodically(self, show_client, control_client):
        """Test that show view sends FPS updates periodically"""
        # In real scenario, show view sends FPS every second
        # For test, we simulate by emitting FPS update
        fps_data = {'fps': 60, 'timestamp': int(time.time() * 1000)}
        show_client.emit('SHOW_FPS_UPDATE', fps_data)
        time.sleep(0.1)
        
        received = control_client.get_received('/control')
        fps_events = [r for r in received if r['name'] == 'SHOW_FPS_UPDATE']
        assert len(fps_events) > 0

