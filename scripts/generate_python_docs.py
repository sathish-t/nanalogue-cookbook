#!/usr/bin/env python3
# Generates Python API documentation from pynanalogue docstrings.
# Creates src/all_python_functions.md with all function documentation.

import inspect
import sys
from pathlib import Path


def format_signature(name, sig):
    """Format a function signature with proper line breaks for readability."""
    sig_str = f"{name}{sig}"

    # If signature is short enough, return as-is
    if len(sig_str) <= 80:
        return sig_str

    # For long signatures, format with line breaks after each parameter
    params = []
    try:
        for param in sig.parameters.values():
            params.append(str(param))
    except Exception:
        return sig_str

    if not params:
        return sig_str

    # Build formatted signature with line breaks
    lines = [f"{name}("]
    for i, param in enumerate(params):
        if i < len(params) - 1:
            lines.append(f"    {param},")
        else:
            lines.append(f"    {param}")
    lines.append(")")

    return "\n".join(lines)


def escape_markdown_brackets(text: str) -> str:
    """Escape square brackets using HTML entities to prevent markdown link parsing.

    Preserves brackets inside backticks (inline code).
    """
    result = []
    in_inline_code = False

    for char in text:
        if char == '`':
            in_inline_code = not in_inline_code
            result.append(char)
            continue

        if in_inline_code:
            result.append(char)
            continue

        if char == '[':
            result.append('&#91;')
        elif char == ']':
            result.append('&#93;')
        else:
            result.append(char)

    return ''.join(result)


def format_docstring(docstring):
    """Format docstring with proper markdown, preserving structure."""
    if not docstring:
        return ""

    lines = docstring.split('\n')
    formatted_lines = []
    in_args_section = False
    current_param = []

    for line in lines:
        stripped = line.strip()

        # Detect section headers like "# Args", "# Returns", etc.
        if stripped.startswith('#') and stripped[1:].strip() in ['Args', 'Arguments', 'Parameters',
                                                                  'Returns', 'Yields', 'Raises',
                                                                  'Note', 'Notes', 'Example',
                                                                  'Examples', 'Errors', 'Example output']:
            # If we were building a parameter, add it first
            if current_param:
                formatted_lines.append("- " + " ".join(current_param))
                formatted_lines.append("")
                current_param = []

            section_name = stripped[1:].strip()
            in_args_section = (section_name in ['Args', 'Arguments', 'Parameters'])
            # Make section headers bold
            formatted_lines.append(f"**{section_name}**")
            formatted_lines.append("")  # Add blank line after header
        elif in_args_section and stripped:
            # Check if this line starts a new parameter (has format "param_name (type):")
            # Look for pattern: word followed by (type):
            if ('(' in stripped and '):' in stripped and
                not stripped.startswith('-') and not stripped.startswith('*')):
                # This is a new parameter line
                if current_param:
                    # Save previous parameter
                    formatted_lines.append("- " + " ".join(current_param))
                    formatted_lines.append("")
                # Start new parameter
                current_param = [stripped]
            elif current_param:
                # This is a continuation of the current parameter
                current_param.append(stripped)
            else:
                # Not in a parameter yet, just add the line
                formatted_lines.append(line)
        else:
            # Not in args section, or empty line
            if current_param:
                # End of args section, save current parameter
                formatted_lines.append("- " + " ".join(current_param))
                formatted_lines.append("")
                current_param = []
                in_args_section = False
            formatted_lines.append(line)

    # Handle any remaining parameter
    if current_param:
        formatted_lines.append("- " + " ".join(current_param))
        formatted_lines.append("")

    # Escape brackets outside of fenced code blocks (``` delimited sections)
    result_lines = []
    in_fenced_code_block = False

    for line in formatted_lines:
        if line.strip().startswith('```'):
            in_fenced_code_block = not in_fenced_code_block
            result_lines.append(line)
            continue

        if in_fenced_code_block:
            result_lines.append(line)
        else:
            result_lines.append(escape_markdown_brackets(line))

    return "\n".join(result_lines)


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
        lines.append(format_signature(name, sig))
        lines.append("```")
        lines.append("")
    except Exception:
        # Some built-in functions don't have signatures
        pass

    # Add docstring
    docstring = inspect.getdoc(func)
    if docstring:
        formatted_doc = format_docstring(docstring)
        lines.append(formatted_doc)
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
            # Indent method docs to show hierarchy
            lines.extend([f"#### `{method_name}`", ""])

            # Add signature
            try:
                sig = inspect.signature(method)
                lines.append("```python")
                lines.append(format_signature(method_name, sig))
                lines.append("```")
                lines.append("")
            except Exception:
                pass

            # Add docstring
            method_doc = inspect.getdoc(method)
            if method_doc:
                formatted_doc = format_docstring(method_doc)
                lines.append(formatted_doc)
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
        "> **Note**: This file is auto-generated.",
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
