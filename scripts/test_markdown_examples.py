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

from test_data import create_test_data

COMMAND_TIMEOUT_SECONDS = 60
REPO_ROOT = Path(__file__).parent.parent.resolve()
OUTPUTS_DIR = REPO_ROOT / "outputs"


def is_gitignored(file_path: Path) -> bool:
    """Check if a file is ignored by git. Exit code 0 means the file IS ignored."""
    result = subprocess.run(
        ['git', 'check-ignore', '-q', str(file_path)],
        cwd=REPO_ROOT,
        capture_output=True
    )
    return result.returncode == 0


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


def find_replace_regions(content: str) -> list[tuple[int, int, str, str]]:
    """Find REPLACE tag regions and extract their replacement rules.

    Returns list of (start_pos, end_pos, from_str, to_str) tuples.
    Tags look like: <!--REPLACE_CHR1_WITH_CONTIG_00001:START--> ... <!--REPLACE_CHR1_WITH_CONTIG_00001:END-->
    """
    regions = []
    # Match REPLACE_<FROM>_WITH_<TO>:START and corresponding END tags
    pattern = r'<!--REPLACE_([^_]+)_WITH_([^:]+):START-->(.*?)<!--REPLACE_\1_WITH_\2:END-->'

    for match in re.finditer(pattern, content, re.DOTALL):
        from_str = match.group(1)
        to_str = match.group(2)
        start_pos = match.start()
        end_pos = match.end()
        regions.append((start_pos, end_pos, from_str, to_str))

    return regions


def apply_replace_tags(code: str, code_start_pos: int, replace_regions: list[tuple[int, int, str, str]]) -> str:
    """Apply REPLACE tag substitutions to code if it falls within a replace region.

    The tag names use uppercase (e.g., CHR1, CONTIG_00001) but the actual code and
    BAM files use lowercase. This function handles the case conversion automatically.
    """
    for start_pos, end_pos, from_str, to_str in replace_regions:
        if start_pos <= code_start_pos <= end_pos:
            # Replace case-insensitively, using lowercase target (BAM uses lowercase contig names)
            code = re.sub(re.escape(from_str), to_str.lower(), code, flags=re.IGNORECASE)
    return code


def extract_code_blocks(markdown_path: str) -> list[CodeBlock]:
    """Extract fenced code blocks from a markdown file."""
    with open(markdown_path, 'r') as f:
        content = f.read()

    # Find REPLACE tag regions for later substitution
    replace_regions = find_replace_regions(content)

    blocks = []
    # Match fenced code blocks: ```language ... ```
    # Allow optional leading whitespace for indented blocks
    pattern = r'^[ \t]*```(\w+)\n(.*?)^[ \t]*```'

    for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
        language = match.group(1)
        code = match.group(2)

        # Apply REPLACE tag substitutions if this code block is within a replace region
        code = apply_replace_tags(code, match.start(), replace_regions)

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

        # Skip installation commands that we don't want to execute
        first_line = lines[0].strip()
        install_prefixes = ('cargo install', 'pip install', 'pip3 install',
                            'docker pull', 'curl ')
        if any(first_line.startswith(prefix) for prefix in install_prefixes):
            return True, "skipping installation command"

        # Skip blocks with placeholder URLs (example.com)
        if 'example.com' in code:
            return True, "skipping example.com placeholder URL"

    return False, ""


def prepare_bash_code(code: str, test_files: dict[str, Path], work_dir: Path) -> str:
    """Prepare bash code for execution by substituting test files."""
    prepared = textwrap.dedent(code)

    # Replace placeholder BAM files with test files
    for placeholder, real_path in test_files.items():
        prepared = prepared.replace(placeholder, str(real_path))


    # Replace output files with paths in work_dir
    # Use word boundary regex to avoid matching substrings (e.g. densities.tsv within detailed_densities.tsv)
    output_files = ['hypermethylated_reads.txt', 
            'hypermethylated.bam',
            'high_meth_reads.txt',
            'detailed_densities.tsv',
            'densities.tsv']
    for outfile in output_files:
        # Match filename only at word boundaries (not as substring of another path)
        pattern = r'(?<![/\w])' + re.escape(outfile) + r'(?![/\w])'
        prepared = re.sub(pattern, str(work_dir / outfile), prepared)

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
            cwd=OUTPUTS_DIR,
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

    # Filter out gitignored files
    ignored_files = [f for f in md_files if is_gitignored(f)]
    md_files = [f for f in md_files if not is_gitignored(f)]

    if ignored_files:
        print(f"Skipping {len(ignored_files)} gitignored file(s):")
        for f in ignored_files:
            print(f"  - {f}")
        print()

    if not md_files:
        print("No markdown files found")
        return 1

    # Create outputs directory for any files generated by test commands
    OUTPUTS_DIR.mkdir(exist_ok=True)

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
