"""
Unit tests for Lissajous curve parameter validation
Tests the expected parameter ranges and validation logic
"""

import pytest
import math


def validate_lissajous_param(param_name, value):
    """
    Validate a single Lissajous parameter value
    This mirrors the JavaScript validation logic for testing
    """
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None, f"Invalid {param_name} value: {value}"
    
    try:
        num_value = float(value)
    except (ValueError, TypeError):
        return None, f"{param_name} must be a number"
    
    if param_name in ('a', 'b'):
        # Frequency ratios: 1-10
        if num_value < 1 or num_value > 10:
            # Clamp to valid range
            clamped = max(1, min(10, num_value))
            return clamped, f"{param_name} out of range, clamped to {clamped}"
        return num_value, None
    
    elif param_name == 'delta':
        # Phase shift: 0-2π
        if num_value < 0 or num_value > 2 * math.pi:
            clamped = max(0, min(2 * math.pi, num_value))
            return clamped, f"{param_name} out of range, clamped to {clamped}"
        return num_value, None
    
    elif param_name == 'speed':
        # Speed: 0.1-3
        if num_value < 0.1 or num_value > 3:
            clamped = max(0.1, min(3, num_value))
            return clamped, f"{param_name} out of range, clamped to {clamped}"
        return num_value, None
    
    elif param_name == 'amplitude':
        # Amplitude: 0.1-0.9
        if num_value < 0.1 or num_value > 0.9:
            clamped = max(0.1, min(0.9, num_value))
            return clamped, f"{param_name} out of range, clamped to {clamped}"
        return num_value, None
    
    return value, None


def validate_lissajous_params(params):
    """
    Validate all Lissajous parameters
    Returns (validated_params, errors, warnings)
    """
    defaults = {
        'a': 3,
        'b': 2,
        'delta': 0,
        'speed': 1,
        'amplitude': 0.4,
        'lineWidth': 2,
        'trailAlpha': 0.05,
        'color': '#39FF14'
    }
    
    validated = defaults.copy()
    errors = []
    warnings = []
    
    for key, value in params.items():
        if key not in defaults:
            warnings.append(f"Unknown parameter: {key}")
            continue
        
        if key == 'color':
            # Color validation
            if not isinstance(value, str) or not (value.startswith('#') or value.isalpha()):
                errors.append(f"Invalid color format: {value}")
                continue
            validated[key] = value
        else:
            validated_value, error_msg = validate_lissajous_param(key, value)
            if error_msg:
                warnings.append(error_msg)
            if validated_value is not None:
                validated[key] = validated_value
    
    return validated, errors, warnings


class TestLissajousParamValidation:
    """Test suite for Lissajous parameter validation"""
    
    def test_valid_params(self):
        """Valid parameters should pass validation"""
        params = {'a': 3, 'b': 2, 'delta': 1.57, 'speed': 1.0}
        validated, errors, warnings = validate_lissajous_params(params)
        assert len(errors) == 0
        assert validated['a'] == 3
        assert validated['b'] == 2
        assert validated['delta'] == 1.57
        assert validated['speed'] == 1.0
    
    def test_param_a_out_of_range_high(self):
        """Parameter 'a' above 10 should be clamped"""
        params = {'a': 15}
        validated, errors, warnings = validate_lissajous_params(params)
        assert len(errors) == 0
        assert validated['a'] == 10
        assert any('clamped' in w for w in warnings)
    
    def test_param_a_out_of_range_low(self):
        """Parameter 'a' below 1 should be clamped"""
        params = {'a': 0.5}
        validated, errors, warnings = validate_lissajous_params(params)
        assert len(errors) == 0
        assert validated['a'] == 1
        assert any('clamped' in w for w in warnings)
    
    def test_param_b_out_of_range(self):
        """Parameter 'b' out of range should be clamped"""
        params = {'b': -5}
        validated, errors, warnings = validate_lissajous_params(params)
        assert validated['b'] == 1
    
    def test_delta_out_of_range(self):
        """Delta parameter out of range should be clamped to 0-2π"""
        params = {'delta': 10}
        validated, errors, warnings = validate_lissajous_params(params)
        assert validated['delta'] == pytest.approx(2 * math.pi)
        
        params = {'delta': -1}
        validated, errors, warnings = validate_lissajous_params(params)
        assert validated['delta'] == 0
    
    def test_speed_out_of_range_high(self):
        """Speed above 3 should be clamped"""
        params = {'speed': 10}
        validated, errors, warnings = validate_lissajous_params(params)
        assert validated['speed'] == 3
    
    def test_speed_out_of_range_low(self):
        """Speed below 0.1 should be clamped"""
        params = {'speed': 0.05}
        validated, errors, warnings = validate_lissajous_params(params)
        assert validated['speed'] == 0.1
    
    def test_null_parameter(self):
        """Null parameters should use defaults"""
        params = {'a': None, 'b': 2}
        validated, errors, warnings = validate_lissajous_params(params)
        assert validated['a'] == 3  # default
        assert validated['b'] == 2
    
    def test_nan_parameter(self):
        """NaN parameters should use defaults"""
        params = {'speed': float('nan')}
        validated, errors, warnings = validate_lissajous_params(params)
        assert validated['speed'] == 1  # default
    
    def test_undefined_parameter(self):
        """Missing parameters should use defaults"""
        params = {'a': 5}
        validated, errors, warnings = validate_lissajous_params(params)
        assert validated['a'] == 5
        assert validated['b'] == 2  # default
        assert validated['delta'] == 0  # default
        assert validated['speed'] == 1  # default
    
    def test_invalid_color_format(self):
        """Invalid color format should produce error"""
        params = {'color': 'invalid-color-format'}
        validated, errors, warnings = validate_lissajous_params(params)
        assert len(errors) > 0
        assert any('color' in e.lower() for e in errors)
    
    def test_valid_color_hex(self):
        """Valid hex color should pass"""
        params = {'color': '#FF0000'}
        validated, errors, warnings = validate_lissajous_params(params)
        assert len(errors) == 0
        assert validated['color'] == '#FF0000'
    
    def test_unknown_parameter(self):
        """Unknown parameters should produce warning but not error"""
        params = {'unknownParam': 123, 'a': 3}
        validated, errors, warnings = validate_lissajous_params(params)
        assert len(errors) == 0
        assert any('unknown' in w.lower() for w in warnings)
        assert 'unknownParam' not in validated
    
    def test_string_number_conversion(self):
        """String numbers should be converted to floats"""
        params = {'a': '5', 'speed': '2.5'}
        validated, errors, warnings = validate_lissajous_params(params)
        assert validated['a'] == 5.0
        assert validated['speed'] == 2.5
    
    def test_all_defaults(self):
        """Empty params should use all defaults"""
        params = {}
        validated, errors, warnings = validate_lissajous_params(params)
        assert validated['a'] == 3
        assert validated['b'] == 2
        assert validated['delta'] == 0
        assert validated['speed'] == 1
        assert validated['amplitude'] == 0.4
        assert validated['color'] == '#39FF14'

