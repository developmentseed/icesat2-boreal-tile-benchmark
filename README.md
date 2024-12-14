# icesat2-boreal-tile-benchmark

Benchmarks for tile rendering performance for the icesat2-boreal dataset

To install the dependencies, [install `uv`](https://docs.astral.sh/uv/getting-started/installation/) then:

```bash
uv sync
```

To run the benchmark locally:

```bash
uv run pytest --benchmark-json /tmp/benchmark.json
```

To run the benchmark and commit the result to the repository you can execute the `benchmark.yml` Github Action script in the Github UI or with the `gh` CLI:

```bash
gh workflow run benchmark.yml
```

To preview the quarto website locally:

```bash
uv run quarto preview
```
