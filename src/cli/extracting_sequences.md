# Extracting Sequences

Nanalogue can extract and display read sequences from BAM files with highlighting for insertions, deletions, and modifications.
This is useful for inspecting alignment quality and understanding modification patterns at the sequence level.

## Quick Reference

| Flag | Effect |
|------|--------|
| `--region <REGION>` | Only include reads passing through the given region |
| `--full-region` | Only include reads that pass through the given region in full |
| `--seq-region <REGION>` | Display sequences from a specific genomic region |
| `--seq-full` | Display the entire basecalled sequence |
| `--show-ins-lowercase` | Show insertions as lowercase letters |
| `--show-mod-z` | Show modified bases as `Z` (or `z` for modified insertions) |
| `--show-base-qual` | Show basecalling quality scores |

Regions are written in the common genomics notation of `contig:start-end` e.g. `chr1:50-100`.
We use 0-based coordinates that are half open i.e. in the example above,
we are including all bases from the 51st base of chr1 to the 100th base.

**Display conventions:**
- Insertions: lowercase letters (with `--show-ins-lowercase`)
- Deletions: shown as periods (`.`)
- Modifications: shown as `Z` or `z` (with `--show-mod-z`)
- Quality at deleted positions: `255`

## Prerequisites

You will need:
- A BAM file with modification tags (`MM` and `ML` tags)
- [Nanalogue installed](../introduction.md#installation)
- For indel examples: a BAM file with insertions and/or deletions

> **Note:** The contig names `contig_00001`, etc. are example names used throughout this guide. In real BAM files aligned to a reference genome, you will see names like `chr1`, `chr2`, `NC_000001.11`, or similar depending on your reference.

## Basic Sequence Extraction

To extract sequences from a specific region, use `--seq-region`:

```bash
nanalogue read-table-show-mods --tag m --region contig_00001:80-120 \
    --seq-region contig_00001:80-120 input.bam
```

**Example output:**
<!-- AUTO-GENERATED:START -->
```
...
```
<!-- AUTO-GENERATED:END -->

In the above example, you may see sequences of varying length.
This is because not all the reads will pass through the given region in full.
To only include such reads and thus ensure more uniformity, you can use `--full-region` as shown below.

```bash
nanalogue read-table-show-mods --tag m --region contig_00001:80-120 \
    --seq-region contig_00001:80-120 --full-region input.bam
```

**Example output:**
<!-- AUTO-GENERATED:START -->
```
...
```
<!-- AUTO-GENERATED:END -->

## Inspecting Alignment Quality

### Viewing Insertions

Insertions relative to the reference can be highlighted as lowercase letters using `--show-ins-lowercase`.
We demonstrate usage using a file with indels in it.

```bash
nanalogue read-table-show-mods --tag m --region contig_00001:80-120 \
    --seq-region contig_00001:80-120 --show-ins-lowercase input_indels.bam
```

**Example output:**
<!-- AUTO-GENERATED:START -->
```
...
```
<!-- AUTO-GENERATED:END -->

In the output, lowercase letters indicate bases that are insertions (present in the read but not in the reference).

### Viewing Deletions

Deletions are automatically shown as periods (`.`) when displaying sequences from a region.
We demonstrate usage using a file with indels in it.

```bash
nanalogue read-table-show-mods --tag m --region contig_00001:80-120 \
    --seq-region contig_00001:80-120 input_indels.bam
```

**Example output:**
<!-- AUTO-GENERATED:START -->
```
...
```
<!-- AUTO-GENERATED:END -->

Each period represents a position where the reference has a base but the read does not.

## Viewing Modification Patterns

To mark modified bases in the sequence, use `--show-mod-z`:

```bash
nanalogue read-table-show-mods --tag m --region contig_00001:80-120 \
    --seq-region contig_00001:80-120 --show-mod-z input.bam
```

**Example output:**
<!-- AUTO-GENERATED:START -->
```
...
```
<!-- AUTO-GENERATED:END -->

Modified bases are displayed as:
- `Z` for modified bases on the reference
- `z` for modified bases within an insertion (when combined with `--show-ins-lowercase`)

In the above example, you may see sequences of varying length.
This is because not all the reads will pass through the given region in full.
To only include such reads and thus ensure more uniformity, you can use `--full-region` as shown below.

```bash
nanalogue read-table-show-mods --tag m --region contig_00001:80-120 \
    --seq-region contig_00001:80-120 --show-mod-z --full-region input.bam
```

**Example output:**
<!-- AUTO-GENERATED:START -->
```
...
```
<!-- AUTO-GENERATED:END -->
## Combining Display Options

You can combine multiple flags to see insertions, deletions, modifications, and quality scores all at once.
We demonstrate usage using a file with indels in it.

```bash
nanalogue read-table-show-mods --tag m --region contig_00001:80-120 \
    --seq-region contig_00001:80-120 \
    --show-ins-lowercase --show-mod-z --show-base-qual \
    input_indels.bam
```

**Example output:**
<!-- AUTO-GENERATED:START -->
```
...
```
<!-- AUTO-GENERATED:END -->

This produces output with:
- Lowercase letters for insertions
- Periods for deletions
- `Z`/`z` for modifications
- Quality scores as period-separated integers (with `255` for deleted positions)

## When to Use read-table-hide-mods

The `read-table-hide-mods` command is a simpler alternative when you don't need modification information.
It supports the same sequence display options (`--seq-region`, `--seq-full`, `--show-ins-lowercase`, `--show-base-qual`)
but does not include `--show-mod-z` or modification-related filters.
We demonstrate usage using a file with indels in it.

Use `read-table-hide-mods` when:
- Your BAM file doesn't have modification data
- You only care about alignment quality (insertions/deletions)
- You want slightly faster processing by skipping modification parsing

```bash
nanalogue read-table-hide-mods --region contig_00001:80-120 \
    --seq-region contig_00001:80-120 --show-ins-lowercase input_indels.bam
```

**Example output:**
<!-- AUTO-GENERATED:START -->
```
...
```
<!-- AUTO-GENERATED:END -->

## Creating Test Data

To create your own BAM files with insertions, deletions, and modifications for testing, see [Test data with indels](../simulations/test_data_indels.md).

## Next Steps

- [Quality control of mod data](./qc_modification_data.md) — Assess modification call quality
- [Extract raw mod calls](./extract_raw_mod_data.md) — Get detailed modification data
- [Finding highly modified reads](./finding_highly_modified_reads.md) — Filter reads by modification level

## See Also

- [Quick look at your data](./quick_look_at_your_data.md) — Initial data inspection
- [CLI Reference](../cli.md) — Full documentation of all nanalogue commands
- [Recipes](./recipes.md) — Quick copy-paste snippets
