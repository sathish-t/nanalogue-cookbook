# Introduction

Nanalogue = *N*ucleic Acid *Analogue* 

A common pain point in the genomics community is that BAM files are information-dense
which makes it difficult to gain insight from them. Nanalogue hopes to make it easy
to extract and process this information, and forms a companion to other tools such
as [samtools](https://www.htslib.org) and [modkit](https://nanoporetech.github.io/modkit/).
Although nanalogue's primary focus is on DNA/RNA modifications
on a single-molecule level, some of its functions are quite general and can be applied
to almost any BAM file. Nanalogue is open-source and its code can be found
on [Github](https://github.com/DNAReplicationLab/nanalogue). The code of a companion package
pynanalogue can be found [here](https://github.com/DNAReplicationLab/nanalogue).

If you are a developer who needs BAM files with defined single-molecule modification patterns
to help develop/test your tool, nanalogue can also help you create BAM files from scratch
using artificial data created using parameters defined by you.

This documentation site is under active development.

## Usage

This book is divided into two parts, based on two out of the following three ways to use
nanalogue:
- as a command line interface i.e. a tool that can be run from the terminal. See [here](./cli.md).
- as a python library i.e. if you write python code, you can use pynanalogue, a wrapper around
  a subset of nanalogue's functions. See [here](./python.md).
- as a rust library i.e. if you write rust code, you can benefit from nanalogue's functions.
  If you are a rust developer looking to use nanalogue as a rust library,
  please head over to [docs.rs](https://docs.rs/nanalogue/latest/nanalogue_core/). 

## Installation

General installation methods such as `cargo install` and `pip install` should work.
For the most up to date information, please consult the README files from the
Github links above.
