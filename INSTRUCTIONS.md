# Instructions for Contributors

This document describes the automated systems in this repository that help maintain documentation quality.

## Overview

The repository has several automation features that run on every push to `main`:

1. **Markdown example testing** - Verifies that code examples in documentation actually work
2. **Auto-generated output sections** - Automatically updates example output in documentation
3. **Link checking** - Validates all links in the documentation

## Testing Markdown Examples

The script `scripts/test_markdown_examples.py` extracts and runs code blocks from markdown files.

### How it works

1. Finds all `.md` files in `src/`
2. Extracts fenced code blocks (```bash or ```python)
3. Simulates test BAM files using `pynanalogue`
4. Runs each code block and verifies it exits successfully

### Running locally

```bash
python scripts/test_markdown_examples.py
```

Options:
- `-v, --verbose` - Show output from tests
- Pass specific files as arguments to test only those files

### Writing testable examples

- Use `input.bam` or `aligned_reads.bam` as placeholder filenames - these are automatically substituted with test data
- Ensure `nanalogue` is installed and available in PATH (via `cargo install nanalogue`)
- Code blocks that look like output (starting with `#contig`, read IDs, etc.) are automatically skipped

## Auto-Generated Output Sections

The script `scripts/generate_markdown_outputs.py` keeps example output in sync with actual command output.

### How it works

1. Finds markers in markdown files:
   ```markdown
   <!-- AUTO-GENERATED:START -->
   content here will be replaced
   <!-- AUTO-GENERATED:END -->
   ```
2. Looks at the bash code block immediately before the marker
3. Runs the command with simulated test data
4. Replaces the content between markers with actual output (truncated to 5 lines)

### Running locally

```bash
python scripts/generate_markdown_outputs.py
```

Options:
- `-n, --dry-run` - Show what would be done without making changes
- `-v, --verbose` - Verbose output

### Adding auto-generated sections

To add a new auto-generated output section:

1. Write your bash code block:
   ````markdown
   ```bash
   nanalogue window-dens --win 10 --step 5 input.bam
   ```
   ````

2. Add the markers below it:
   ````markdown
   **Example output:**
   <!-- AUTO-GENERATED:START -->
   ```
   placeholder content
   ```
   <!-- AUTO-GENERATED:END -->
   ````

3. Run the script to populate the output:
   ```bash
   python scripts/generate_markdown_outputs.py
   ```

## Link Checking

The repository uses `mdbook-linkcheck` to validate all links during the build.

### Configuration

In `book.toml`:
```toml
[output.linkcheck]
warning-policy = "error"
```

This treats broken links as errors, failing the build.

### Running locally

```bash
cargo install mdbook-linkcheck
mdbook build
```

## GitHub Workflow

All of these run automatically in `.github/workflows/main.yml` on push to `main`:

1. Install dependencies (nanalogue, pynanalogue, samtools, jq)
2. Run `test_markdown_examples.py` - fails build if examples don't work
3. Run `generate_markdown_outputs.py` - updates auto-generated sections
4. Run `mdbook build` with linkcheck - fails build if links are broken
5. Deploy to S3

## Dependencies

The automation scripts require:
- Python 3.11+
- `pynanalogue` - for simulating test BAM files
- `nanalogue` CLI - the tool being documented
- `samtools` - used in some examples
- `jq` - used in some examples
