#!/usr/bin/env python3
"""
Generate auto-generated output sections in markdown documentation.

Finds markers in markdown files and replaces content between them with
actual command output from running the code block above the marker.

Markers (truncated to 5 lines):
    <!-- AUTO-GENERATED:START -->
    content to be replaced
    <!-- AUTO-GENERATED:END -->

Markers (full output, no truncation):
    <!-- AUTO-GENERATED-FULL:START -->
    content to be replaced
    <!-- AUTO-GENERATED-FULL:END -->

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
from dataclasses import dataclass
from pathlib import Path

import pynanalogue

COMMAND_TIMEOUT_SECONDS = 60
REPO_ROOT = Path(__file__).parent.parent.resolve()
OUTPUT_FILES = ['hypermethylated_reads.txt', 'hypermethylated.bam', 'densities.tsv']
DEFAULT_TRUNCATE_LINES = 5


@dataclass
class MarkerConfig:
    """Configuration for an auto-generation marker type."""
    start: str
    end: str
    max_lines: int | None


MARKERS = [
    MarkerConfig(
        start='<!-- AUTO-GENERATED:START -->',
        end='<!-- AUTO-GENERATED:END -->',
        max_lines=DEFAULT_TRUNCATE_LINES,
    ),
    MarkerConfig(
        start='<!-- AUTO-GENERATED-FULL:START -->',
        end='<!-- AUTO-GENERATED-FULL:END -->',
        max_lines=None,
    ),
]


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


@dataclass
class CommandResult:
    """Result of running a bash command."""
    success: bool
    stdout: str
    stderr: str


def run_bash_command(code: str, work_dir: Path) -> CommandResult:
    """Run a bash command and return the result."""
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
        return CommandResult(
            success=result.returncode == 0,
            stdout=result.stdout,
            stderr=result.stderr
        )
    except subprocess.TimeoutExpired:
        return CommandResult(
            success=False,
            stdout="",
            stderr=f"Command timed out after {COMMAND_TIMEOUT_SECONDS} seconds"
        )
    except Exception as e:
        return CommandResult(success=False, stdout="", stderr=str(e))


def find_code_block_before_marker(content: str, marker_pos: int) -> str | None:
    """Find the bash code block immediately before a marker position."""
    text_before = content[:marker_pos]
    pattern = r'```bash\n(.*?)```'
    matches = list(re.finditer(pattern, text_before, re.DOTALL))

    if not matches:
        return None

    return matches[-1].group(1).strip()


def format_output(stdout: str, max_lines: int | None = 5) -> str:
    """Format command output, truncating if necessary. max_lines=None means no truncation."""
    output_lines = stdout.strip().split('\n')
    if max_lines is not None and len(output_lines) > max_lines:
        output_lines = output_lines[:max_lines] + ['...']
    return '\n'.join(output_lines)


def process_marker(
    content: str,
    marker: MarkerConfig,
    test_files: dict[str, Path],
    work_dir: Path,
    errors: list[str]
) -> tuple[str, int]:
    """Process all instances of a single marker type in content."""
    pattern = re.compile(
        rf'{re.escape(marker.start)}\n(.*?){re.escape(marker.end)}',
        re.DOTALL
    )
    replacements = 0

    def replace_section(match: re.Match) -> str:
        nonlocal replacements

        marker_pos = match.start()
        code = find_code_block_before_marker(content, marker_pos)

        if code is None:
            errors.append(f"No code block found before marker at position {marker_pos}")
            return match.group(0)

        prepared_code = prepare_bash_code(code, test_files, work_dir)
        result = run_bash_command(prepared_code, work_dir)

        if not result.success:
            errors.append(f"Command failed: {result.stderr}")
            return match.group(0)

        formatted_output = format_output(result.stdout, max_lines=marker.max_lines)
        replacements += 1
        return f"{marker.start}\n```\n{formatted_output}\n```\n{marker.end}"

    new_content = pattern.sub(replace_section, content)
    return new_content, replacements


def process_markdown_file(
    file_path: Path,
    test_files: dict[str, Path],
    work_dir: Path,
    dry_run: bool = False
) -> tuple[bool, int]:
    """Process a markdown file, replacing auto-generated sections."""
    content = file_path.read_text()
    new_content = content
    total_replacements = 0
    errors: list[str] = []

    for marker in MARKERS:
        new_content, replacements = process_marker(
            new_content, marker, test_files, work_dir, errors
        )
        total_replacements += replacements

    if errors:
        for error in errors:
            print(f"  ERROR: {error}", file=sys.stderr)
        return (False, total_replacements)

    if new_content != content and not dry_run:
        file_path.write_text(new_content)

    return (True, total_replacements)


def get_markdown_files(file_args: list[str]) -> list[Path]:
    """Get markdown files from arguments or default src/ directory."""
    if file_args:
        return [Path(f) for f in file_args]
    return list((REPO_ROOT / 'src').rglob('*.md'))


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate auto-generated output sections in markdown files'
    )
    parser.add_argument('files', nargs='*', help='Markdown files to process')
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='Show what would be done without making changes')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')
    return parser.parse_args()


def main() -> int:
    args = parse_args()

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
