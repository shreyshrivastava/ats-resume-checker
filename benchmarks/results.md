# Benchmark Results

These results are one local run on synthetic data. They should be treated as reproducibility evidence, not universal performance claims.

- Generated at: `2026-08-11T15:38:21.922394+00:00`
- Python: `3.14.5`
- Platform: `macOS-26.5.2-arm64-arm-64bit-Mach-O`
- Iterations: `10`
- Score reproducible: `True`

## Latency

### PDF extraction

- Median latency: `0.89 ms`
- Min/Max latency: `0.81 ms` / `2.63 ms`

### Deterministic scoring

- Median latency: `0.56 ms`
- Min/Max latency: `0.52 ms` / `1.19 ms`

### Local retrieved guidance

- Median latency: `0.07 ms`
- Min/Max latency: `0.06 ms` / `0.08 ms`

### Total analysis without MLX

- Median latency: `2.51 ms`
- Min/Max latency: `2.27 ms` / `4.12 ms`

### Total report without MLX

- Median latency: `2.52 ms`
- Min/Max latency: `2.34 ms` / `2.91 ms`
