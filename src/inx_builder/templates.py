"""
Template definitions for different extension types
"""

TEMPLATES = {
    'basic_effect': {
        'description': 'Basic effect extension with simple parameters',
        'files': {
            '{{ext_name}}.py.j2': 'main_effect.py',
            '{{ext_name}}.inx.j2': 'extension.inx',
            'README.md.j2': 'README.md',
        },
        'parameters': [
            {
                'name': 'width',
                'type': 'float',
                'default': 100.0,
                'gui_text': 'Width',
                'min': 1,
                'max': 1000,
            },
            {
                'name': 'height',
                'type': 'float',
                'default': 100.0,
                'gui_text': 'Height',
                'min': 1,
                'max': 1000,
            }
        ]
    },
    'render': {
        'description': 'Render extension (like Mondrian generator)',
        'files': {
            '{{ext_name}}.py.j2': 'main_render.py',
            '{{ext_name}}.inx.j2': 'extension.inx',
            'utils.py.j2': 'utils.py',
            'generator.py.j2': 'generator.py',
            'README.md.j2': 'README.md',
        },
        'parameters': [
            {
                'name': 'tab',
                'type': 'notebook',
                'pages': [
                    {'name': 'canvas', 'gui_text': 'Canvas'},
                    {'name': 'settings', 'gui_text': 'Settings'},
                    {'name': 'advanced', 'gui_text': 'Advanced'},
                ]
            },
            {
                'name': 'seed',
                'type': 'int',
                'default': 0,
                'gui_text': 'Random Seed',
                'min': 0,
                'max': 999999,
            }
        ]
    },
    'input_output': {
        'description': 'Extension with file input/output',
        'files': {
            '{{ext_name}}.py.j2': 'main_io.py',
            '{{ext_name}}.inx.j2': 'extension.inx',
            'processor.py.j2': 'processor.py',
            'README.md.j2': 'README.md',
        }
    }
}
