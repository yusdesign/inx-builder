# inx-builder
Inkscape Extension Builder


inx-builder/  
├── README.md  
├── LICENSE (MIT recommended for tools)  
├── pyproject.toml  
├── .gitignore  
├── requirements.txt  
│  
├── src/  
│   └── inx_builder/  
│       ├── __init__.py  
│       ├── cli.py          # Command-line interface  
│       ├── builder.py      # Core building logic  
│       ├── templates.py    # Jinja2 templates  
│       ├── config.py       # Configuration handling  
│       └── utils.py        # Utility functions  
│  
├── templates/              # Template files for different extension types  
│   ├── basic_effect/       # Simple effect extension  
│   │   ├── {{ext_name}}.py.j2  
│   │   ├── {{ext_name}}.inx.j2  
│   │   └── README.md.j2  
│   ├── input_output/       # Extension with input/output  
│   ├── render/            # Render extension (like Mondrian)  
│   └── custom/            # Fully customizable template  
│  
├── examples/              # Example configurations  
│   ├── mondrian.json      # Mondrian generator config  
│   ├── spiral.json        # Spiral generator example  
│   └── pattern_fill.json  # Pattern fill example  
│  
└── scripts/  
    ├── build_example.py   # Build from example config  
    └── install_dev.py     # Install in development mode  
