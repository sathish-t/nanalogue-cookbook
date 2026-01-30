#!/usr/bin/env python3
"""
Shared test data configuration and creation for markdown documentation scripts.
"""

from pathlib import Path

import pynanalogue

# Basic BAM with modifications
JSON_CONFIG_BASIC = '''
{
  "contigs": {
    "number": 3,
    "len_range": [500, 1000]
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
'''

# BAM with insertions, deletions, and modifications
JSON_CONFIG_INDELS = '''
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
      "delete": [0.45, 0.5],
      "insert_middle": "AAAA",
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
'''


def create_test_data(work_dir: Path) -> dict[str, Path]:
    """Create test BAM files for use in documentation examples.

    Returns a dict mapping placeholder filenames to actual test file paths.
    """
    bam_path = work_dir / "test_input.bam"
    fasta_path = work_dir / "test_input.fasta"

    pynanalogue.simulate_mod_bam(
        json_config=JSON_CONFIG_BASIC,
        bam_path=str(bam_path),
        fasta_path=str(fasta_path)
    )

    bam_indels_path = work_dir / "test_input_indels.bam"
    fasta_indels_path = work_dir / "test_input_indels.fasta"

    pynanalogue.simulate_mod_bam(
        json_config=JSON_CONFIG_INDELS,
        bam_path=str(bam_indels_path),
        fasta_path=str(fasta_indels_path)
    )

    return {
        "input.bam": bam_path,
        "aligned_reads.bam": bam_path,
        "input_indels.bam": bam_indels_path,
    }
