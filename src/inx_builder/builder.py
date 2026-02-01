"""
Core builder class for Inkscape extensions
"""

import os
import shutil
import json
import zipfile
from pathlib import Path
from datetime import datetime
import platform
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .config import ExtensionConfig


class ExtensionBuilder:
    """Builds Inkscape extensions from templates"""
    
    def __init__(self, config=None, template_name=None):
        from .config import ExtensionConfig
        if isinstance(config, dict):
            self.config = ExtensionConfig.from_dict(config)
        else:
            self.config = config
        self.template_name = template_name or self.config.type or 'basic_effect'
        
        # Setup Jinja2 environment
        templates_dir = Path(__file__).parent.parent / 'templates'
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        self.env.filters['to_snake'] = lambda s: s.lower().replace(' ', '_')
        self.env.filters['to_camel'] = lambda s: ''.join(word.title() for word in s.split('_'))
        
    @classmethod
    def from_directory(cls, source_dir):
        """Load builder from existing extension directory"""
        config_path = Path(source_dir) / 'extension.json'
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            # Try to infer config from files
            config = cls._infer_config(source_dir)
        
        return cls(config)
    
    @staticmethod
    def _infer_config(source_dir):
        """Infer configuration from existing extension files"""
        # This is a simplified version - in reality, you'd parse .inx files
        return {
            'name': Path(source_dir).name,
            'type': 'effect',
            'id': f"org.inkscape.effect.{Path(source_dir).name}",
        }
    
    def build(self, output_dir='./output', verbose=False):
        """Build the extension"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Get template directory
        template_dir = Path(__file__).parent.parent / 'templates' / self.template_name
        
        if not template_dir.exists():
            raise ValueError(f"Template '{self.template_name}' not found")
        
        # Prepare template context
        context = self._prepare_context()
        
        if verbose:
            print(f"Building extension: {self.config.name}")
            print(f"Template: {self.template_name}")
            print(f"Output: {output_path}")
        
        # Process all template files
        for template_file in template_dir.rglob('*.j2'):
            # Get relative path from template directory
            rel_path = template_file.relative_to(template_dir)
            
            # Remove .j2 extension
            output_file = output_path / str(rel_path).replace('.j2', '')
            
            # Render template
            template = self.env.get_template(str(rel_path))
            content = template.render(**context)
            
            # Ensure parent directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            if verbose:
                print(f"  Created: {output_file}")
        
        # Copy non-template files
        for item in template_dir.iterdir():
            if item.is_file() and not item.suffix == '.j2':
                shutil.copy2(item, output_path / item.name)
                if verbose:
                    print(f"  Copied: {item.name}")
        
        # Save configuration
        config_file = output_path / 'extension.json'
        with open(config_file, 'w') as f:
            json.dump(self.config.to_dict(), f, indent=2)
        
        print(f"✅ Extension built successfully in: {output_path}")
        return output_path
    
    def _prepare_context(self):
        """Prepare context for template rendering"""
        return {
            'config': self.config,
            'ext_name': self.config.name.lower().replace(' ', '_'),
            'ext_class': ''.join(word.title() for word in self.config.name.split()),
            'year': datetime.now().year,
            'platform': platform.system(),
            'parameters': self.config.parameters,
        }
    
    def _generate_parameter(self, param_config):
        """Generate XML for a single parameter"""
        param_type = param_config.get('type', 'string')
        
        # Base XML structure
        if param_type == 'optiongroup':
            xml = f'<param name="{param_config["name"]}" type="optiongroup" appearance="{param_config.get("appearance", "full")}">\n'
            xml += f'  <_gui-text>{param_config.get("gui_text", param_config["name"])}</_gui-text>\n'
            for option in param_config.get('options', []):
                xml += f'  <_option value="{option.lower()}">{option}</_option>\n'
            if param_config.get('default'):
                xml += f'  <_default>{param_config["default"]}</_default>\n'
            xml += '</param>'
        elif param_type == 'notebook':
            xml = f'<param name="{param_config["name"]}" type="notebook">\n'
            for page in param_config.get('pages', []):
                xml += f'  <page name="{page["name"]}" gui-text="{page["gui_text"]}"/>\n'
            xml += '</param>'
        else:
            xml = f'<param name="{param_config["name"]}" type="{param_type}"'
            
            # Add attributes based on type
            if param_type in ['int', 'float']:
                if param_config.get('min') is not None:
                    xml += f' min="{param_config["min"]}"'
                if param_config.get('max') is not None:
                    xml += f' max="{param_config["max"]}"'
            
            # Add GUI text and description
            gui_text = param_config.get('gui_text', param_config['name'].replace('_', ' ').title())
            xml += f'\n      gui-text="{gui_text}"'
            
            if param_config.get('gui_description'):
                xml += f' gui-description="{param_config["gui_description"]}"'
            
            # Close tag
            if param_config.get('default') is not None:
                xml += f'>{param_config["default"]}</param>'
            else:
                xml += '/>'
        
        return xml
    
    def build_zip(self, output_dir=None):
        """Build extension and create ZIP archive"""
        if output_dir:
            build_dir = self.build(output_dir)
        else:
            build_dir = self.build()
        
        # Create ZIP file
        zip_name = f"{self.config.name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = build_dir.parent / zip_name
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in build_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(build_dir)
                    zipf.write(file_path, arcname)
        
        return zip_path
    
    def install_to_inkscape(self):
        """Install the built extension to Inkscape"""
        system = platform.system()
        
        if system == 'Windows':
            inkscape_dir = Path(os.environ.get('APPDATA', '')) / 'inkscape' / 'extensions'
        elif system == 'Darwin':  # macOS
            inkscape_dir = Path.home() / 'Library' / 'Application Support' / 'inkscape' / 'extensions'
        else:  # Linux
            inkscape_dir = Path.home() / '.config' / 'inkscape' / 'extensions'
        
        inkscape_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy .inx and .py files
        for ext in ['.inx', '.py']:
            for file in Path.cwd().glob(f'*{ext}'):
                shutil.copy2(file, inkscape_dir / file.name)
        
        print(f"✅ Extension installed to: {inkscape_dir}")
