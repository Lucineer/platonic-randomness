"""Platonic Randomness — Structured RNG via Platonic solid symmetries.

Each Platonic solid generates differently-characterized randomness:
- Tetrahedron: 4 faces, chaotic/fast-changing
- Cube: 6 faces, balanced/predictable  
- Octahedron: 8 faces, smooth transitions
- Dodecahedron: 12 faces, complex/beautiful (golden ratio)
- Icosahedron: 20 faces, most uniform
"""

import math
import hashlib
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Optional


class SolidType(Enum):
    TETRAHEDRON = "tetrahedron"
    CUBE = "cube"
    OCTAHEDRON = "octahedron"
    DODECAHEDRON = "dodecahedron"
    ICOSAHEDRON = "icosahedron"


# Platonic solid properties
SOLID_PROPS = {
    SolidType.TETRAHEDRON: {"faces": 4, "edges": 6, "vertices": 4, "dual": SolidType.TETRAHEDRON, "symmetry_group": "A4"},
    SolidType.CUBE: {"faces": 6, "edges": 12, "vertices": 8, "dual": SolidType.OCTAHEDRON, "symmetry_group": "S4"},
    SolidType.OCTAHEDRON: {"faces": 8, "edges": 12, "vertices": 6, "dual": SolidType.CUBE, "symmetry_group": "S4"},
    SolidType.DODECAHEDRON: {"faces": 12, "edges": 30, "vertices": 20, "dual": SolidType.ICOSAHEDRON, "symmetry_group": "A5"},
    SolidType.ICOSAHEDRON: {"faces": 20, "edges": 30, "vertices": 12, "dual": SolidType.DODECAHEDRON, "symmetry_group": "A5"},
}

PHI = (1 + math.sqrt(5)) / 2  # Golden ratio


@dataclass
class SolidGeometry:
    """Geometric properties of a Platonic solid."""
    solid: SolidType
    faces: int
    edges: int
    vertices: int
    dual: SolidType
    symmetry_group: str
    euler_characteristic: int = 2  # V - E + F = 2 for all Platonic solids


@dataclass
class PatternResult:
    """A generated pattern from Platonic symmetry."""
    values: List[float]
    dimensions: Tuple[int, int]
    symmetry: str
    entropy: float  # Shannon entropy of the pattern


class PlatonicRNG:
    """Random number generator based on Platonic solid symmetries.
    
    Uses the mathematical properties of each solid to shape
    the distribution of random numbers.
    """
    
    def __init__(self, solid: SolidType = SolidType.DODECAHEDRON, seed: Optional[int] = None):
        self.solid = solid
        self.props = SOLID_PROPS[solid]
        self._counter = 0
        self._seed = seed or 42
        
    def _hash(self, extra: int = 0) -> float:
        """Generate a deterministic float from solid + counter."""
        data = f"{self.solid.value}:{self._seed}:{self._counter}:{extra}"
        h = hashlib.sha256(data.encode()).hexdigest()
        return int(h[:16], 16) / (2**64)
    
    def next_float(self) -> float:
        """Generate a structured random float [0, 1]."""
        raw = self._hash()
        self._counter += 1
        
        # Shape the distribution based on solid properties
        if self.solid == SolidType.TETRAHEDRON:
            # Chaotic: cube root for more extreme values
            return raw ** (1/3)
        elif self.solid == SolidType.CUBE:
            # Balanced: linear
            return raw
        elif self.solid == SolidType.OCTAHEDRON:
            # Smooth: sin-based warping
            return (math.sin(raw * math.pi * 2) + 1) / 2
        elif self.solid == SolidType.DODECAHEDRON:
            # Golden ratio modulation
            return (raw * PHI) % 1.0
        elif self.solid == SolidType.ICOSAHEDRON:
            # Most uniform: already near-uniform from hash
            return raw
        return raw
    
    def next_int(self, low: int, high: int) -> int:
        """Generate a structured random int [low, high]."""
        return low + int(self.next_float() * (high - low + 1))
    
    def next_boolean(self, probability: float = 0.5) -> bool:
        """Generate a structured random boolean."""
        return self.next_float() < probability
    
    def next_choice(self, options: list) -> any:
        """Pick a structured random choice from options."""
        return options[self.next_int(0, len(options) - 1)]
    
    def next_gaussian(self, mean: float = 0.0, stddev: float = 1.0) -> float:
        """Approximate Gaussian using Box-Muller with solid shaping."""
        u1 = max(self.next_float(), 1e-10)
        u2 = self.next_float()
        z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
        return mean + z * stddev
    
    def geometry(self) -> SolidGeometry:
        """Get the geometric properties of this RNG's solid."""
        p = self.props
        return SolidGeometry(self.solid, p["faces"], p["edges"], p["vertices"],
                           p["dual"], p["symmetry_group"])


class PatternGenerator:
    """Generate 2D patterns using Platonic symmetries."""
    
    @staticmethod
    def symmetric_pattern(size: int, symmetry: str = "icosahedral", seed: int = 42) -> PatternResult:
        """Generate a symmetric 2D pattern.
        
        Args:
            size: Grid size (size x size)
            symmetry: Symmetry type (tetrahedral, cubic, octahedral, dodecahedral, icosahedral)
            seed: RNG seed
        """
        sym_map = {
            "tetrahedral": SolidType.TETRAHEDRON,
            "cubic": SolidType.CUBE,
            "octahedral": SolidType.OCTAHEDRON,
            "dodecahedral": SolidType.DODECAHEDRON,
            "icosahedral": SolidType.ICOSAHEDRON,
        }
        solid = sym_map.get(symmetry, SolidType.ICOSAHEDRON)
        rng = PlatonicRNG(solid, seed)
        
        # Symmetry fold counts (how many times the pattern repeats)
        fold_map = {
            SolidType.TETRAHEDRON: 4,
            SolidType.CUBE: 6,
            SolidType.OCTAHEDRON: 8,
            SolidType.DODECAHEDRON: 12,
            SolidType.ICOSAHEDRON: 20,
        }
        folds = fold_map[solid]
        
        # Generate one sector, then replicate with symmetry
        sector_size = size // 2
        base = []
        for y in range(sector_size):
            row = []
            for x in range(sector_size):
                row.append(rng.next_float())
            base.append(row)
        
        # Mirror and rotate to fill the grid
        values = [[0.0] * size for _ in range(size)]
        for y in range(min(sector_size, size)):
            for x in range(min(sector_size, size)):
                val = base[y % len(base)][x % len(base[0])]
                values[y][x] = val
                values[y][size - 1 - x] = val  # Mirror horizontal
                if y < size - 1 - y:
                    values[size - 1 - y][x] = val  # Mirror vertical
                    values[size - 1 - y][size - 1 - x] = val  # Mirror both
        
        # Calculate entropy
        flat = [v for row in values for v in row]
        entropy = -sum(p * math.log2(p) for p in _histogram(flat, 32) if p > 0)
        
        return PatternResult(values=flat, dimensions=(size, size), symmetry=symmetry, entropy=entropy)
    
    @staticmethod
    def golden_spiral(n: int = 100, seed: int = 42) -> List[Tuple[float, float]]:
        """Generate points on a golden spiral using dodecahedral RNG."""
        rng = PlatonicRNG(SolidType.DODECAHEDRON, seed)
        points = []
        for i in range(n):
            theta = i * 2 * math.pi / PHI
            r = math.sqrt(i / n) * rng.next_float()
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            points.append((x, y))
        return points


def _histogram(values: List[float], bins: int) -> List[float]:
    """Compute normalized histogram."""
    counts = [0] * bins
    for v in values:
        idx = min(int(v * bins), bins - 1)
        counts[idx] += 1
    total = sum(counts)
    return [c / total for c in counts] if total > 0 else counts


# Vertex coordinates for each solid
VERTICES = {
    SolidType.TETRAHEDRON: [(1,1,1),(1,-1,-1),(-1,1,-1),(-1,-1,1)],
    SolidType.CUBE: [(x,y,z) for x in (-1,1) for y in (-1,1) for z in (-1,1)],
    SolidType.OCTAHEDRON: [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)],
    SolidType.DODECAHEDRON: [
        (0,PHI,1),(0,PHI,-1),(0,-PHI,1),(0,-PHI,-1),
        (1,0,PHI),(1,0,-PHI),(-1,0,PHI),(-1,0,-PHI),
        (PHI,1,0),(PHI,-1,0),(-PHI,1,0),(-PHI,-1,0),
        (1,1,1),(1,1,-1),(1,-1,1),(1,-1,-1),
        (-1,1,1),(-1,1,-1),(-1,-1,1),(-1,-1,-1),
    ],
    SolidType.ICOSAHEDRON: [
        (0,1,PHI),(0,1,-PHI),(0,-1,PHI),(0,-1,-PHI),
        (1,PHI,0),(1,-PHI,0),(-1,PHI,0),(-1,-PHI,0),
        (PHI,0,1),(PHI,0,-1),(-PHI,0,1),(-PHI,0,-1),
    ],
}
