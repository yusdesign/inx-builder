#!/usr/bin/env python3
"""
INX Builder CLI - Command-line tool for building Inkscape extensions
"""

import argparse
import sys
import json
import os
from pathlib import Path
from .builder import ExtensionBuilder
from .config import load_config, validate_config


def main():
    parser = argparse.ArgumentParser(
        description="Build Inkscape extensions from templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  inx-builder new --type effect --name "MyEffect" --output ./my-extension
  inx-builder new --config mondrian.json --output ./mondrian-generator
  inx-builder param --name "radius" --type float --min 0 --max 100
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # New extension command
    new_parser = subparsers.add_parser('new', help='Create new extension')
    new_parser.add_argument('--config', '-c', help='JSON configuration file')
    new_parser.add_argument('--type', '-t', choices=['effect', 'input', 'output', 'render', 'custom'],
                          help='Extension type')
    new_parser.add_argument('--name', '-n', help='Extension name')
    new_parser.add_argument('--id', '-i', help='Extension ID (e.g., org.inkscape.effect.my_effect)')
    new_parser.add_argument('--author', '-a', help='Author name')
    new_parser.add_argument('--email', '-e', help='Author email')
    new_parser.add_argument('--description', '-d', help='Extension description')
    new_parser.add_argument('--output', '-o', default='./output',
                          help='Output directory (default: ./output)')
    new_parser.add_argument('--template', help='Custom template directory')
    new_parser.add_argument('--verbose', '-v', action='store_true',
                          help='Verbose output')
    
    # Add parameter command
    param_parser = subparsers.add_parser('param', help='Generate parameter definition')
    param_parser.add_argument('--name', '-n', required=True, help='Parameter name')
    param_parser.add_argument('--type', '-t', required=True,
                            choices=['int', 'float', 'string', 'boolean', 'optiongroup', 'notebook'],
                            help='Parameter type')
    param_parser.add_argument('--gui-text', help='GUI display text')
    param_parser.add_argument('--gui-description', help='GUI description')
    param_parser.add_argument('--default', help='Default value')
    param_parser.add_argument('--min', help='Minimum value (for int/float)')
    param_parser.add_argument('--max', help='Maximum value (for int/float)')
    param_parser.add_argument('--options', help='Options for optiongroup (comma-separated)')
    param_parser.add_argument('--appearance', choices=['full', 'minimal', 'combo'],
                            default='full', help='GUI appearance')
    
    # Build command
    build_parser = subparsers.add_parser('build', help='Build existing extension')
    build_parser.add_argument('--source', '-s', required=True, help='Source directory')
    build_parser.add_argument('--output', '-o', help='Output directory')
    build_parser.add_argument('--zip', action='store_true', help='Create ZIP archive')
    build_parser.add_argument('--install', action='store_true',
                            help='Install to Inkscape after building')
    
    # List templates command
    subparsers.add_parser('list-templates', help='List available templates')
    
    # Validate config command
    validate_parser = subparsers.add_parser('validate', help='Validate configuration')
    validate_parser.add_argument('config', help='Configuration file to validate')
    
    args = parser.parse_args()
    
    if args.command == 'new':
        if args.config:
            # Load from config file
            config = load_config(args.config)
        else:
            # Build config from command line
            config = {
                'type': args.type,
                'name': args.name,
                'id': args.id or f"org.inkscape.{args.type}.{args.name.lower().replace(' ', '_')}",
                'author': args.author,
                'email': args.email,
                'description': args.description,
                'parameters': []  # Will be added interactively or via config
            }
        
        builder = ExtensionBuilder(config, args.template)
        builder.build(args.output, verbose=args.verbose)
        
    elif args.command == 'param':
        # Generate parameter XML snippet
        param_config = {
            'name': args.name,
            'type': args.type,
            'gui_text': args.gui_text or args.name.replace('_', ' ').title(),
            'gui_description': args.gui_description or '',
            'default': args.default,
            'min': args.min,
            'max': args.max,
            'appearance': args.appearance,
        }
        
        if args.options:
            param_config['options'] = [opt.strip() for opt in args.options.split(',')]
        
        builder = ExtensionBuilder({})
        xml_snippet = builder._generate_parameter(param_config)
        print(xml_snippet)
        
    elif args.command == 'build':
        builder = ExtensionBuilder.from_directory(args.source)
        if args.zip:
            zip_path = builder.build_zip(args.output)
            print(f"Created ZIP: {zip_path}")
        else:
            output_dir = args.output or args.source
            builder.build(output_dir)
            
        if args.install:
            builder.install_to_inkscape()
            
    elif args.command == 'list-templates':
        templates_dir = Path(__file__).parent.parent / 'templates'
        for template in templates_dir.iterdir():
            if template.is_dir():
                print(f"  {template.name}")
                
    elif args.command == 'validate':
        try:
            config = load_config(args.config)
            validate_config(config)
            print("✅ Configuration is valid!")
        except Exception as e:
            print(f"❌ Validation error: {e}")
            sys.exit(1)
            
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
