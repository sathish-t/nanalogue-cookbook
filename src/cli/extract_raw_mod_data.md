# Extracting raw mod calls

If you are interested in extracting raw mod calls, please use the following command.
You need to have the `jq` package installed.

```bash
nanalogue read-info --detailed $bam_resource | jq '.[].mod_table[].data[][2]'
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
