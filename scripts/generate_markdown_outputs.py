#!/usr/bin/env python3
"""
Generate auto-generated output sections in markdown documentation.

Finds markers in markdown files and replaces content between them with
actual command output from running the code block above the marker.

Markers:
    <!-- AUTO-GENERATED:START -->
    content to be replaced
    <!-- AUTO-GENERATED:END -->

Usage:
    python generate_markdown_outputs.py [markdown_files...]

If no files specified, searches for all .md files in src/
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pynanalogue

COMMAND_TIMEOUT_SECONDS = 60
REPO_ROOT = Path(__file__).parent.parent.resolve()
START_MARKER = "<!-- AUTO-GENERATED:START -->"
END_MARKER = "<!-- AUTO-GENERATED:END -->"
OUTPUT_FILES = ['hypermethylated_reads.txt', 'hypermethylated.bam', 'densities.tsv']


def create_test_data(work_dir: Path) -> dict[str, Path]:
    """Create test BAM files for use in examples."""
    json_config = '''
    {
      "contigs": {
        "number": 3,
        "len_range": [500, 1000]
      },
      "reads": [
        {
          "number": 30,
          "mapq_range": [20, 60],
          "base_qual_range": [20, 40],
          "len_range": [0.3, 0.8],
          "mods": [{
            "base": "C",
            "is_strand_plus": true,
            "mod_code": "m",
            "win": [5, 3],
            "mod_range": [[0.7, 1.0], [0.1, 0.4]]
          }]
        }
      ]
    }
    '''

    bam_path = work_dir / "test_input.bam"
    fasta_path = work_dir / "test_input.fasta"

    pynanalogue.simulate_mod_bam(
        json_config=json_config,
        bam_path=str(bam_path),
        fasta_path=str(fasta_path)
    )

    return {
        "input.bam": bam_path,
        "aligned_reads.bam": bam_path,
    }


def prepare_bash_code(code: str, test_files: dict[str, Path], work_dir: Path) -> str:
    """Prepare bash code for execution by substituting test files and paths."""
    prepared = code

    for placeholder, real_path in test_files.items():
        prepared = prepared.replace(placeholder, str(real_path))

    for outfile in OUTPUT_FILES:
        prepared = prepared.replace(outfile, str(work_dir / outfile))

    prepared = re.sub(r'chr\d+:\d+-\d+', 'contig_00000:0-500', prepared)
    prepared = re.sub(r'\s*>\s*\S+\.tsv\s*$', '', prepared, flags=re.MULTILINE)

    return prepared


def run_bash_command(code: str, work_dir: Path) -> tuple[bool, str, str]:
    """Run a bash command and return (success, stdout, stderr)."""
    env = {**os.environ, 'HOME': str(work_dir)}

    try:
        result = subprocess.run(
            ['bash', '-e', '-c', code],
            capture_output=True,
            text=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
            cwd=REPO_ROOT,
            env=env
        )
        return (result.returncode == 0, result.stdout, result.stderr)
    except subprocess.TimeoutExpired:
        return (False, "", f"Command timed out after {COMMAND_TIMEOUT_SECONDS} seconds")
    except Exception as e:
        return (False, "", str(e))


def find_code_block_before_marker(content: str, marker_pos: int) -> str | None:
    """Find the bash code block immediately before a marker position."""
    text_before = content[:marker_pos]
    pattern = r'```bash\n(.*?)```'
    matches = list(re.finditer(pattern, text_before, re.DOTALL))

    if not matches:
        return None

    return matches[-1].group(1).strip()


def format_output(stdout: str, max_lines: int = 5) -> str:
    """Format command output, truncating if necessary."""
    output_lines = stdout.strip().split('\n')
    if len(output_lines) > max_lines:
        output_lines = output_lines[:max_lines] + ['...']
    return '\n'.join(output_lines)


def process_markdown_file(
    file_path: Path,
    test_files: dict[str, Path],
    work_dir: Path,
    dry_run: bool = False
) -> tuple[bool, int]:
    """Process a markdown file, replacing auto-generated sections."""
    content = file_path.read_text()
    pattern = re.compile(
        rf'{re.escape(START_MARKER)}\n(.*?){re.escape(END_MARKER)}',
        re.DOTALL
    )

    replacements = 0
    errors = []

    def replace_section(match: re.Match) -> str:
        nonlocal replacements

        marker_pos = match.start()
        code = find_code_block_before_marker(content, marker_pos)

        if code is None:
            errors.append(f"No code block found before marker at position {marker_pos}")
            return match.group(0)

        prepared_code = prepare_bash_code(code, test_files, work_dir)
        success, stdout, stderr = run_bash_command(prepared_code, work_dir)

        if not success:
            errors.append(f"Command failed: {stderr}")
            return match.group(0)

        formatted_output = format_output(stdout)
        replacements += 1
        return f"{START_MARKER}\n```\n{formatted_output}\n```\n{END_MARKER}"

    new_content = pattern.sub(replace_section, content)

    if errors:
        for error in errors:
            print(f"  ERROR: {error}", file=sys.stderr)
        return (False, replacements)

    if new_content != content and not dry_run:
        file_path.write_text(new_content)

    return (True, replacements)


def get_markdown_files(file_args: list[str]) -> list[Path]:
    """Get markdown files from arguments or default src/ directory."""
    if file_args:
        return [Path(f) for f in file_args]
    return list((REPO_ROOT / 'src').rglob('*.md'))


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Generate auto-generated output sections in markdown files'
    )
    parser.add_argument('files', nargs='*', help='Markdown files to process')
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='Show what would be done without making changes')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')
    args = parser.parse_args()

    md_files = get_markdown_files(args.files)
    if not md_files:
        print("No markdown files found")
        return 1

    print(f"Processing {len(md_files)} markdown file(s)...\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        work_dir = Path(tmpdir)

        print("Creating test data...")
        test_files = create_test_data(work_dir)
        print(f"  Created test BAM: {test_files['input.bam']}\n")

        total_replacements = 0
        all_success = True
        action = "Would update" if args.dry_run else "Updated"

        for md_file in md_files:
            if args.verbose:
                print(f"Processing {md_file}...")

            success, num_replacements = process_markdown_file(
                md_file, test_files, work_dir, dry_run=args.dry_run
            )

            if num_replacements > 0:
                print(f"  {action} {num_replacements} section(s) in {md_file}")

            total_replacements += num_replacements
            if not success:
                all_success = False

    print()
    print("=" * 60)
    print(f"{action} {total_replacements} auto-generated section(s)")
    print("=" * 60)

    return 0 if all_success else 1


if __name__ == '__main__':
    sys.exit(main())
