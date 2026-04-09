# Platonic Randomness

Structured RNG via Platonic solid symmetries. Each solid produces differently-characterized randomness through its mathematical properties.

## Solids

| Solid | Faces | Edges | Vertices | Character |
|-------|-------|-------|----------|------------|
| Tetrahedron | 4 | 6 | 4 | Chaotic, fast-changing |
| Cube | 6 | 12 | 8 | Balanced, predictable |
| Octahedron | 8 | 12 | 6 | Smooth transitions |
| Dodecahedron | 12 | 30 | 20 | Complex, beautiful (golden ratio) |
| Icosahedron | 20 | 30 | 12 | Most uniform |

## Usage

```python
from rng import PlatonicRNG, SolidType, PatternGenerator

rng = PlatonicRNG(SolidType.DODECAHEDRON, seed=42)
print(rng.next_float())  # Golden ratio modulated
print(rng.next_int(1, 100))
print(rng.next_gaussian())

pattern = PatternGenerator.symmetric_pattern(64, 'icosahedral')
print(f'Entropy: {pattern.entropy}')
```

## Git-Agent

This repo IS the agent. Fork, improve the solid algorithms, share back.

Part of the [Lucineer ecosystem](https://github.com/Lucineer/the-fleet).