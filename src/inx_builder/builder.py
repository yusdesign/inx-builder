"""
Main builder class - FIXED VERSION
"""

import os
import shutil
from pathlib import Path
from .templates import TemplateManager
from .config import ExtensionConfig


class InxBuilder:
    """Build Inkscape extensions from templates"""
    
    def __init__(self, config, template_name=None):
        # FIX: Handle both dict and ExtensionConfig objects
        from .config import ExtensionConfig
        if isinstance(config, dict):
            self.config = ExtensionConfig.from_dict(config)
        else:
            self.config = config
            
        self.template_mgr = TemplateManager()
        self.output_dir = None
        self.template_name = template_name or self.config.type or 'basic_effect'
    
    def build(self, output_path: str = "./output", clean: bool = True) -> Path:
        """
        Build the extension
        
        Args:
            output_path: Where to put the built extension
            clean: Remove output directory if it exists
            
        Returns:
            Path to built extension
        """
        self.output_dir = Path(output_path)
        
        # Clean or create output directory
        if clean and self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🔨 Building: {self.config.name}")
        print(f"📁 Output: {self.output_dir}")
        
        # Create context for templates
        context = self.template_mgr.create_context(self.config)
        
        # Get template directory
        template_dir = self.template_mgr.TEMPLATES_DIR / self.template_name
        
        if not template_dir.exists():
            print(f"⚠️ Template '{self.template_name}' not found, using 'basic_effect'")
            template_dir = self.template_mgr.TEMPLATES_DIR / 'basic_effect'
        
        # Render each template file
        for template_file in template_dir.glob("*.j2"):
            # Render template
            content = self.template_mgr.render_template(
                f"{self.template_name}/{template_file.name}", 
                context
            )
            
            # Determine output filename
            output_file = template_file.name.replace('.j2', '')
            
            # Special handling for main files
            if output_file == 'extension.py':
                output_file = f"{context['snake_name']}.py"
            elif output_file == 'extension.inx':
                output_file = f"{context['snake_name']}.inx"
            
            # Write file
            output_path = self.output_dir / output_file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  📄 Created: {output_file}")
        
        print(f"✅ Success! Extension built in: {self.output_dir}")
        return self.output_dir


# SIMPLE TEST
if __name__ == "__main__":
    # Quick test
    from .config import ExtensionConfig
    config = ExtensionConfig(
        name="TestExtension",
        type="effect",
        author="TestUser"
    )
    builder = InxBuilder(config)
    builder.build()
