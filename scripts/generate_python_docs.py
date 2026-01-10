#!/usr/bin/env python3
# Generates Python API documentation from pynanalogue docstrings.
# Creates src/all_python_functions.md with all function documentation.

import inspect
import sys
from pathlib import Path


def get_all_members(module):
    """Get all public functions and classes from a module."""
    members = []

    # Get all members
    for name, obj in inspect.getmembers(module):
        # Skip private members
        if name.startswith('_'):
            continue

        # Skip imported modules
        if inspect.ismodule(obj):
            continue

        # Include functions (including built-in functions from Rust/C extensions) and classes
        if inspect.isfunction(obj) or inspect.isbuiltin(obj) or inspect.isclass(obj):
            members.append((name, obj))

    return members


def format_function_docs(name, func):
    """Format function documentation as markdown."""
    lines = [f"## `{name}`", ""]

    # Add signature
    try:
        sig = inspect.signature(func)
        lines.append("```python")
        lines.append(f"{name}{sig}")
        lines.append("```")
        lines.append("")
    except Exception:
        # Some built-in functions don't have signatures
        pass

    # Add docstring
    docstring = inspect.getdoc(func)
    if docstring:
        lines.append(docstring)
        lines.append("")
    else:
        lines.append("*No documentation available.*")
        lines.append("")

    return lines


def format_class_docs(name, cls):
    """Format class documentation as markdown."""
    lines = [f"## `{name}` (class)", ""]

    # Add docstring
    docstring = inspect.getdoc(cls)
    if docstring:
        lines.append(docstring)
        lines.append("")

    # Add methods (only include public methods)
    methods = []
    for method_name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if not method_name.startswith('_'):
            methods.append((method_name, method))

    if methods:
        lines.append("### Methods")
        lines.append("")
        for method_name, method in sorted(methods):
            method_lines = format_function_docs(f"{name}.{method_name}", method)
            # Indent method docs to show hierarchy
            lines.extend([f"#### `{method_name}`", ""])

            # Add signature
            try:
                sig = inspect.signature(method)
                lines.append("```python")
                lines.append(f"{method_name}{sig}")
                lines.append("```")
                lines.append("")
            except Exception:
                pass

            # Add docstring
            method_doc = inspect.getdoc(method)
            if method_doc:
                lines.append(method_doc)
                lines.append("")
            else:
                lines.append("*No documentation available.*")
                lines.append("")

    return lines


def main():
    """Generate Python API documentation."""
    output_file = Path(__file__).parent.parent / "src" / "all_python_functions.md"

    print("Generating Python API documentation...")

    # Import pynanalogue
    try:
        print("  Importing pynanalogue...")
        import pynanalogue
    except ImportError as e:
        print(f"Error: Could not import pynanalogue: {e}", file=sys.stderr)
        print("Make sure pynanalogue is installed: pip install pynanalogue", file=sys.stderr)
        return 1

    # Build markdown content
    markdown_lines = [
        "# pynanalogue Python API Reference",
        "",
        "> **Note**: This file is auto-generated. Do not edit manually.",
        "",
    ]

    # Get all members
    print("  Discovering functions and classes...")
    members = get_all_members(pynanalogue)

    # Separate functions and classes
    functions = [(n, o) for n, o in members if inspect.isfunction(o) or inspect.isbuiltin(o)]
    classes = [(n, o) for n, o in members if inspect.isclass(o)]

    print(f"  Found {len(functions)} functions and {len(classes)} classes")

    # Add functions section
    if functions:
        markdown_lines.append("# Functions")
        markdown_lines.append("")
        for name, func in sorted(functions):
            print(f"  Documenting function '{name}'...")
            markdown_lines.extend(format_function_docs(name, func))

    # Add classes section
    if classes:
        markdown_lines.append("# Classes")
        markdown_lines.append("")
        for name, cls in sorted(classes):
            print(f"  Documenting class '{name}'...")
            markdown_lines.extend(format_class_docs(name, cls))

    # Handle case where no functions or classes found
    if not functions and not classes:
        markdown_lines.append("*No public functions or classes found.*")
        markdown_lines.append("")

    # Write to file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(markdown_lines))
    print(f"✓ Generated Python API documentation: {output_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
