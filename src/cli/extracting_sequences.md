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
# mod-unmod threshold is 0.5
read_id	align_length	sequence_length_template	alignment_type	mod_count	sequence
0.e0e13cbf-76aa-4b82-a79e-25361bb3cd54	225	225	secondary_reverse	m:30	TACGCTCTTCTTTGTGGATTTCATCTGTA
0.a01acfba-ed78-4a1a-a769-456f5bbb3651	373	373	secondary_reverse	m:57	TAAGGGGTACGTACGCTCTTCTTTGTGGATTTCATCTGTA
0.66b20896-3557-4a0e-b3bc-80a9b8e7a73d	399	399	supplementary_forward	m:65	TAAGGGGTACGTACGCTCTTCTTTGTGGATTTCATCTGTA
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
# mod-unmod threshold is 0.5
read_id	align_length	sequence_length_template	alignment_type	mod_count	sequence
0.66b20896-3557-4a0e-b3bc-80a9b8e7a73d	399	399	supplementary_forward	m:65	TAAGGGGTACGTACGCTCTTCTTTGTGGATTTCATCTGTA
0.a01acfba-ed78-4a1a-a769-456f5bbb3651	373	373	secondary_reverse	m:57	TAAGGGGTACGTACGCTCTTCTTTGTGGATTTCATCTGTA
0.7b86eac7-c04b-4f78-8829-02684b149fd9	329	329	supplementary_reverse	m:45	TAAGGGGTACGTACGCTCTTCTTTGTGGATTTCATCTGTA
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
# mod-unmod threshold is 0.5
read_id	align_length	sequence_length_template	alignment_type	mod_count	sequence
0.4a978055-5d60-4040-a116-3440b5e8e720	200	194	supplementary_reverse	m:25	TCAAACGGTA..........aaaaGATGGGACACGGATTTGCTA
0.41e77be9-d738-4cf9-ba33-a5b6d0e786c7	200	194	supplementary_forward	m:28	TCAAACGGTA..........aaaaGATGGGACACGGATTTGCTA
0.fd8cf189-6b8e-45fd-9ec8-5d4221abd07c	200	194	primary_forward	m:28	TCAAACGGTA..........aaaaGATGGGACACGGATTTGCTA
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
# mod-unmod threshold is 0.5
read_id	align_length	sequence_length_template	alignment_type	mod_count	sequence
0.d994b056-5ec5-434c-8196-0372b5b62868	200	194	secondary_reverse	m:25	TCAAACGGTA..........AAAAGATGGGACACGGATTTGCTA
0.41e77be9-d738-4cf9-ba33-a5b6d0e786c7	200	194	supplementary_forward	m:28	TCAAACGGTA..........AAAAGATGGGACACGGATTTGCTA
0.42835575-9f68-4b1e-a804-a131a2a32a1f	200	194	primary_reverse	m:25	TCAAACGGTA..........AAAAGATGGGACACGGATTTGCTA
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
# mod-unmod threshold is 0.5
read_id	align_length	sequence_length_template	alignment_type	mod_count	sequence
0.a01acfba-ed78-4a1a-a769-456f5bbb3651	373	373	secondary_reverse	m:57	TAAZZZZTACGTACGCTCTTCTTTGTZZATTTCATCTZTA
0.7b86eac7-c04b-4f78-8829-02684b149fd9	329	329	supplementary_reverse	m:45	TAAGZZZTACZTACZCTCTTCTTTGTGGATTTCATCTZTA
0.66b20896-3557-4a0e-b3bc-80a9b8e7a73d	399	399	supplementary_forward	m:65	TAAGGGGTAZGTAZGZTZTTZTTTGTGGATTTCATCTGTA
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
# mod-unmod threshold is 0.5
read_id	align_length	sequence_length_template	alignment_type	mod_count	sequence
0.7b86eac7-c04b-4f78-8829-02684b149fd9	329	329	supplementary_reverse	m:45	TAAGZZZTACZTACZCTCTTCTTTGTGGATTTCATCTZTA
0.a01acfba-ed78-4a1a-a769-456f5bbb3651	373	373	secondary_reverse	m:57	TAAZZZZTACGTACGCTCTTCTTTGTZZATTTCATCTZTA
0.66b20896-3557-4a0e-b3bc-80a9b8e7a73d	399	399	supplementary_forward	m:65	TAAGGGGTAZGTAZGZTZTTZTTTGTGGATTTCATCTGTA
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
# mod-unmod threshold is 0.5
read_id	align_length	sequence_length_template	alignment_type	mod_count	sequence	qualities
0.41e77be9-d738-4cf9-ba33-a5b6d0e786c7	200	194	supplementary_forward	m:28	TCAAACGGTA..........aaaaGATGGGACAZGGATTTGZTA	25.24.33.30.22.34.34.23.29.22.255.255.255.255.255.255.255.255.255.255.38.35.21.39.29.29.34.35.34.30.38.31.33.24.40.24.35.40.33.26.35.37.28.37
0.fd8cf189-6b8e-45fd-9ec8-5d4221abd07c	200	194	primary_forward	m:28	TCAAACGGTA..........aaaaGATGGGACAZGGATTTGZTA	39.38.25.33.23.30.40.32.34.33.255.255.255.255.255.255.255.255.255.255.30.37.22.24.35.26.28.33.38.20.23.29.25.38.33.22.38.40.36.38.25.39.21.35
0.d994b056-5ec5-434c-8196-0372b5b62868	200	194	secondary_reverse	m:25	TCAAACZZTA..........aaaaZATZGGACACGZATTTZCTA	22.39.36.34.26.28.27.38.40.23.255.255.255.255.255.255.255.255.255.255.38.37.29.34.22.32.29.20.37.30.38.25.23.30.29.36.40.37.24.39.26.37.29.22
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
read_id	align_length	sequence_length_template	alignment_type	sequence
0.fd8cf189-6b8e-45fd-9ec8-5d4221abd07c	200	194	primary_forward	TCAAACGGTA..........aaaaGATGGGACACGGATTTGCTA
0.41e77be9-d738-4cf9-ba33-a5b6d0e786c7	200	194	supplementary_forward	TCAAACGGTA..........aaaaGATGGGACACGGATTTGCTA
0.d994b056-5ec5-434c-8196-0372b5b62868	200	194	secondary_reverse	TCAAACGGTA..........aaaaGATGGGACACGGATTTGCTA
0.4a978055-5d60-4040-a116-3440b5e8e720	200	194	supplementary_reverse	TCAAACGGTA..........aaaaGATGGGACACGGATTTGCTA
...
```
<!-- AUTO-GENERATED:END -->

## Creating Test Data with Indels (Advanced)

> **Advanced:** This section is for users who want to create their own test BAM files. You can skip this if you're working with real data.

You can create your own BAM files with insertions, deletions, and modifications using `nanalogue_sim_bam`. This is useful for testing and learning.

Create a JSON configuration file and run the simulation:

```bash
cat > config.json << 'EOF'
{
  "contigs": {
    "number": 3,
    "len_range": [200, 200]
  },
  "reads": [
    {
      "number": 30,
      "mapq_range": [20, 60],
      "base_qual_range": [20, 40],
      "len_range": [1.0, 1.0],
      "delete": [0.4, 0.5],
      "insert": "AAAA",
      "mods": [{
        "base": "C",
        "is_strand_plus": true,
        "mod_code": "m",
        "win": [5, 3],
        "mod_range": [[0.7, 1.0], [0.1, 0.4]]
      }]
    }
  ]
}
EOF
nanalogue_sim_bam config.json output.bam output.fasta
```

This configuration creates:
- 3 contigs of exactly 200bp each
- 30 reads spanning the full contig length
- A deletion in positions 40%-50% of each read
- A 4bp insertion ("AAAA")
- 5-methylcytosine modifications

## Next Steps

- [Quality control of mod data](./qc_modification_data.md) — Assess modification call quality
- [Extract raw mod calls](./extract_raw_mod_data.md) — Get detailed modification data
- [Finding highly modified reads](./finding_highly_modified_reads.md) — Filter reads by modification level

## See Also

- [Quick look at your data](./quick_look_at_your_data.md) — Initial data inspection
- [CLI Reference](../cli.md) — Full documentation of all nanalogue commands
- [Recipes](./recipes.md) — Quick copy-paste snippets
