# Quick Look at Your Data

After basecalling with a tool like Dorado, your first question is usually: "What's in my BAM file?" Nanalogue provides two commands for quickly inspecting your data before diving into detailed analysis.

## Prerequisites

You will need:
- A BAM file with modification tags (`MM` and `ML` tags), typically produced by a basecaller like Dorado
- [Nanalogue installed](../introduction.md#installation)

## The `peek` Command

The `peek` command gives you a quick overview of your BAM file by examining the header and first 100 records:

```bash
nanalogue peek input.bam
```

**Example output:**
<!-- AUTO-GENERATED-FULL:START -->
```
contigs_and_lengths:
contig_00000	682
contig_00001	509
contig_00002	543

modifications:
C+m
```
<!-- AUTO-GENERATED-FULL:END -->

> **Note:** The contig names `contig_00000`, `contig_00001`, etc. are example names used here. In real BAM files aligned to a reference genome, you will see names like `chr1`, `chr2`, `NC_000001.11`, or similar depending on your reference.

This tells you:
- **Contigs**: The reference sequences in your BAM and their lengths
- **Modifications**: The modification types detected (e.g., `C+m` means 5-methylcytosine on the + strand)

### Common Modification Codes

| Code | Modification |
|------|-------------|
| `C+m` | 5-methylcytosine (5mC) |
| `C+h` | 5-hydroxymethylcytosine (5hmC) |
| `A+a` | N6-methyladenine (6mA) |
| `T+472552` | BrdU (5-bromodeoxyuridine). Older BAM files may use `T+T` (generic thymidine modification) or `T+B` |

## The `read-stats` Command

For a more detailed summary of your reads, use `read-stats`:

```bash
nanalogue read-stats input.bam
```

**Example output:**
<!-- AUTO-GENERATED-FULL:START -->
```
key	value
n_primary_alignments	8
n_secondary_alignments	8
n_supplementary_alignments	9
n_unmapped_reads	5
n_reversed_reads	12
align_len_mean	304
align_len_max	445
align_len_min	164
align_len_median	284
align_len_n50	329
seq_len_mean	315
seq_len_max	482
seq_len_min	164
seq_len_median	293
seq_len_n50	331
```
<!-- AUTO-GENERATED-FULL:END -->

This provides:
- **Alignment counts**: Primary, secondary, supplementary, and unmapped reads
- **Length statistics**: Mean, median, min, max, and N50 for both alignment and sequence lengths

## Troubleshooting: No Modifications Detected

If `peek` shows no modifications, check:

1. **Basecaller model**: Did you use a modification-aware model? For Dorado, models with `5mC` or `6mA` in the name produce modification calls.

2. **MM/ML tags present**: Check if your BAM has the required tags:
   ```bash
   samtools view input.bam | head -1 | grep -o "MM:Z:[^ ]*"
   ```
   If this returns nothing, your BAM lacks modification data.

3. **Correct reference**: For aligned BAMs, ensure reads actually align to the reference. A high unmapped count in `read-stats` suggests alignment issues.

## Quick Sanity Checks

Before detailed analysis, verify your data looks reasonable:

```bash
# Check you have enough reads
nanalogue read-stats input.bam | grep n_primary_alignments

# Verify modification types match your experiment
nanalogue peek input.bam | grep modifications
```

## Next Steps

Once you've confirmed your data looks correct:
- [Quality control of mod data](./qc_modification_data.md) — Assess modification call quality
- [Find highly modified reads](./finding_highly_modified_reads.md) — Filter reads by modification level
- [Explore a specific region](./region_specific_analysis.md) — Focus on genes or features of interest

## See Also

- [CLI Reference](../cli.md) — Full documentation of all nanalogue commands
- [Recipes](./recipes.md) — Quick copy-paste snippets for common tasks
