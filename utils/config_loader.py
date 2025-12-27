"""
Configuration loader utility.
"""

import yaml
from pathlib import Path
from datetime import datetime


def load_config(config_path: str) -> dict:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Add timestamp-based log path if not absolute
    if config.get('log_path') and not Path(config['log_path']).is_absolute():
        # Add timestamp to log filename
        log_path = Path(config['log_path'])
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_name = f"{log_path.stem}_{timestamp}{log_path.suffix}"
        config['log_path'] = str(log_path.parent / new_name)
    
    return config


def load_persona_template(template_path: str) -> str:
    """
    Load persona prompt template from file.
    
    Args:
        template_path: Path to template file
        
    Returns:
        Template string
    """
    template_file = Path(template_path)
    
    if not template_file.exists():
        return ""
    
    with open(template_file, 'r') as f:
        return f.read()