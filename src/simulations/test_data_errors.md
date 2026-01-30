# Test Data with Random Errors

This configuration creates BAM files where all reads have random mismatches scattered throughout.
Useful for understanding what sequencing errors look like versus real variants.

## Configuration

```bash
cat > config_errors.json << 'EOF'
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
nanalogue_sim_bam config_errors.json error_data.bam error_data.fasta
```

## What This Creates

- **3 contigs** of exactly 200bp each
- **30 reads** spanning the full contig length
- **50% mismatch rate** — high rate for demonstration purposes
- **5-methylcytosine modifications** with alternating high/low regions

The high mismatch rate creates visually obvious noise where differences are scattered randomly across positions rather than appearing in consistent columns.

## Used In

- [Spotting variants in sequence data](../cli/spotting_variants_in_sequence_data.md) — Distinguishing errors from real variants
