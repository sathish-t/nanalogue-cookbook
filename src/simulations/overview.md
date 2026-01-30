# Simulating Test Data

Nanalogue includes `nanalogue_sim_bam`, a tool for creating synthetic BAM files with modifications.
This is useful for testing, learning, and benchmarking.

## Basic Usage

Create a JSON configuration file describing your desired data, then run:

```bash
nanalogue_sim_bam config.json output.bam output.fasta
```

This produces:
- A BAM file with simulated reads and modification tags
- A FASTA file with the reference contigs

## Configuration Structure

All configurations follow this basic structure:

```json
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
      "len_range": [0.3, 0.8],
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
```

### Contigs Section

| Field | Description |
|-------|-------------|
| `number` | Number of contigs to create |
| `len_range` | `[min, max]` length of contigs in bp |
| `repeated_seq` | Optional: repeat this sequence to build contig |

### Reads Section

Each entry in the `reads` array creates a group of reads. Multiple groups can have different properties.

| Field | Description |
|-------|-------------|
| `number` | Number of reads in this group |
| `mapq_range` | `[min, max]` mapping quality |
| `base_qual_range` | `[min, max]` base quality scores |
| `len_range` | `[min, max]` as fraction of contig length |
| `delete` | `[start%, end%]` deletion position range |
| `insert` or `insert_middle` | Insertion sequence string |
| `mismatch` | Mismatch rate (0.0 to 1.0) |
| `mods` | Array of modification configurations |

### Modifications Section

| Field | Description |
|-------|-------------|
| `base` | Target base (e.g., "C" for cytosine) |
| `is_strand_plus` | true for + strand, false for - strand |
| `mod_code` | Modification code (e.g., "m" for 5mC) |
| `win` | List of window sizes (number of target bases, e.g., cytosines) |
| `mod_range` | List of `[min, max]` probability ranges, same length as `win` |

The `win` and `mod_range` fields work together to create repeating modification patterns.
Each window size in `win` pairs with the corresponding probability range in `mod_range`.
The pattern cycles along the read until it ends.

For example, with `"base": "C"`, `"win": [5, 3]` and `"mod_range": [[0.7, 1.0], [0.1, 0.4]]` creates:
- 5 cytosines with modification probability 0.7-1.0 (high)
- 3 cytosines with modification probability 0.1-0.4 (low)
- Then repeats: 5 high, 3 low, 5 high, 3 low, ...

## Read ID Prefixes

When you create multiple read groups, each group's read IDs are prefixed with the group index:
- First group: `0.uuid...`
- Second group: `1.uuid...`
- And so on...

This helps identify which group a read belongs to when inspecting output.

## Example Configurations

- [Test data with indels](./test_data_indels.md) — Insertions and deletions
- [Test data with random errors](./test_data_errors.md) — Simulated sequencing errors
- [Test data with variants](./test_data_variants.md) — Heterozygous-like SNP patterns

## Further Reading

For complete API documentation and additional options, see the [nanalogue_core simulate_mod_bam documentation](https://docs.rs/nanalogue/latest/nanalogue_core/simulate_mod_bam/index.html).
