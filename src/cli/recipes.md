# Recipes

Quick, copy-paste snippets for common nanalogue tasks. For detailed explanations, see the linked tutorials.

> **Tip:** Most filtering options (such as `--mapq-filter`, `--min-align-len`, `--mod-prob-filter`) are shared across subcommands. You can combine the filters shown below with almost any nanalogue command.

---

## Quick Inspection

### Peek at BAM contents

```bash
nanalogue peek input.bam
```

Shows contigs, lengths, and modification types. [More info](./quick_look_at_your_data.md)

### Get read statistics

```bash
nanalogue read-stats input.bam
```

### Count reads with a specific modification

```bash
nanalogue read-table-show-mods --tag m input.bam | wc -l
```

---

## Filtering Reads

### Get read IDs above a methylation threshold

```bash
nanalogue find-modified-reads any-dens-above \
    --win 10 --step 5 --tag m --high 0.8 \
    input.bam
```

[More info](./finding_highly_modified_reads.md)

### Filter by mapping quality

```bash
nanalogue read-stats --mapq-filter 20 input.bam
```

### Filter by alignment length

```bash
nanalogue read-stats --min-align-len 1000 input.bam
```

### Subsample for quick exploration

```bash
nanalogue read-stats -s 0.1 input.bam
```

Analyzes ~10% of reads.

### Keep only primary alignments

```bash
nanalogue read-stats --read-filter primary_forward,primary_reverse input.bam
```

---

## Extracting Data

### Export windowed densities to TSV

```bash
nanalogue window-dens --win 10 --step 5 input.bam > densities.tsv
```

### Export windowed gradients to TSV

```bash
nanalogue window-grad --win 10 --step 5 input.bam > gradients.tsv
```

### Export raw modification probabilities

```bash
nanalogue read-info --detailed input.bam | jq '.[].mod_table[].data[][2]'
```

Values are 0-255 (rescaled from 0-100% probability). [More info](./qc_modification_data.md)

### Get per-read modification counts

```bash
nanalogue read-table-show-mods --tag m input.bam
```

### Export detailed read info as JSON

```bash
nanalogue read-info --detailed-pretty input.bam > reads.json
```

---

## Region Queries

### Analyze a specific gene

<!--REPLACE_CHR1_WITH_CONTIG_00001:START-->
```bash
nanalogue window-dens --win 10 --step 5 \
    --region chr1:100-200 \
    input.bam
```
<!--REPLACE_CHR1_WITH_CONTIG_00001:END-->

[More info](./region_specific_analysis.md)

### Analyze from a remote URL

```bash
nanalogue window-dens --win 10 --step 5 \
    --region chr17:43044295-43170245 \
    https://example.com/sample.bam
```

Always use `--region` with remote files to avoid downloading the entire BAM.

### Only count modifications within a region

<!--REPLACE_CHR1_WITH_CONTIG_00001:START-->
```bash
nanalogue window-dens --win 10 --step 5 \
    --mod-region chr1:100-200 \
    input.bam
```
<!--REPLACE_CHR1_WITH_CONTIG_00001:END-->

### Require reads to span the full region

<!--REPLACE_CHR1_WITH_CONTIG_00001:START-->
```bash
nanalogue window-dens --win 10 --step 5 \
    --region chr1:100-200 \
    --full-region \
    input.bam
```
<!--REPLACE_CHR1_WITH_CONTIG_00001:END-->

---

## Quality Filtering

### Remove low-confidence modification calls

```bash
nanalogue window-dens --win 10 --step 5 \
    --mod-prob-filter 0.3,0.7 \
    input.bam
```

Excludes calls with probability between 0.3 and 0.7. [More info](./qc_modification_data.md)

### Filter by base quality

```bash
nanalogue window-dens --win 10 --step 5 \
    --base-qual-filter-mod 20 \
    input.bam
```

### Trim read ends before analysis

```bash
nanalogue window-dens --win 10 --step 5 \
    --trim-read-ends-mod 50 \
    input.bam
```

Ignores the first and last 50 bp of each read.

### Exclude poorly mapped reads

```bash
nanalogue window-dens --win 10 --step 5 \
    --mapq-filter 20 \
    input.bam
```

---

## Piping with Other Tools

### Extract highly modified reads to a new BAM

```bash
nanalogue find-modified-reads any-dens-above \
    --win 10 --step 5 --tag m --high 0.8 \
    input.bam > high_meth_reads.txt

samtools view -h -b -N high_meth_reads.txt -o high_meth.bam input.bam
samtools index high_meth.bam
```

### Pipe from samtools view

```bash
samtools view -h input.bam chr17 | nanalogue read-stats -
```

Always include `-h` to pass the header.

### Analyze specific reads by ID

```bash
# Using high_meth_reads.txt created in the previous section
nanalogue window-dens --win 10 --step 5 \
    --read-id-list high_meth_reads.txt \
    input.bam
```

### Count modifications per chromosome

```bash
for chr in chr1 chr2 chr3; do
    echo -n "$chr: "
    nanalogue read-table-show-mods --tag m --region $chr input.bam | wc -l
done
```

---

## Modification-Specific Queries

### Filter by modification strand

```bash
nanalogue window-dens --win 10 --step 5 \
    --mod-strand bc \
    input.bam
```

Use `bc` for basecalled strand, `bc_comp` for complement.

### Analyze specific modification type

```bash
nanalogue window-dens --win 10 --step 5 \
    --tag m \
    input.bam
```

Common tags: `m` (5mC), `h` (5hmC), `a` (6mA).

---

## See Also

- [Quick look at your data](./quick_look_at_your_data.md)
- [Quality control of mod data](./qc_modification_data.md)
- [Finding highly modified reads](./finding_highly_modified_reads.md)
- [Exploring modification gradients](./exploring_modification_gradients.md)
- [Region-specific analysis](./region_specific_analysis.md)
- [CLI Reference](../cli.md)
