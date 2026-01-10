#!/usr/bin/env python3
# Generates CLI documentation from nanalogue help text.
# Creates src/all_cli_commands.md with all command help text.

import subprocess
import re
import sys
from pathlib import Path


def get_help_text(command):
    """Get help text for a command."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout if result.returncode == 0 else result.stderr
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after 30 seconds"
    except FileNotFoundError:
        return f"Error: Command not found - {' '.join(command)}"
    except Exception as e:
        return f"Error getting help: {e}"


def parse_subcommands(help_text):
    """Extract subcommand names from main help text."""
    subcommands = []

    # Look for "Commands:" or "COMMANDS:" section
    # Typical clap format shows commands in a section like:
    # Commands:
    #   subcommand1  Description
    #   subcommand2  Description

    lines = help_text.split('\n')
    in_commands_section = False

    for line in lines:
        # Check if we're entering the commands section
        if re.match(r'^Commands?:', line, re.IGNORECASE):
            in_commands_section = True
            continue

        # Check if we've left the commands section (next major section or empty line after commands)
        if in_commands_section:
            # If we hit another major section (Options:, Args:, etc.), stop
            if re.match(r'^[A-Z][a-z]+:', line):
                break

            # Extract command name (first word, indented)
            match = re.match(r'^\s+([a-z][a-z0-9_-]*)\s+', line)
            if match:
                subcommands.append(match.group(1))

    return subcommands


def format_command_section(command_name, help_text):
    """Format a single command's help as markdown."""
    lines = [
        f"## `{command_name}`",
        "",
        "```",
        help_text.strip(),
        "```",
        ""
    ]
    return lines


def main():
    """Generate CLI documentation."""
    output_file = Path(__file__).parent.parent / "src" / "all_cli_commands.md"

    print("Generating CLI documentation...")

    # Get main help
    print("  Getting main help...")
    main_help = get_help_text(["nanalogue", "--help"])

    if main_help.startswith("Error:"):
        print(f"Failed to get main help: {main_help}", file=sys.stderr)
        sys.exit(1)

    # Parse subcommands
    print("  Parsing subcommands...")
    subcommands = parse_subcommands(main_help)
    print(f"  Found {len(subcommands)} subcommands: {', '.join(subcommands)}")

    # Build markdown content
    markdown_lines = [
        "# nanalogue CLI Commands Reference",
        "",
        "> **Note**: This file is auto-generated. Do not edit manually.",
        "",
        "## Main Command",
        "",
        "```",
        main_help.strip(),
        "```",
        ""
    ]

    # Add each subcommand
    if subcommands:
        markdown_lines.append("# Subcommands")
        markdown_lines.append("")

        for subcmd in subcommands:
            print(f"  Getting help for '{subcmd}'...")
            help_text = get_help_text(["nanalogue", subcmd, "--help"])
            markdown_lines.extend(format_command_section(subcmd, help_text))

    # Write to file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(markdown_lines))
    print(f"✓ Generated CLI documentation: {output_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
