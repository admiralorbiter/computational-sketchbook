"""
Configuration management system.

Loads and manages JSON configuration files for easy game tuning.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """
    Manages game configuration files.
    
    Loads JSON configs from the config directory and provides
    easy access to configuration values.
    """
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.configs: Dict[str, Dict[str, Any]] = {}
        
    def load_all(self):
        """Load all JSON configuration files from the config directory."""
        if not self.config_dir.exists():
            print(f"Warning: Config directory {self.config_dir} does not exist")
            return
            
        for config_file in self.config_dir.glob("*.json"):
            config_name = config_file.stem
            try:
                with open(config_file, 'r') as f:
                    self.configs[config_name] = json.load(f)
                print(f"Loaded config: {config_name}")
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config {config_name}: {e}")
    
    def get(self, category: str, key: Optional[str] = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            category: The config file name (without .json)
            key: Optional key within the config file
            
        Returns:
            The configuration value, or None if not found
        """
        if category not in self.configs:
            print(f"Warning: Config category '{category}' not found")
            return None
            
        if key is None:
            return self.configs[category]
            
        return self.configs[category].get(key)
    
    def get_candy_type(self, candy_type: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific candy type."""
        return self.get('candy_types', candy_type)
    
    def get_personality(self, personality: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific personality type."""
        return self.get('personalities', personality)
    
    def get_scenario(self, scenario: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific scenario."""
        return self.get('scenarios', scenario)
    
    def reload(self):
        """Reload all configuration files."""
        self.configs.clear()
        self.load_all()


# Global config manager instance
config_manager = ConfigManager()
