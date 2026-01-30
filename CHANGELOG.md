# Changelog

All notable changes to this project will be documented in this file.

## 2026-01-30

* adds "Extracting sequences" tutorial covering sequence display with indel and modification highlighting
* refactors test data creation into shared `scripts/test_data.py` module
* adds indel test data configuration for testing insertion/deletion examples
* consolidates generated test outputs into `outputs/` directory
* adds tip about shared filtering options to recipes page
* renames "QC your modification data" to "Quality control of mod data" for clarity
* adds table of contents with anchor links under Installation section
* adds CLI tutorials summary section in cli.md with links to all tutorial pages
* reorders CLI sidebar so CLI Commands Reference appears at the bottom
* adds REPLACE tag functionality for testing: documentation shows user-friendly region names (chr1) while tests automatically substitute test data contig names (contig_00001)
* updates all region-specific examples to use chr1 instead of contig_00001

## 2026-01-29

* adds 5 new CLI tutorials: quick data inspection, QC workflow, modification gradients, region-specific analysis, and recipes
* adds `AUTO-GENERATED-FULL` marker support for full output (no truncation) in documentation
* adds install script instructions to introduction
* improves test script with gitignore filtering and better output file substitution
* adds matplotlib dependency to GitHub workflow
* expands .gitignore with patterns for AI files and generated test outputs

## 2026-01-25

* adds "Finding highly modified reads" documentation page
* adds automated testing of markdown code examples (`scripts/test_markdown_examples.py`)
* adds auto-generation of example output in markdown (`scripts/generate_markdown_outputs.py`)
* adds mdbook-linkcheck for validating links during build
* updates GitHub workflow with samtools, jq dependencies and new automation scripts
* updates installation instructions in introduction.md with latest from nanalogue README
* adds INSTRUCTIONS.md for contributors

## 2026-01-15

* adds extract raw mod calls
* adds common options
* adds links to intro and organizes it a bit better
