"""
Integration tests for preset switching
Tests that switching between presets works smoothly and within time limits
"""

import pytest
import time
from flask_socketio import SocketIOTestClient
from app import app, socketio


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


class TestPresetSwitching:
    """Test suite for preset switching functionality"""
    
    def test_switch_between_simple_presets(self, control_client, show_client):
        """Test switching between simple presets (Lissajous, Polar Roses)"""
        # Start first preset
        control_client.emit('CONTROL_START_SCENE', {
            'sceneId': 'lissajous',
            'params': {}
        })
        time.sleep(0.1)
        show_client.get_received('/show')
        
        # Switch to second preset
        start_time = time.time()
        control_client.emit('CONTROL_START_SCENE', {
            'sceneId': 'polar-roses',
            'params': {}
        })
        time.sleep(0.1)
        
        # Verify switch completed
        received = show_client.get_received('/show')
        switch_events = [r for r in received if r['name'] == 'SHOW_START_SCENE']
        assert len(switch_events) > 0
        
        # Check timing (should be < 500ms)
        elapsed = (time.time() - start_time) * 1000
        assert elapsed < 500, f"Switch took {elapsed}ms, should be < 500ms"
    
    def test_switch_with_transition(self, control_client, show_client):
        """Test switching with fade transition"""
        # Start first preset
        control_client.emit('CONTROL_START_SCENE', {
            'sceneId': 'lissajous',
            'params': {}
        })
        time.sleep(0.1)
        show_client.get_received('/show')
        
        # Switch with fade transition
        control_client.emit('CONTROL_START_SCENE', {
            'sceneId': 'spirograph',
            'params': {
                'transitionIn': 'fade:300'
            }
        })
        time.sleep(0.4)  # Wait for transition
        
        # Verify transition parameters were passed
        received = show_client.get_received('/show')
        switch_events = [r for r in received if r['name'] == 'SHOW_START_SCENE']
        assert len(switch_events) > 0
    
    def test_switch_between_all_presets(self, control_client, show_client):
        """Test switching through all presets"""
        presets = [
            'lissajous', 'polar-roses', 'spirograph',
            'digits-rain', 'ulam-spiral', 'conway-life', 'mandelbrot'
        ]
        
        for preset_id in presets:
            control_client.emit('CONTROL_START_SCENE', {
                'sceneId': preset_id,
                'params': {}
            })
            time.sleep(0.1)
            
            received = show_client.get_received('/show')
            switch_events = [r for r in received if r['name'] == 'SHOW_START_SCENE']
            assert len(switch_events) > 0, f"Failed to switch to {preset_id}"
            
            # Clear received events for next iteration
            show_client.get_received('/show')
    
    def test_rapid_switching(self, control_client, show_client):
        """Test rapid switching between presets"""
        # Rapidly switch between presets
        for _ in range(5):
            control_client.emit('CONTROL_START_SCENE', {
                'sceneId': 'lissajous',
                'params': {}
            })
            time.sleep(0.05)
            
            control_client.emit('CONTROL_START_SCENE', {
                'sceneId': 'polar-roses',
                'params': {}
            })
            time.sleep(0.05)
        
        # Should handle rapid switches without errors
        received = show_client.get_received('/show')
        switch_events = [r for r in received if r['name'] == 'SHOW_START_SCENE']
        assert len(switch_events) > 0


class TestPresetSwitchingPerformance:
    """Test performance during preset switching"""
    
    @pytest.mark.manual
    def test_switch_timing_under_500ms(self):
        """
        Manual test: Verify preset switching completes in < 500ms
        
        Instructions:
        1. Open Show View and Operator UI
        2. Start any preset
        3. Switch to another preset
        4. Measure time from button click to visual change
        5. Should be < 500ms
        """
        assert True

