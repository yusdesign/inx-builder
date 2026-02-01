#!/usr/bin/env python3
"""
INX Builder - Minimal working version
"""

import argparse
import os
from pathlib import Path


def create_simple_extension(name, ext_type, author, output_dir):
    """Create a simple working extension"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Create .inx file
    inx_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<inkscape-extension xmlns="http://www.inkscape.org/namespace/inkscape/extension">
  <_name>{name}</_name>
  <id>org.inkscape.effect.{name.lower().replace(" ", "_")}</id>
  <dependency type="executable" location="extensions">python3</dependency>
  
  <param name="message" type="string" gui-text="Message" gui-description="Test message">Hello World!</param>
  
  <effect>
    <object-type>all</object-type>
    <effects-menu>
      <submenu name="Extensions"/>
    </effects-menu>
  </effect>
  
  <script>
    <command location="inx" interpreter="python">{name.lower().replace(" ", "_")}.py</command>
  </script>
</inkscape-extension>'''
    
    # Create .py file
    py_content = f'''#!/usr/bin/env python3
"""
{name} - Generated with INX Builder
"""

import inkex


class {name.replace(" ", "")}(inkex.EffectExtension):
    """{name} extension"""
    
    def add_arguments(self, pars):
        pars.add_argument("--message", type=str, default="Hello World!", help="Test message")
    
    def effect(self):
        self.msg(f"{{self.options.message}} from {{self.__class__.__name__}}!")


if __name__ == '__main__':
    {name.replace(" ", "")}().run()
'''
    
    # Write files
    snake_name = name.lower().replace(" ", "_")
    
    with open(output_path / f"{snake_name}.inx", "w") as f:
        f.write(inx_content)
    
    with open(output_path / f"{snake_name}.py", "w") as f:
        f.write(py_content)
    
    print(f"✅ Created: {name}")
    print(f"📁 Location: {output_path}")
    print(f"📄 Files: {snake_name}.inx, {snake_name}.py")

def create_extension_from_template(name, ext_type, author, output_dir, template_name=None):
    """Create extension using template system"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    snake_name = name.lower().replace(' ', '_')
    camel_name = ''.join(word.title() for word in name.split())
    
    # Choose template
    if template_name:
        template_dir = Path(__file__).parent.parent / 'templates' / template_name
    elif ext_type == 'render':
        template_dir = Path(__file__).parent.parent / 'templates' / 'mondrian_render'
    else:
        template_dir = Path(__file__).parent.parent / 'templates' / 'basic_effect'
    
    if not template_dir.exists():
        print(f"⚠️ Template not found: {template_dir}")
        return create_simple_extension(name, ext_type, author, output_dir)
    
    # Read and process templates
    for template_file in template_dir.glob('*.j2'):
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Simple template replacement (for now)
        content = template_content
        content = content.replace('{{ config.name }}', name)
        content = content.replace('{{ config.author }}', author)
        content = content.replace('{{ config.description }}', f'{name} Inkscape Extension')
        content = content.replace('{{ ext_id }}', f'org.inkscape.{ext_type}.{snake_name}')
        content = content.replace('{{ snake_name }}', snake_name)
        content = content.replace('{{ camel_name }}', camel_name)
        content = content.replace('{{ year }}', '2024')
        
        output_file = template_file.stem  # Remove .j2
        if output_file == 'extension':
            output_file = snake_name
        
        with open(output_path / output_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f"🎨 Created: {name} (using template: {template_dir.name})")
    print(f"📁 Output: {output_path}")
    
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Simple INX Builder")
    parser.add_argument("--name", "-n", required=True, help="Extension name")
    parser.add_argument("--type", "-t", default="effect", help="Extension type")
    parser.add_argument("--author", "-a", default="Anonymous", help="Author name")
    parser.add_argument("--output", "-o", default="./output", help="Output directory")
    
    args = parser.parse_args()
    
    create_simple_extension(
        name=args.name,
        ext_type=args.type,
        author=args.author,
        output_dir=args.output
    )


if __name__ == "__main__":
    main()
