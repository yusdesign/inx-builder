"""
Configuration handling for INX Builder
"""

import json
import yaml
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


@dataclass
class Parameter:
    """Extension parameter configuration"""
    name: str
    type: str  # int, float, string, boolean, optiongroup, notebook
    default: Any = None
    gui_text: Optional[str] = None
    gui_description: Optional[str] = None
    min: Optional[float] = None
    max: Optional[float] = None
    options: List[str] = field(default_factory=list)  # For optiongroup
    pages: List[Dict[str, str]] = field(default_factory=list)  # For notebook
    appearance: str = 'full'  # full, minimal, combo
    
    def validate(self):
        """Validate parameter configuration"""
        if self.type not in ['int', 'float', 'string', 'boolean', 'optiongroup', 'notebook']:
            raise ValueError(f"Invalid parameter type: {self.type}")
        
        if self.type == 'optiongroup' and not self.options:
            raise ValueError("Optiongroup parameters require options")
        
        if self.type == 'notebook' and not self.pages:
            raise ValueError("Notebook parameters require pages")
        
        if self.min is not None and self.max is not None and self.min > self.max:
            raise ValueError(f"min ({self.min}) cannot be greater than max ({self.max})")


@dataclass
class ExtensionConfig:
    """Extension configuration"""
    name: str
    type: str = 'effect'
    id: Optional[str] = None
    author: str = 'Anonymous'
    email: Optional[str] = None
    description: str = 'Inkscape Extension'
    version: str = '1.0.0'
    license: str = 'GPL-2.0-or-later'
    requires: List[str] = field(default_factory=list)
    parameters: List[Parameter] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.id:
            # Generate ID from name
            clean_name = self.name.lower().replace(' ', '_').replace('-', '_')
            self.id = f"org.inkscape.{self.type}.{clean_name}"
    
    def to_dict(self):
        """Convert to dictionary for serialization"""
        data = asdict(self)
        # Convert parameters to dicts
        data['parameters'] = [asdict(p) for p in self.parameters]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create from dictionary"""
        # Convert parameter dicts to Parameter objects
        params_data = data.pop('parameters', [])
        config = cls(**data)
        config.parameters = [Parameter(**p) for p in params_data]
        return config
    
    def validate(self):
        """Validate entire configuration"""
        if not self.name:
            raise ValueError("Extension name is required")
        
        if self.type not in ['effect', 'input', 'output', 'render', 'custom']:
            raise ValueError(f"Invalid extension type: {self.type}")
        
        for param in self.parameters:
            param.validate()


def load_config(filepath: str) -> ExtensionConfig:
    """Load configuration from JSON or YAML file"""
    path = Path(filepath)
    
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {filepath}")
    
    with open(path, 'r') as f:
        if path.suffix.lower() == '.json':
            data = json.load(f)
        elif path.suffix.lower() in ['.yaml', '.yml']:
            data = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported config file format: {path.suffix}")
    
    return ExtensionConfig.from_dict(data)


def save_config(config: ExtensionConfig, filepath: str):
    """Save configuration to JSON file"""
    with open(filepath, 'w') as f:
        json.dump(config.to_dict(), f, indent=2)


def validate_config(config: ExtensionConfig):
    """Validate configuration and raise errors if invalid"""
    config.validate()
    return True
