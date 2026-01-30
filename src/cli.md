# Command line usage of nanalogue

## Tutorials

The following tutorials demonstrate common workflows with nanalogue:

- [Quick look at your data](./cli/quick_look_at_your_data.md) — Initial inspection of BAM files to see contigs and modification types
- [Quality control of mod data](./cli/qc_modification_data.md) — Assess modification call quality and apply filters
- [Extract raw mod calls](./cli/extract_raw_mod_data.md) — Get raw modification data from BAM files
- [Extracting sequences](./cli/extracting_sequences.md) — Display read sequences with indel and modification highlighting
- [Finding highly modified reads](./cli/finding_highly_modified_reads.md) — Filter reads by modification level
- [Exploring modification gradients](./cli/exploring_modification_gradients.md) — Detect directional patterns in modification data
- [Region-specific analysis](./cli/region_specific_analysis.md) — Focus analysis on specific genomic regions
- [Recipes](./cli/recipes.md) — Quick copy-paste snippets for common tasks

For detailed documentation of all CLI commands and options, see the [CLI Commands Reference](./all_cli_commands.md).

The CLI Commands Reference is automatically generated from the latest version of the `nanalogue` package and provides comprehensive help text for all commands and subcommands.

## Common options

Most if not all CLI commands have options to filter by:
- minimum sequence or alignment length
- alignment quality
- alignment type (primary/secondary/supplementary/unmapped)
- read ids
- mod quality
- base quality

You can also perform subsampling, trim by read ends etc.
Please see the CLI commands reference shown above.
