# Region-Specific Analysis

Rather than analyzing an entire BAM file, you often want to focus on specific genomic regions — a gene, promoter, or feature of interest. Nanalogue provides several region filtering options that work with both local and remote BAM files.

## Prerequisites

You will need:
- A BAM file with modification tags (`MM` and `ML` tags)
- [Nanalogue installed](../introduction.md#installation)
- For indexed remote BAMs: the `.bai` index file must be accessible

## Why Focus on Regions?

Region-specific analysis is useful for:
- **Targeted analysis**: Focus on genes or features of biological interest
- **Performance**: Avoid processing multi-gigabyte files when you only need a small region
- **Comparison**: Compare modification patterns between different loci
- **Validation**: Check expected modification levels at control regions

## Region Filtering Options

Nanalogue provides three region-related parameters:

| Parameter | Effect |
|-----------|--------|
| `--region` | Keep reads that **overlap** the specified region |
| `--mod-region` | Only count modifications **within** the specified region |
| `--full-region` | Only keep reads that **span the entire** region |

### `--region`: Read Selection

The `--region` parameter selects reads that overlap a genomic region:

<!--REPLACE_CHR1_WITH_CONTIG_00001:START-->
```bash
nanalogue window-dens --win 10 --step 5 \
    --region chr1:100-200 \
    input.bam
```
<!--REPLACE_CHR1_WITH_CONTIG_00001:END-->

This keeps any read that overlaps the specified region. Reads may extend beyond the region boundaries.

### `--mod-region`: Modification Selection

The `--mod-region` parameter filters which modifications are counted:

<!--REPLACE_CHR1_WITH_CONTIG_00001:START-->
```bash
nanalogue window-dens --win 10 --step 5 \
    --mod-region chr1:100-200 \
    input.bam
```
<!--REPLACE_CHR1_WITH_CONTIG_00001:END-->

This processes all reads but only counts modifications that fall within the specified region.

### Combining `--region` and `--mod-region`

For the most focused analysis, use both:

<!--REPLACE_CHR1_WITH_CONTIG_00001:START-->
```bash
nanalogue window-dens --win 10 --step 5 \
    --region chr1:100-200 \
    --mod-region chr1:100-200 \
    input.bam
```
<!--REPLACE_CHR1_WITH_CONTIG_00001:END-->

This selects only reads overlapping the region AND only counts modifications within it.

### `--full-region`: Complete Coverage

Use `--full-region` when you need reads that span an entire feature:

<!--REPLACE_CHR1_WITH_CONTIG_00001:START-->
```bash
nanalogue window-dens --win 10 --step 5 \
    --region chr1:100-200 \
    --full-region \
    input.bam
```
<!--REPLACE_CHR1_WITH_CONTIG_00001:END-->

This is useful when you want to ensure complete coverage of a promoter or exon.

## Practical Example: BRCA1 Methylation from Public Data

Let's analyze CpG methylation at the BRCA1 gene using publicly available PacBio HiFi data.

### The Dataset

We'll use the HG002 (Genome in a Bottle) dataset with CpG methylation calls:

```
https://downloads.pacbcloud.com/public/dataset/HG002-CpG-methylation-202202/HG002.GRCh38.haplotagged.bam
```

### BRCA1 Coordinates

BRCA1 is located on chromosome 17:
- **Gene body**: chr17:43,044,295-43,170,245 (GRCh38)
- **Promoter region**: For the purposes of this tutorial, let's consider chr17:43,170,000-43,172,000 as the promoter region (the actual promoter boundaries may differ)

### Analyzing the BRCA1 Promoter

Check modification densities in the BRCA1 promoter region:

```bash
nanalogue window-dens --win 10 --step 5 \
    --region chr17:43170000-43172000 \
    https://downloads.pacbcloud.com/public/dataset/HG002-CpG-methylation-202202/HG002.GRCh38.haplotagged.bam
```

> **Note:** This streams data directly from the remote URL. Only the region of interest is downloaded, making this efficient even for large BAM files.

### Comparing Two Regions

You can compare modification patterns between regions by running separate queries:

```bash
# BRCA1 promoter
nanalogue window-dens --win 10 --step 5 \
    --region chr17:43170000-43172000 \
    https://downloads.pacbcloud.com/public/dataset/HG002-CpG-methylation-202202/HG002.GRCh38.haplotagged.bam \
    > brca1_promoter.tsv

# BRCA2 promoter (for tutorial, assume chr13:32,315,000-32,317,000)
nanalogue window-dens --win 10 --step 5 \
    --region chr13:32315000-32317000 \
    https://downloads.pacbcloud.com/public/dataset/HG002-CpG-methylation-202202/HG002.GRCh38.haplotagged.bam \
    > brca2_promoter.tsv
```

## Two-Pass Analysis with Read ID Lists

For complex analyses, use a two-pass approach:

### Pass 1: Find Interesting Reads

First, identify reads meeting your criteria:

<!--REPLACE_CHR1_WITH_CONTIG_00001:START-->
```bash
nanalogue find-modified-reads any-dens-above \
    --win 10 --step 5 --tag m --high 0.8 \
    --region chr1:100-200 \
    input.bam > high_meth_brca1_reads.txt
```
<!--REPLACE_CHR1_WITH_CONTIG_00001:END-->

### Pass 2: Detailed Analysis

Then analyze those specific reads in detail:

```bash
nanalogue window-dens --win 5 --step 2 \
    --read-id-list high_meth_brca1_reads.txt \
    input.bam > detailed_densities.tsv
```

This workflow lets you first filter for reads of interest, then perform fine-grained analysis on just those reads.

## Performance Tips

### Remote BAM Files

When working with remote URLs:
- **Always use `--region`** to avoid downloading the entire file
- Ensure the BAM is indexed (`.bai` file at the same URL location)
- Nanalogue streams only the required data

### Local BAM Files

For local files:
- Index your BAM with `samtools index` for faster region queries
- Without an index, nanalogue must scan the entire file

### Subsampling for Exploration

When exploring a new dataset, subsample first:

<!--REPLACE_CHR1_WITH_CONTIG_00001:START-->
```bash
nanalogue window-dens --win 10 --step 5 \
    --region chr1:100-200 \
    -s 0.1 \
    input.bam
```
<!--REPLACE_CHR1_WITH_CONTIG_00001:END-->

## Next Steps

- [Finding highly modified reads](./finding_highly_modified_reads.md) — Filter reads by modification level
- [Exploring modification gradients](./exploring_modification_gradients.md) — Detect directional patterns
- [Recipes](./recipes.md) — Quick copy-paste snippets

## See Also

- [Quick look at your data](./quick_look_at_your_data.md) — Initial data inspection
- [Quality control of mod data](./qc_modification_data.md) — Ensure data quality
- [CLI Reference](../cli.md) — Full documentation of all nanalogue commands
