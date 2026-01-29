# Finding Highly Modified Reads

A common task in single-molecule genomics with DNA/RNA modifications is to identify reads that are "highly modified" — for example, reads where a large fraction of CpG sites are methylated. This can be useful for:

- Identifying molecules from hypermethylated regions (e.g., imprinted loci, repeat elements)
- Quality control: checking if your sample has the expected modification levels
- Filtering reads for downstream analysis based on modification status
- Studying heterogeneity in modification patterns across single molecules

Nanalogue provides the `find-modified-reads` command for exactly this purpose.

## Prerequisites

You will need:
- A BAM file with modification tags (`MM` and `ML` tags), typically produced by a basecaller like Dorado
- [Nanalogue installed](../introduction.md#installation)

## The `find-modified-reads` Command

The `find-modified-reads` command outputs a list of read IDs that satisfy a specified criterion. To see available subcommands and options:

```bash
nanalogue find-modified-reads --help
```

### Finding Reads by Modification Density

The most common use case is finding reads where the modification density (the fraction of modified bases) exceeds a threshold. Use the `any-dens-above` subcommand:

```bash
nanalogue find-modified-reads any-dens-above \
    --win 10 \
    --step 5 \
    --tag m \
    --high 0.8 \
    input.bam
```

This outputs read IDs where at least one window has a modification density at or above 0.8 (80%). The required parameters are:
- `--win`: Window size in number of modified bases (e.g., 10 Cs per window)
- `--step`: How many bases to slide the window by
- `--tag`: The modification code to look for (e.g., `m` for 5mC)
- `--high`: The threshold value

**Example output:**
```
a4f36092-b4d5-47a9-813e-c22c3b477a0f
5d10eb9a-aae1-4db8-8ec6-7ebb34d32576
fffffff1-10d2-49cb-8ca3-e8d48979001a
```

### Understanding Windowed Analysis

Nanalogue computes modification density over sliding windows along each read. This windowed approach is important because:

1. A read might be partially modified (e.g., one end is methylated, the other is not)
2. Modification patterns often have biological meaning at specific scales
3. It allows you to detect local hotspots of modification

You can control the window size and step with additional parameters. Run `nanalogue find-modified-reads any-dens-above --help` for all available options.

## Practical Example: Finding Hypermethylated Reads

Suppose you have nanopore sequencing data from a human sample and want to find reads that are highly methylated at CpG sites. A typical workflow might look like:

```bash
# Step 1: Find read IDs with >=70% methylation in any window
nanalogue find-modified-reads any-dens-above \
    --win 10 \
    --step 5 \
    --tag m \
    --high 0.7 \
    aligned_reads.bam > hypermethylated_reads.txt

# Step 2: Count how many reads were found
wc -l hypermethylated_reads.txt

# Step 3: Extract these reads using samtools for further analysis
samtools view -h -b -N hypermethylated_reads.txt -o hypermethylated.bam aligned_reads.bam
samtools index hypermethylated.bam
```

## Exploring Modification Patterns with Windowed Densities

If you want to see the actual modification densities (not just filter reads), use the `window-dens` command:

```bash
nanalogue window-dens \
    --win 10 \
    --step 5 \
    input.bam > densities.tsv
```

**Example output:**
<!-- AUTO-GENERATED:START -->
```
#contig	ref_win_start	ref_win_end	read_id	win_val	strand	base	mod_strand	mod_type	win_start	win_end	basecall_qual
contig_00000	82	134	0.b55f2482-b935-4d11-8b03-4ea7d1c838a3	0.5	-	C	+	m	12	64	28
contig_00000	95	150	0.b55f2482-b935-4d11-8b03-4ea7d1c838a3	0.7	-	C	+	m	25	80	27
contig_00000	139	174	0.b55f2482-b935-4d11-8b03-4ea7d1c838a3	0.7	-	C	+	m	69	104	28
contig_00000	152	190	0.b55f2482-b935-4d11-8b03-4ea7d1c838a3	0.5	-	C	+	m	82	120	27
...
```
<!-- AUTO-GENERATED:END -->

This output can be loaded into Python/R for custom analysis and visualization.

## Tips

- **Choosing a threshold**: The appropriate threshold depends on your biological question. For CpG methylation in mammals, "highly methylated" often means >80% methylation. For other modifications or organisms, you may need to adjust.

- **Window size matters**: Smaller windows capture local patterns but are noisier. Larger windows give more stable estimates but may miss focal modifications.

- **Combine with region filtering**: Use the `--region` parameter to filter reads to a genomic region:
  ```bash
  # Replace contig_00001:100-200 with an actual region from your BAM file, e.g. chr1:1000-2000
  nanalogue find-modified-reads any-dens-above \
      --win 10 --step 5 --tag m --high 0.8 \
      --region contig_00001:100-200 \
      input.bam
  ```

- **Performance**: Nanalogue is written in Rust and designed to handle large BAM files efficiently. For very large files, you can process in parallel by splitting by chromosome.

## Next Steps

- Explore modification gradients with `window-grad`
- Create synthetic test data with `pynanalogue.simulate_mod_bam()` for benchmarking
- Visualize your results with tools like IGV or custom matplotlib plots

## See Also

- [CLI Reference](../cli.md) — Full documentation of all nanalogue commands
- [Python Library](../python.md) — Using pynanalogue for scripting
- [modkit](https://nanoporetech.github.io/modkit/) — Complementary tool for aggregated modification statistics
