# Exploring Modification Gradients

While modification density tells you *how much* of a region is modified, modification gradients tell you *where modifications change* and in *what direction*. Gradients are particularly powerful for detecting transitions, boundaries, and directional patterns in single-molecule data.

## Prerequisites

You will need:
- A BAM file with modification tags (`MM` and `ML` tags)
- [Nanalogue installed](../introduction.md#installation)

## What Are Modification Gradients?

A **gradient** measures the rate of change in modification level along a read. Consider a read where:
- The first half has 80% modification
- The second half has 20% modification

The **density** would average these together (~50%), obscuring the pattern. The **gradient** would show a strong negative value at the transition point, revealing that modification *decreases* as you move along the read.

### Key insight

Gradients reveal **directionality**:
- **Positive gradient**: Modification increasing along the read
- **Negative gradient**: Modification decreasing along the read
- **Near-zero gradient**: Stable modification level (no change)

## The `window-grad` Command

The `window-grad` command computes modification gradients over sliding windows:

```bash
nanalogue window-grad --win 10 --step 5 input.bam
```

<!-- AUTO-GENERATED:START -->
```
#contig	ref_win_start	ref_win_end	read_id	win_val	strand	base	mod_strand	mod_type	win_start	win_end	basecall_qual
contig_00000	23	68	0.8d55bcf0-eb75-4fad-aac4-b6aac8c23aae	-0.054545455	+	C	+	m	6	51	26
contig_00000	54	93	0.8d55bcf0-eb75-4fad-aac4-b6aac8c23aae	0.030303031	+	C	+	m	37	76	26
contig_00000	78	112	0.8d55bcf0-eb75-4fad-aac4-b6aac8c23aae	0.018181818	+	C	+	m	61	95	27
contig_00000	95	122	0.8d55bcf0-eb75-4fad-aac4-b6aac8c23aae	-0.036363635	+	C	+	m	78	105	26
...
```
<!-- AUTO-GENERATED:END -->

### Understanding the Output

| Column | Description |
|--------|-------------|
| `contig` | Reference contig name |
| `ref_win_start`, `ref_win_end` | Window coordinates on the reference |
| `read_id` | Unique read identifier |
| `win_val` | **The gradient value** (key column) |
| `strand` | Alignment strand (+/-) |
| `base`, `mod_strand`, `mod_type` | Modification details |
| `win_start`, `win_end` | Window coordinates on the read |
| `basecall_qual` | Average basecall quality in the window |

### Required Parameters

- `--win`: Window size in number of modified bases (e.g., 10 cytosines per window)
- `--step`: How many bases to slide the window by

## Interpreting Gradient Values

The gradient value (`win_val`) indicates the direction and magnitude of modification change.
The representative values shown below are for illustrative purposes only --
the gradient value may depend on the size of the window and step chosen.

| Gradient | Meaning | Example |
|----------|---------|---------|
| `+0.05` to `+0.2` | Modification increasing | Entering a modified region |
| `-0.05` to `-0.2` | Modification decreasing | Leaving a modified region |
| `-0.02` to `+0.02` | Stable | Within a uniformly modified/unmodified region |
| `> +0.2` or `< -0.2` | Sharp transition | Boundary between distinct modification states |

## Practical Example: DNA Replication Fork Direction from BrdU

One powerful application of gradient analysis is determining DNA replication fork direction from BrdU (5-bromodeoxyuridine) incorporation data.

### Background

During DNA replication under appropriate experimental conditions:
- BrdU is incorporated into newly synthesized DNA
- Nanopore sequencing detects BrdU as a thymidine modification
- The direction of BrdU signal change along a molecule reveals which way the replication fork was traveling

### How Gradients Reveal Fork Direction

Let's say you have set up an experiment so that BrdU levels are high
at the start of the experiment and the level decrease over time.
Consider a single DNA molecule that was replicated by a fork moving left-to-right:
- The **left end** was replicated first → more BrdU
- The **right end** was replicated later → less BrdU
- This creates a **negative gradient** (BrdU decreasing left-to-right)

Conversely, a fork moving right-to-left would show a **positive gradient**.

If you have set up an experiment where BrdU levels are increasing over time,
then you will have the opposite sign of gradients to the scenario described
above.

### Finding Replication Pause Sites

When a replication fork pauses, the gradient pattern changes:
- Before the pause: consistent gradient direction
- At the pause site: gradient is much steeper as BrdU levels change over the duration of the pause
- After resumption: gradient direction may be consistent or change depending on how the pause was rescued

Use `window-grad` to identify reads with gradient transitions:

```bash
nanalogue window-grad --win 20 --step 10 input.bam > gradients.tsv
```

Then analyze in Python/R to find reads where the gradient sign changes, indicating potential pause or termination sites.

### Further Reading

For a comprehensive study of DNA replication pausing using this approach, see:
- [Thiyagarajan et al., "Single-molecule landscape of DNA replication pausing" (bioRxiv)](https://www.biorxiv.org/content/10.1101/2025.08.14.670160v1)

## When to Use Gradients vs Densities

| Use Case | Tool | Why |
|----------|------|-----|
| "How modified is this region?" | `window-dens` | Density gives the average level |
| "Where do modification patterns change?" | `window-grad` | Gradient detects transitions |
| "What direction was this process moving?" | `window-grad` | Sign reveals directionality |
| "Find highly modified reads" | `find-modified-reads` | Filters by density threshold |
| "Find reads with modification boundaries" | `window-grad` + custom analysis | Gradient changes indicate boundaries |

## Combining Gradients with Other Filters

Apply the same quality filters as other nanalogue commands:

```bash
# Filter by mapping quality and base quality
nanalogue window-grad --win 10 --step 5 \
    --mapq-filter 20 \
    --base-qual-filter-mod 20 \
    input.bam
```

<!--REPLACE_CHR1_WITH_CONTIG_00001:START-->
```bash
# Focus on a specific region
nanalogue window-grad --win 10 --step 5 \
    --region chr1:100-200 \
    input.bam
```
<!--REPLACE_CHR1_WITH_CONTIG_00001:END-->

## Next Steps

- [Region-specific analysis](./region_specific_analysis.md) — Focus gradient analysis on specific genes
- [Finding highly modified reads](./finding_highly_modified_reads.md) — Combine with density-based filtering
- [Recipes](./recipes.md) — Quick copy-paste snippets

## See Also

- [Quality control of mod data](./qc_modification_data.md) — Ensure data quality before gradient analysis
- [CLI Reference](../cli.md) — Full documentation of all nanalogue commands
