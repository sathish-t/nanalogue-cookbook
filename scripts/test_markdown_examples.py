#!/usr/bin/env python3
"""
Test runner for code blocks in markdown documentation.

Extracts fenced code blocks from markdown files and executes them,
verifying they complete successfully.

Usage:
    python test_markdown_examples.py [markdown_files...]

If no files specified, searches for all .md files in src/
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
import textwrap
from dataclasses import dataclass
from pathlib import Path

import pynanalogue

COMMAND_TIMEOUT_SECONDS = 60
REPO_ROOT = Path(__file__).parent.parent.resolve()


@dataclass
class CodeBlock:
    """Represents a fenced code block from markdown."""
    language: str
    code: str
    line_number: int
    file_path: str

    def __str__(self):
        return f"{self.file_path}:{self.line_number} ({self.language})"


@dataclass
class TestResult:
    """Result of running a code block test."""
    block: CodeBlock
    success: bool
    output: str
    error: str


def extract_code_blocks(markdown_path: str) -> list[CodeBlock]:
    """Extract fenced code blocks from a markdown file."""
    with open(markdown_path, 'r') as f:
        content = f.read()

    blocks = []
    # Match fenced code blocks: ```language ... ```
    # Allow optional leading whitespace for indented blocks
    pattern = r'^[ \t]*```(\w+)\n(.*?)^[ \t]*```'

    for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
        language = match.group(1)
        code = match.group(2)

        # Calculate line number
        line_number = content[:match.start()].count('\n') + 1

        blocks.append(CodeBlock(
            language=language,
            code=code,
            line_number=line_number,
            file_path=markdown_path
        ))

    return blocks


def should_skip_block(block: CodeBlock) -> tuple[bool, str]:
    """Determine if a code block should be skipped."""
    # Skip non-executable languages
    if block.language not in ('bash', 'python'):
        return True, f"skipping non-executable language: {block.language}"

    # Skip blocks that are just showing example output (no actual commands)
    code = block.code.strip()

    # Skip if it looks like example output (starts with # comment showing output)
    if block.language == 'bash':
        lines = [line for line in code.split('\n') if line.strip() and not line.strip().startswith('#')]
        if not lines:
            return True, "skipping comment-only block"

        # Skip blocks that look like output examples (no commands, just data)
        first_line = lines[0].strip()
        if first_line.startswith(('#contig', 'a4f36092', '5d10eb9a', 'fffffff1', 'dummyI')):
            return True, "skipping example output block"

        # Skip installation commands that we don't want to execute
        install_prefixes = ('cargo install', 'pip install', 'pip3 install',
                            'docker pull', 'curl ')
        if any(first_line.startswith(prefix) for prefix in install_prefixes):
            return True, "skipping installation command"

    return False, ""


def create_test_data(work_dir: Path) -> dict[str, Path]:
    """Create test BAM files for use in examples."""

    # Create a test BAM with modifications
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
    """Prepare bash code for execution by substituting test files."""
    prepared = textwrap.dedent(code)

    # Replace placeholder BAM files with test files
    for placeholder, real_path in test_files.items():
        prepared = prepared.replace(placeholder, str(real_path))


    # Replace output files with paths in work_dir
    output_files = ['hypermethylated_reads.txt', 'hypermethylated.bam', 'densities.tsv']
    for outfile in output_files:
        prepared = prepared.replace(outfile, str(work_dir / outfile))

    # Replace example regions with test data regions
    # Test BAM has contigs named contig_00000, contig_00001, etc.
    prepared = re.sub(r'chr\d+:\d+-\d+', 'contig_00000:0-500', prepared)

    return prepared


def prepare_python_code(code: str, test_files: dict[str, Path], work_dir: Path) -> str:
    """Prepare Python code for execution by substituting test files."""
    prepared = code
    for placeholder, real_path in test_files.items():
        for quote in ('"', "'"):
            prepared = prepared.replace(f'{quote}{placeholder}{quote}', f'{quote}{real_path}{quote}')
    return prepared


def run_code_block(language: str, code: str, work_dir: Path) -> tuple[bool, str, str]:
    """Run a code block and return (success, stdout, stderr)."""
    if language == 'bash':
        command = ['bash', '-e', '-c', code]
        env = {**os.environ, 'HOME': str(work_dir)}
    else:
        command = [sys.executable, '-c', code]
        env = None

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
            cwd=REPO_ROOT,
            env=env
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"Command timed out after {COMMAND_TIMEOUT_SECONDS} seconds"
    except Exception as e:
        return False, "", str(e)


def run_test(block: CodeBlock, test_files: dict[str, Path], work_dir: Path) -> TestResult:
    """Run a single code block test."""
    if block.language == 'bash':
        prepared_code = prepare_bash_code(block.code, test_files, work_dir)
    elif block.language == 'python':
        prepared_code = prepare_python_code(block.code, test_files, work_dir)
    else:
        return TestResult(block, False, "", f"Unknown language: {block.language}")

    success, stdout, stderr = run_code_block(block.language, prepared_code, work_dir)
    return TestResult(block, success, stdout, stderr)


def print_output_preview(output: str, label: str, max_lines: int = 5) -> None:
    """Print a preview of output with a label prefix."""
    if not output:
        return
    for line in output.strip().split('\n')[:max_lines]:
        print(f"       {label}: {line}")


def main():
    parser = argparse.ArgumentParser(description='Test code blocks in markdown files')
    parser.add_argument('files', nargs='*', help='Markdown files to test')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show output from tests')
    args = parser.parse_args()

    # Find markdown files
    if args.files:
        md_files = [Path(f) for f in args.files]
    else:
        src_dir = REPO_ROOT / 'src'
        md_files = list(src_dir.rglob('*.md'))

    if not md_files:
        print("No markdown files found")
        return 1

    print(f"Testing {len(md_files)} markdown file(s)...\n")

    # Create temp directory and test data
    with tempfile.TemporaryDirectory() as tmpdir:
        work_dir = Path(tmpdir)

        print("Creating test data...")
        test_files = create_test_data(work_dir)
        print(f"  Created test BAM: {test_files['input.bam']}\n")

        results: list[TestResult] = []
        skipped = 0

        for md_file in md_files:
            print(f"Processing {md_file}...")
            blocks = extract_code_blocks(str(md_file))

            for block in blocks:
                skip, reason = should_skip_block(block)
                if skip:
                    if args.verbose:
                        print(f"  SKIP {block}: {reason}")
                    skipped += 1
                    continue

                result = run_test(block, test_files, work_dir)
                results.append(result)

                status = "PASS" if result.success else "FAIL"
                print(f"  {status} {block}")

                if args.verbose or not result.success:
                    print_output_preview(result.output, "stdout")
                    print_output_preview(result.error, "stderr")

            print()

    # Summary
    passed = sum(r.success for r in results)
    failed = len(results) - passed

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed, {skipped} skipped")
    print("=" * 60)

    if failed > 0:
        print("\nFailed tests:")
        for r in results:
            if not r.success:
                print(f"  - {r.block}")
                if r.error:
                    print(f"    Error: {r.error[:200]}")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
