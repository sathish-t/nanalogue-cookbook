# Spotting Variants in Sequence Data

When inspecting aligned sequences, you may notice positions where some reads differ from others.
These could be sequencing errors (random, scattered) or real variants like SNPs (consistent, appearing in a subset of reads).
This tutorial shows how to use nanalogue's sequence visualization to spot these patterns visually.
We'll first see what random errors look like, then contrast with a cleaner variant pattern where only some reads carry the difference.

## Key Concept

When viewing many reads across a short region (10-20bp) with `--full-region`, all sequences align to the same length.
Random errors scatter across positions.
A real variant appears as a vertical column where a subset of reads consistently shows a different base.

## Prerequisites

You will need:
- A BAM file with modification tags (`MM` and `ML` tags)
- [Nanalogue installed](../introduction.md#installation)
- For this tutorial: test data with simulated mismatches (configurations provided below)

Please read the [Extracting sequences](./extracting_sequences.md) tutorial first, as this tutorial builds on those concepts.

> **Note:** The contig names `contig_00001`, etc. are example names used throughout this guide. In real BAM files aligned to a reference genome, you will see names like `chr1`, `chr2`, `NC_000001.11`, or similar depending on your reference.

## What Random Errors Look Like

First, let's see what data looks like when all reads have random mismatches scattered throughout.
This simulates sequencing errors or very noisy data.

```bash
nanalogue read-table-show-mods --tag m --region contig_00001:90-110 \
    --seq-region contig_00001:90-110 --full-region error_data.bam
```

**Example output:**
<!-- AUTO-GENERATED-FULL:START -->
```
...
```
<!-- AUTO-GENERATED-FULL:END -->

Notice how the mismatches are distributed randomly across positions.
No single column shows a consistent pattern.
If you were looking for a real variant, you wouldn't find a clear signal here - just noise.

## Spotting a Consistent Variant

Now let's look at data where only some reads have mismatches - simulating a heterozygous-like variant.
This test data has two groups of reads: one clean, one with mismatches.

```bash
nanalogue read-table-show-mods --tag m --region contig_00001:90-110 \
    --seq-region contig_00001:90-110 --full-region variant_data.bam
```

**Example output:**
<!-- AUTO-GENERATED-FULL:START -->
```
...
```
<!-- AUTO-GENERATED-FULL:END -->

Compare the read IDs to the sequences.
The reads with IDs starting with "1." carry mismatches while those starting with "0." are clean.

**Important:** This ID-based grouping exists only because we created the test data this way.
In real datasets, read IDs have no relationship to sequence features.
However, the visual pattern remains the same: a subset of reads consistently differing at certain positions.
That's the visual signature of a potential variant.

Unlike the random noise in the previous section, here we see structure.
This is closer to what a real heterozygous variant looks like - consistent differences in a subset of reads.

## Combining Variant and Modification Views

Add `--show-mod-z` to see modifications marked alongside the base differences:

```bash
nanalogue read-table-show-mods --tag m --region contig_00001:90-110 \
    --seq-region contig_00001:90-110 --full-region --show-mod-z variant_data.bam
```

**Example output:**
<!-- AUTO-GENERATED-FULL:START -->
```
...
```
<!-- AUTO-GENERATED-FULL:END -->

This combined view lets you inspect whether variants occur near modified bases.
In some biological contexts, SNPs can affect modification patterns - or a variant at a modified position might affect how the modification is called.
Visual inspection gives you a quick sanity check before deeper analysis.

**Note:** Modifications at variant positions may be less reliable since the basecaller's modification model may assume the reference base.

## Interpreting What You See

**Patterns to look for:**

- **Consistent column differences** in a subset of reads → potential variant worth investigating
- **Scattered differences** across positions → likely sequencing errors or very noisy data
- **Single read with many differences** → possible alignment issue or sample contamination

**Limitations:**

- Visual inspection works for quick exploration, not rigorous variant calling
- High coverage helps - with few reads, random errors can look like variants
- Short regions (10-20bp) work best for this approach; longer regions become hard to scan visually

**What to do next:**

For rigorous SNP detection and genotyping, use specialized variant calling tools.
Nanalogue's strength is quick visual inspection - useful for QC, sanity checks, or exploring specific regions of interest.

## Creating Test Data

To create your own test BAM files for this tutorial:

- [Test data with random errors](../simulations/test_data_errors.md) — All reads have scattered mismatches
- [Test data with variants](../simulations/test_data_variants.md) — Two read groups simulating heterozygous-like pattern

## Next Steps

- [Extracting sequences](./extracting_sequences.md) — More sequence display options
- [Quality control of mod data](./qc_modification_data.md) — Assess modification call quality
- [Finding highly modified reads](./finding_highly_modified_reads.md) — Filter reads by modification level

## See Also

- [Quick look at your data](./quick_look_at_your_data.md) — Initial data inspection
- [CLI Reference](../cli.md) — Full documentation of all nanalogue commands
- [Recipes](./recipes.md) — Quick copy-paste snippets
