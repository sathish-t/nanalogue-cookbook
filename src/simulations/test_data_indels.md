# Test Data with Indels

This configuration creates BAM files with insertions, deletions, and modifications.
Useful for testing sequence extraction and alignment visualization.

## Configuration

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

## What This Creates

- **3 contigs** of exactly 200bp each
- **30 reads** spanning the full contig length
- **Deletion** in positions 40%-50% of each read
- **4bp insertion** ("AAAA")
- **5-methylcytosine modifications** with alternating high/low regions

## Used In

- [Extracting sequences](../cli/extracting_sequences.md) — Inspecting insertions and deletions
