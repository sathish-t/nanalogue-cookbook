# Test Data with Variants

This configuration creates BAM files with two read groups: one clean, one with mismatches.
This simulates a heterozygous-like variant pattern where only some reads carry the difference.

## Configuration

```bash
cat > config_variant.json << 'EOF'
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
      "mods": [{
        "base": "C",
        "is_strand_plus": true,
        "mod_code": "m",
        "win": [5, 3],
        "mod_range": [[0.7, 1.0], [0.1, 0.4]]
      }]
    },
    {
      "number": 30,
      "mapq_range": [20, 60],
      "base_qual_range": [20, 40],
      "len_range": [1.0, 1.0],
      "mismatch": 0.5,
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
nanalogue_sim_bam config_variant.json variant_data.bam variant_data.fasta
```

## What This Creates

- **3 contigs** of exactly 200bp each
- **Two read groups** of 30 reads each:
  - Group 0 (read IDs start with "0."): Clean reads, no mismatches
  - Group 1 (read IDs start with "1."): Reads with 50% mismatch rate
- **5-methylcytosine modifications** in both groups

## Read ID Prefixes

Read IDs indicate which group a read belongs to:
- `0.uuid...` — First group (clean)
- `1.uuid...` — Second group (with mismatches)

**Important:** This ID-based grouping exists only because we created the test data this way.
In real datasets, read IDs have no relationship to sequence features.

## Used In

- [Spotting variants in sequence data](../cli/spotting_variants_in_sequence_data.md) — Visualizing heterozygous-like patterns
