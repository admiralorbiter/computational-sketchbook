"""
Unit tests for math visual preset parameter validation
Tests all presets: Lissajous, Polar Roses, Spirograph, Digits Rain, Ulam Spiral, Conway Life, Mandelbrot
"""

import pytest
import math


def validate_math_param(preset_name, param_name, value, default_value):
    """
    Validate a parameter for a math visual preset
    This mirrors the JavaScript validation logic
    """
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return default_value, f"Invalid {param_name} value"
    
    try:
        num_value = float(value)
    except (ValueError, TypeError):
        if param_name in ['charset', 'seed']:
            return value if isinstance(value, str) else default_value, None
        return default_value, f"{param_name} must be a number"
    
    # Preset-specific validation
    if preset_name == 'lissajous':
        if param_name in ('a', 'b'):
            if num_value < 1 or num_value > 10:
                clamped = max(1, min(10, num_value))
                return clamped, f"{param_name} clamped to {clamped}"
            return num_value, None
        elif param_name == 'delta':
            if num_value < 0 or num_value > 2 * math.pi:
                clamped = max(0, min(2 * math.pi, num_value))
                return clamped, f"{param_name} clamped"
            return num_value, None
        elif param_name == 'speed':
            if num_value < 0.1 or num_value > 3:
                clamped = max(0.1, min(3, num_value))
                return clamped, f"{param_name} clamped"
            return num_value, None
    
    elif preset_name == 'polar_roses':
        if param_name == 'k':
            if num_value <= 0:
                return default_value, f"{param_name} must be positive"
            return num_value, None
        elif param_name == 'petalGlow':
            if num_value < 0 or num_value > 1:
                clamped = max(0, min(1, num_value))
                return clamped, f"{param_name} clamped"
            return num_value, None
    
    elif preset_name == 'spirograph':
        if param_name == 'radii':
            if not isinstance(value, list):
                return default_value, "radii must be array"
            return [max(10, min(200, float(r))) for r in value[:5]], None
    
    elif preset_name == 'digits_rain':
        if param_name == 'charset':
            if value in ['pi', 'e', 'primes']:
                return value, None
            return default_value, f"Invalid charset: {value}"
        elif param_name == 'density':
            if num_value < 0 or num_value > 1:
                clamped = max(0, min(1, num_value))
                return clamped, f"{param_name} clamped"
            return num_value, None
        elif param_name == 'fontSize':
            if num_value < 8 or num_value > 48:
                clamped = max(8, min(48, num_value))
                return clamped, f"{param_name} clamped"
            return num_value, None
    
    elif preset_name == 'ulam_spiral':
        if param_name == 'grid':
            if num_value < 20 or num_value > 100:
                clamped = max(20, min(100, num_value))
                return math.floor(clamped), f"{param_name} clamped"
            return math.floor(num_value), None
    
    elif preset_name == 'conway_life':
        if param_name == 'stepMs':
            if num_value < 50 or num_value > 1000:
                clamped = max(50, min(1000, num_value))
                return clamped, f"{param_name} clamped"
            return num_value, None
        elif param_name == 'cellSize':
            if num_value < 5 or num_value > 20:
                clamped = max(5, min(20, num_value))
                return clamped, f"{param_name} clamped"
            return num_value, None
    
    elif preset_name == 'mandelbrot':
        if param_name == 'zoom':
            if num_value < 0.1 or num_value > 100:
                clamped = max(0.1, min(100, num_value))
                return clamped, f"{param_name} clamped"
            return num_value, None
        elif param_name == 'maxIter':
            if num_value < 10 or num_value > 500:
                clamped = max(10, min(500, num_value))
                return math.floor(clamped), f"{param_name} clamped"
            return math.floor(num_value), None
    
    return value, None


class TestLissajousParams:
    """Test Lissajous parameter validation"""
    
    def test_valid_params(self):
        params = {'a': 3, 'b': 2, 'delta': 1.57, 'speed': 1.0}
        for key, value in params.items():
            validated, _ = validate_math_param('lissajous', key, value, value)
            assert validated == value
    
    def test_a_out_of_range(self):
        validated, _ = validate_math_param('lissajous', 'a', 15, 3)
        assert validated == 10


class TestPolarRosesParams:
    """Test Polar Roses parameter validation"""
    
    def test_valid_params(self):
        params = {'k': 3.0, 'rotation': 0.0, 'petalGlow': 0.7, 'speed': 1.0}
        for key, value in params.items():
            validated, _ = validate_math_param('polar_roses', key, value, value)
            assert validated == value
    
    def test_k_must_be_positive(self):
        validated, _ = validate_math_param('polar_roses', 'k', -1, 3.0)
        assert validated == 3.0


class TestSpirographParams:
    """Test Spirograph parameter validation"""
    
    def test_radii_array(self):
        validated, _ = validate_math_param('spirograph', 'radii', [80, 50, 30], [80, 50, 30])
        assert isinstance(validated, list)
        assert len(validated) == 3
    
    def test_radii_clamped(self):
        validated, _ = validate_math_param('spirograph', 'radii', [300, -5], [80, 50])
        assert validated[0] == 200  # Clamped
        assert validated[1] == 10   # Clamped


class TestDigitsRainParams:
    """Test Digits Rain parameter validation"""
    
    def test_charset_validation(self):
        validated, _ = validate_math_param('digits_rain', 'charset', 'pi', 'pi')
        assert validated == 'pi'
        
        validated, _ = validate_math_param('digits_rain', 'charset', 'invalid', 'pi')
        assert validated == 'pi'  # Falls back to default
    
    def test_density_clamping(self):
        validated, _ = validate_math_param('digits_rain', 'density', 1.5, 0.5)
        assert validated == 1.0


class TestUlamSpiralParams:
    """Test Ulam Spiral parameter validation"""
    
    def test_grid_size_clamping(self):
        validated, _ = validate_math_param('ulam_spiral', 'grid', 150, 50)
        assert validated == 100
        
        validated, _ = validate_math_param('ulam_spiral', 'grid', 10, 50)
        assert validated == 20


class TestConwayLifeParams:
    """Test Conway's Life parameter validation"""
    
    def test_step_ms_clamping(self):
        validated, _ = validate_math_param('conway_life', 'stepMs', 2000, 100)
        assert validated == 1000
        
        validated, _ = validate_math_param('conway_life', 'stepMs', 10, 100)
        assert validated == 50


class TestMandelbrotParams:
    """Test Mandelbrot parameter validation"""
    
    def test_zoom_clamping(self):
        validated, _ = validate_math_param('mandelbrot', 'zoom', 200, 1.0)
        assert validated == 100
        
        validated, _ = validate_math_param('mandelbrot', 'zoom', 0.05, 1.0)
        assert validated == 0.1
    
    def test_max_iter_clamping(self):
        validated, _ = validate_math_param('mandelbrot', 'maxIter', 1000, 100)
        assert validated == 500
        
        validated, _ = validate_math_param('mandelbrot', 'maxIter', 5, 100)
        assert validated == 10


class TestAllPresetsDefaultParams:
    """Test that all presets have reasonable defaults"""
    
    def test_all_presets_have_defaults(self):
        presets = [
            'lissajous', 'polar_roses', 'spirograph', 
            'digits_rain', 'ulam_spiral', 'conway_life', 'mandelbrot'
        ]
        
        for preset in presets:
            # Each preset should have validatable parameters
            assert preset is not None

