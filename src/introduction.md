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

- [Using Cargo](#using-cargo)
- [Using Docker](#using-docker)
- [Pre-built Binaries](#pre-built-binaries)
- [Python Library](#python-library)

### Using Cargo

Run the following command to install or update `nanalogue` for usage on the command line:

```bash
cargo install nanalogue
```

`cargo` is the Rust package manager. If you do not have `cargo`,
follow these [instructions](https://doc.rust-lang.org/cargo/getting-started/installation.html)
to get it. On Linux and macOS systems, the install command is as simple as
`curl https://sh.rustup.rs -sSf | sh`

If the `cargo install` command fails, try using the `--locked` flag:

```bash
cargo install nanalogue --locked
```

This uses the exact versions of dependencies specified in the package's `Cargo.lock` file,
and fixes install problems due to newer packages.

### Using Docker

You can also use `nanalogue` via Docker:

```bash
docker pull dockerofsat/nanalogue:latest
```

### Pre-built Binaries

The easiest way to install pre-built binaries is using the install script:

```bash
curl -fsSL https://raw.githubusercontent.com/DNAReplicationLab/nanalogue/main/install.sh | sh
```

The script requires `curl` (or `wget`), `unzip`, `jq`, and `sha256sum` (or `shasum`).

Alternatively, pre-built binaries for macOS and Linux are available from:

- **GitHub Releases**: Official release binaries can be downloaded from the [Releases page](https://github.com/DNAReplicationLab/nanalogue/releases). Each release includes binaries for multiple platforms.

- **GitHub Actions Artifacts**: Binaries built from the latest code are available as artifacts from the [Build Release Binaries workflow](https://github.com/DNAReplicationLab/nanalogue/actions/workflows/build-binaries.yml). Download the binary artifact for your platform (macOS, musl Linux, manylinux variants for different glibc versions).

### Python Library

To install the Python wrapper `pynanalogue`:

```bash
pip install pynanalogue
```
