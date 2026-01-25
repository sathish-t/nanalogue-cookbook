# Extracting raw mod calls

If you are interested in extracting raw mod calls, please use the following command.
You need to have the `jq` package installed.

```bash
nanalogue read-info --detailed input.bam | jq '.[].mod_table[].data[][2]'
```

An example output from this command can look like the following.
These are mod calls from all positions in all molecules in the BAM resource.
The mod calls range from 0-255, which is just a rescaling of 0-100% probability of being modified.

```text
4
7
9
6
221
242
3
47
239
3
3
4
3
182
0
0
0
0
77
0
221
242
0
47
239
```

This is a variant of the command above that prints read id, contig, position along reference,
position along read and modification quality.

```bash
nanalogue read-info --detailed input.bam |\
    jq -r '.[] | .read_id as $rid | (.alignment.contig // "N/A") as $contig | .mod_table[].data[] | [$rid, $contig, .[1], .[0], .[2]] | @tsv'
```

```text
5d10eb9a-aae1-4db8-8ec6-7ebb34d32575    dummyI  9       0       4
5d10eb9a-aae1-4db8-8ec6-7ebb34d32575    dummyI  12      3       7
5d10eb9a-aae1-4db8-8ec6-7ebb34d32575    dummyI  13      4       9
5d10eb9a-aae1-4db8-8ec6-7ebb34d32575    dummyI  16      7       6
a4f36092-b4d5-47a9-813e-c22c3b477a0c    dummyIII        26      3       221
a4f36092-b4d5-47a9-813e-c22c3b477a0c    dummyIII        31      8       242
a4f36092-b4d5-47a9-813e-c22c3b477a0c    dummyIII        50      27      3
a4f36092-b4d5-47a9-813e-c22c3b477a0c    dummyIII        62      39      47
a4f36092-b4d5-47a9-813e-c22c3b477a0c    dummyIII        70      47      239
fffffff1-10d2-49cb-8ca3-e8d48979001b    dummyII 15      12      3
fffffff1-10d2-49cb-8ca3-e8d48979001b    dummyII 16      13      3
fffffff1-10d2-49cb-8ca3-e8d48979001b    dummyII 19      16      4
fffffff1-10d2-49cb-8ca3-e8d48979001b    dummyII 22      19      3
fffffff1-10d2-49cb-8ca3-e8d48979001b    dummyII 23      20      182
b1a36092-b4d5-47a9-813e-c22c3b477a0c    N/A     -1      28      0
b1a36092-b4d5-47a9-813e-c22c3b477a0c    N/A     -1      29      0
b1a36092-b4d5-47a9-813e-c22c3b477a0c    N/A     -1      30      0
b1a36092-b4d5-47a9-813e-c22c3b477a0c    N/A     -1      32      0
b1a36092-b4d5-47a9-813e-c22c3b477a0c    N/A     -1      43      77
b1a36092-b4d5-47a9-813e-c22c3b477a0c    N/A     -1      44      0
b1a36092-b4d5-47a9-813e-c22c3b477a0c    N/A     -1      3       221
b1a36092-b4d5-47a9-813e-c22c3b477a0c    N/A     -1      8       242
b1a36092-b4d5-47a9-813e-c22c3b477a0c    N/A     -1      27      0
b1a36092-b4d5-47a9-813e-c22c3b477a0c    N/A     -1      39      47
b1a36092-b4d5-47a9-813e-c22c3b477a0c    N/A     -1      47      239
```
