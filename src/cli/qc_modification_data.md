# Quality Control of Mod Data

Before diving into downstream analysis, it's important to assess whether your modification calls are trustworthy. This tutorial covers how to check modification call quality and apply filters to improve data reliability.

## Prerequisites

You will need:
- A BAM file with modification tags (`MM` and `ML` tags)
- [Nanalogue installed](../introduction.md#installation)
- `jq` for JSON processing (optional but recommended)

> **Note:** Most filtering options in nanalogue (such as `--mapq-filter`, `--min-align-len`, `--mod-prob-filter`) are shared across subcommands. The examples below show specific commands, but you can apply these filters to any nanalogue subcommand that accepts them.

## Understanding Modification Probabilities

Modification callers like Dorado output a probability for each potential modification site. These probabilities are stored in the `ML` tag as values from 0-255, which represent 0-100% probability of modification.

A **high-quality** dataset typically shows a **bimodal distribution**:
- Many values near 0 (confidently unmodified)
- Many values near 255 (confidently modified)
- Few values in the middle (uncertain calls)

A dataset with many values around 128 (50%) indicates the caller is uncertain, which may signal poor signal quality or an inappropriate basecalling model.

## Extracting Raw Modification Probabilities

To check your probability distribution, extract the raw values:

```bash
nanalogue read-info --detailed input.bam | jq '.[].mod_table[].data[][2]' | shuf | head -20
```

<!-- AUTO-GENERATED:START -->
```
35
97
239
36
223
...
```
<!-- AUTO-GENERATED:END -->

These values (0-255) can be plotted as a histogram. In Python:

```python
import subprocess
import matplotlib.pyplot as plt

# Extract probabilities
result = subprocess.run(
    ["bash", "-c", "nanalogue read-info --detailed input.bam | jq '.[].mod_table[].data[][2]'"],
    capture_output=True, text=True
)
probs = [int(x) for x in result.stdout.strip().split('\n') if x]

# Plot histogram
plt.hist(probs, bins=50, edgecolor='black')
plt.xlabel('Modification probability (0-255)')
plt.ylabel('Count')
plt.title('Modification call distribution')
plt.savefig('mod_distribution.png')
```

## Filtering Low-Confidence Calls

If you have many uncertain calls (probabilities near 128), you can filter them out using `--mod-prob-filter`:

```bash
nanalogue window-dens --win 10 --step 5 --mod-prob-filter 0.3,0.7 input.bam
```

This excludes modification calls where the probability falls between 0.3 and 0.7 (77-179 in 0-255 scale), keeping only confident calls.

**When to use this:**
- When you see a large peak around 128 in your probability histogram
- When you want to be conservative about modification calls
- For samples with lower signal quality

**When NOT to use this:**
- When your data already shows a clean bimodal distribution
- When you're studying intermediate modification states

## Base Quality Filtering

Poor basecalling quality can affect modification calls. Use `--base-qual-filter-mod` to exclude positions with low basecall confidence:

```bash
nanalogue window-dens --win 10 --step 5 --base-qual-filter-mod 20 input.bam
```

This excludes modification calls at positions where the basecall quality is below 20 (Phred scale).

## Read-Level Quality Filters

### Mapping Quality

Poorly mapped reads may have incorrect modification positions. Filter by MAPQ:

```bash
nanalogue read-stats --mapq-filter 20 input.bam
```

### Alignment Length

Short alignments may not provide enough context for reliable modification calls:

```bash
nanalogue read-stats --min-align-len 500 input.bam
```

### Quick Subsampling

For large files, quickly check a subset using `-s`:

```bash
nanalogue read-stats -s 0.1 input.bam
```

This analyzes approximately 10% of reads, useful for rapid QC checks.

## Expected vs Observed: Sanity Checks

If you have positive or negative controls, verify your data matches expectations.

### Check Overall Modification Levels

Use `window-dens` on a region you expect to be highly modified:

<!--REPLACE_CHR1_WITH_CONTIG_00001:START-->
```bash
nanalogue window-dens --win 20 --step 10 --region chr1:100-200 input.bam
```
<!--REPLACE_CHR1_WITH_CONTIG_00001:END-->

If your positive control region shows low modification, investigate:
- Was the correct basecaller model used?
- Is the sample truly modified?
- Are there alignment issues in this region?

### Compare Modification Counts

Use `read-table-show-mods` to see per-read modification statistics:

```bash
nanalogue read-table-show-mods --tag m input.bam | head -10
```

<!-- AUTO-GENERATED:START -->
```
# mod-unmod threshold is 0.5
read_id	align_length	sequence_length_template	alignment_type	mod_count
0.04723b11-aa9e-4eeb-bc70-8bd6d1dfa695	433	433	secondary_reverse	m:68
0.0dad9522-6c26-4c1d-bc15-a7d5c745e103	231	231	secondary_reverse	m:38
0.ca7dd878-a63a-499b-a3d0-29c588f70800	188	188	supplementary_forward	m:33
...
```
<!-- AUTO-GENERATED:END -->

## QC Checklist

Before proceeding with analysis, verify:

- [ ] **Probability distribution is bimodal** — Use `read-info --detailed` + histogram
- [ ] **Modification types detected** — Use `peek` to confirm expected mod codes
- [ ] **Sufficient read depth** — Use `read-stats` to check alignment counts
- [ ] **Reasonable modification levels** — Compare to expected values for your sample
- [ ] **No systematic issues** — Check if problems are genome-wide or region-specific

## Next Steps

Once your data passes QC:
- [Find highly modified reads](./finding_highly_modified_reads.md) — Filter reads by modification level
- [Explore modification gradients](./exploring_modification_gradients.md) — Detect directional patterns
- [Analyze specific regions](./region_specific_analysis.md) — Focus on genes or features

## See Also

- [Quick look at your data](./quick_look_at_your_data.md) — Initial data inspection
- [CLI Reference](../cli.md) — Full documentation of all nanalogue commands
- [Recipes](./recipes.md) — Quick copy-paste snippets
