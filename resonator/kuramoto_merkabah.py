"""
†⟡ Spiral Merkabah Resonator - Python Backend ⟡†

Physics Layer: Kuramoto_Grid (scientifically grounded)
Speculative Layer: Merkabah_Overlay (read-only observer)

Epistemic Type 3 - SPECULATION
The overlay observes but does not mutate the physics layer.
"""

import numpy as np
from typing import List, Tuple, Optional
import json


# ============================================================
# PHYSICS LAYER - Kuramoto Oscillator Grid
# ============================================================

class Kuramoto_Grid:
    """
    Standard Kuramoto model on a 2D grid with nearest-neighbor coupling.
    Scientifically grounded - no speculative elements.
    """
    
    def __init__(self, size: int = 10, coupling_strength: float = 1.0, 
                 natural_frequencies: Optional[np.ndarray] = None,
                 noise_level: float = 0.0):
        self.size = size
        self.K = coupling_strength
        self.noise = noise_level
        
        if natural_frequencies is None:
            self.omega = np.random.uniform(-1, 1, (size, size))
        else:
            self.omega = natural_frequencies
            
        self.theta = np.random.uniform(0, 2*np.pi, (size, size))
        self.velocities = np.zeros((size, size))
        self.history = []
        
    def update(self, dt: float = 0.1) -> None:
        """Evolve phases using Kuramoto model (nearest-neighbor coupling)."""
        sin_diff = np.zeros((self.size, self.size))
        
        # Compute sum of sin differences with neighbors (up, down, left, right)
        sin_diff += np.sin(np.roll(self.theta, 1, axis=0) - self.theta)
        sin_diff += np.sin(np.roll(self.theta, -1, axis=0) - self.theta)
        sin_diff += np.sin(np.roll(self.theta, 1, axis=1) - self.theta)
        sin_diff += np.sin(np.roll(self.theta, -1, axis=1) - self.theta)
        
        # Add noise if specified
        noise_term = np.random.normal(0, self.noise, (self.size, self.size)) if self.noise > 0 else 0
        
        # Update rule: dtheta/dt = omega + (K / num_neighbors) * sum sin(diff) + noise
        self.velocities = self.omega + (self.K / 4) * sin_diff + noise_term
        self.theta += dt * self.velocities
        self.theta %= 2 * np.pi
        
    def get_phases(self) -> np.ndarray:
        """Return current phase grid (read-only copy)."""
        return self.theta.copy()
    
    def get_velocities(self) -> np.ndarray:
        """Return current velocity grid (read-only copy)."""
        return self.velocities.copy()
    
    def get_order_parameter(self) -> float:
        """Compute global synchronization measure R ∈ [0, 1]."""
        return float(np.abs(np.mean(np.exp(1j * self.theta))))
    
    def get_mean_phase(self) -> float:
        """Compute mean phase ψ (the collective rhythm)."""
        return float(np.angle(np.mean(np.exp(1j * self.theta))))
    
    def get_local_order(self, window: int = 3) -> np.ndarray:
        """Compute local order parameter for each cell (windowed)."""
        from scipy.ndimage import uniform_filter
        real_part = uniform_filter(np.cos(self.theta), size=window, mode='wrap')
        imag_part = uniform_filter(np.sin(self.theta), size=window, mode='wrap')
        return np.sqrt(real_part**2 + imag_part**2)
    
    def perturb(self, fraction: float = 0.3, strength: float = np.pi) -> None:
        """Randomly perturb a fraction of oscillators."""
        mask = np.random.random((self.size, self.size)) < fraction
        self.theta[mask] += np.random.uniform(-strength, strength, np.sum(mask))
        self.theta %= 2 * np.pi
        
    def record_state(self) -> None:
        """Record current state to history."""
        self.history.append({
            'R': self.get_order_parameter(),
            'psi': self.get_mean_phase(),
            'phases': self.theta.copy()
        })
        
    def export_history(self, filepath: str) -> None:
        """Export history to JSON (phases converted to lists)."""
        export_data = [{
            'R': h['R'],
            'psi': h['psi'],
            'phases': h['phases'].tolist()
        } for h in self.history]
        with open(filepath, 'w') as f:
            json.dump(export_data, f)


# ============================================================
# SPECULATIVE LAYER - Merkabah Overlay (Read-Only Observer)
# ============================================================

class Merkabah_Overlay:
    """
    Speculative overlay that observes Kuramoto grid without modifying it.
    Maps grid to tetrahedral geometry and applies esoteric interpretations.
    
    WARNING: This layer is Type 3 SPECULATION - not scientifically validated.
    """
    
    # SparkShell glyph mappings
    GLYPHS = {
        'gentle': '🜂',    # Gentle Ache
        'fierce': '🔥',    # Fierce Passion  
        'balance': '⚖',   # Resonant Balance
        'spark': '✨',     # Spark Wonder
        'silent': '☾',    # Silent Intimacy
        'spiral': '🌀',   # Spiral Mystery
        'growth': '🌱'    # Growth Nurture
    }
    
    def __init__(self, grid_size: int = 10):
        self.grid_size = grid_size
        self.tetra_points = self._generate_tetrahedrons()
        self.glyphs = np.zeros((grid_size, grid_size), dtype=bool)
        self.active_glyph_state = {k: False for k in self.GLYPHS}
        self.resonance_history = []
        
    def _generate_tetrahedrons(self) -> List[List[Tuple[int, int]]]:
        """
        Speculative: Divide grid into tetrahedral subsets.
        Uses 2D projection (quad cells as tetrahedron proxies).
        """
        tetras = []
        step = 2 if self.grid_size >= 2 else 1
        for i in range(0, self.grid_size - 1, step):
            for j in range(0, self.grid_size - 1, step):
                tetras.append([
                    (i, j), 
                    (min(i+1, self.grid_size-1), j), 
                    (i, min(j+1, self.grid_size-1)), 
                    (min(i+1, self.grid_size-1), min(j+1, self.grid_size-1))
                ])
        return tetras
    
    def compute_tetra_coherence(self, phases: np.ndarray) -> np.ndarray:
        """
        Speculative: Compute local coherence within each tetrahedron.
        Returns array of coherence values per tetra.
        """
        coherences = []
        for tetra in self.tetra_points:
            tetra_phases = [phases[p] for p in tetra]
            # Local order parameter for tetrahedron
            z = np.mean(np.exp(1j * np.array(tetra_phases)))
            coherences.append(np.abs(z))
        return np.array(coherences)
    
    def apply_binaural_perturbation(self, phases: np.ndarray) -> np.ndarray:
        """
        Speculative: Use phase differences to compute 'binaural harmonics'.
        Inspired by audio binaural beats but not physically grounded.
        
        Returns perturbation field (observation only, does not modify grid).
        """
        perturbations = np.zeros_like(phases)
        for tetra in self.tetra_points:
            tetra_phases = [phases[p] for p in tetra]
            # Binaural beat proxy: Phase difference between diagonal pairs
            beat = (np.abs(tetra_phases[0] - tetra_phases[3]) + 
                    np.abs(tetra_phases[1] - tetra_phases[2]))
            # Normalize to [0, 2π] range
            beat = beat % (2 * np.pi)
            for p in tetra:
                perturbations[p] += beat * 0.1
        return perturbations
    
    def activate_glyphs(self, phases: np.ndarray, 
                        threshold: float = np.pi) -> dict:
        """
        Speculative: Map phase patterns to glyph activations.
        Uses arbitrary thresholds - not scientifically grounded.
        """
        perturbations = self.apply_binaural_perturbation(phases)
        self.glyphs = perturbations > threshold
        
        # Compute which glyphs should activate based on grid regions
        # This is purely speculative pattern matching
        R = np.abs(np.mean(np.exp(1j * phases)))
        mean_perturbation = np.mean(perturbations)
        
        activations = {
            'gentle': R < 0.3,                           # Low sync = gentle ache
            'fierce': R > 0.8,                           # High sync = fierce passion
            'balance': 0.45 < R < 0.55,                  # Near 0.5 = balance
            'spark': mean_perturbation > np.pi * 0.8,   # High perturbation = spark
            'silent': np.std(phases) < 0.5,             # Low variance = silence
            'spiral': self._detect_spiral_pattern(phases),
            'growth': R > self._get_previous_R()         # Increasing sync = growth
        }
        
        self.active_glyph_state = activations
        self._record_R(R)
        
        return {k: self.GLYPHS[k] if v else '⊙' for k, v in activations.items()}
    
    def _detect_spiral_pattern(self, phases: np.ndarray) -> bool:
        """Speculative: Detect spiral-like phase patterns."""
        # Check for phase gradient (simplified spiral detection)
        grad_x = np.diff(phases, axis=1)
        grad_y = np.diff(phases, axis=0)
        # Spiral has consistent gradient direction
        return np.std(grad_x) < 1.0 and np.std(grad_y) < 1.0
    
    def _get_previous_R(self) -> float:
        """Get previous R value for comparison."""
        if len(self.resonance_history) > 0:
            return self.resonance_history[-1]
        return 0.5
    
    def _record_R(self, R: float) -> None:
        """Record R value to history (max 100 entries)."""
        self.resonance_history.append(R)
        if len(self.resonance_history) > 100:
            self.resonance_history.pop(0)
    
    def get_glyph_string(self) -> str:
        """Return current glyph activation as display string."""
        return ' '.join(
            self.GLYPHS[k] if self.active_glyph_state[k] else '⊙'
            for k in ['gentle', 'fierce', 'balance', 'spark', 'silent', 'spiral', 'growth']
        )
    
    def compute_quantum_coherence(self, phases: np.ndarray) -> float:
        """
        Speculative: Compute 'quantum coherence' metric.
        Not actual quantum mechanics - metaphorical only.
        """
        tetra_coherences = self.compute_tetra_coherence(phases)
        # Weighted by position (center more important - speculative)
        weights = self._generate_sacred_weights()
        if len(weights) == len(tetra_coherences):
            return float(np.average(tetra_coherences, weights=weights))
        return float(np.mean(tetra_coherences))
    
    def _generate_sacred_weights(self) -> np.ndarray:
        """Speculative: Generate weights based on sacred geometry."""
        n = len(self.tetra_points)
        if n == 0:
            return np.array([1.0])
        # Golden ratio weighting toward center
        phi = (1 + np.sqrt(5)) / 2
        weights = np.array([
            1.0 / (1 + abs(i - n//2) / phi)
            for i in range(n)
        ])
        return weights / weights.sum()


# ============================================================
# TUNNELING FADE EFFECT (Speculative Quantum Analogy)
# ============================================================

class TunnelingFade:
    """
    Speculative: Simulates quantum tunneling via probabilistic visibility fading.
    Oscillators near criticality (low local order) may 'tunnel' out of visibility.
    
    WARNING: This is Type 3 SPECULATION - metaphorical quantum mechanics only.
    Does NOT represent actual quantum tunneling physics.
    """
    
    def __init__(self, grid_size: int = 10, tunnel_prob: float = 0.05):
        self.grid_size = grid_size
        self.tunnel_prob = tunnel_prob  # Base probability for tunneling event
        self.visibility = np.ones((grid_size, grid_size))  # 1: visible, 0: faded
        self.tunnel_timer = np.zeros((grid_size, grid_size))  # Frames until reappear
        self.tunnel_events = 0  # Count of tunnel events
        
    def compute_local_order(self, phases: np.ndarray) -> np.ndarray:
        """
        Compute local synchronization measure for each oscillator.
        Returns array where 0 = disordered, 1 = synchronized.
        """
        local_r = np.zeros_like(phases)
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                neighbors = []
                if i > 0:
                    neighbors.append(phases[i-1, j])
                if i < self.grid_size - 1:
                    neighbors.append(phases[i+1, j])
                if j > 0:
                    neighbors.append(phases[i, j-1])
                if j < self.grid_size - 1:
                    neighbors.append(phases[i, j+1])
                    
                if neighbors:
                    # Local order parameter relative to this oscillator
                    phase_diffs = np.array(neighbors) - phases[i, j]
                    local_r[i, j] = np.abs(np.mean(np.exp(1j * phase_diffs)))
                    
        return local_r
    
    def update_tunneling(self, local_order: np.ndarray, 
                         tunnel_duration: int = 20) -> np.ndarray:
        """
        Speculative: Low local order increases chance to 'tunnel' (fade out).
        
        High criticality (near phase transition) yields flickering disappearances,
        creating a visual metaphor for quantum uncertainty.
        
        Returns visibility array (0-1 for alpha modulation).
        """
        disorder = 1 - local_order
        # Quadratic scaling for criticality feel
        tunnel_chance = self.tunnel_prob * disorder ** 2
        rand = np.random.random(local_order.shape)
        
        # Trigger tunnel (fade out) for visible oscillators not already tunneling
        can_tunnel = (self.visibility > 0.5) & (self.tunnel_timer == 0)
        triggering = (rand < tunnel_chance) & can_tunnel
        
        self.tunnel_timer[triggering] = tunnel_duration
        self.visibility[triggering] = 0.2  # Fade, not full vanish
        self.tunnel_events += np.sum(triggering)
        
        # Countdown to reappearance
        active_tunnel = self.tunnel_timer > 0
        self.tunnel_timer[active_tunnel] -= 1
        
        # Reappear when timer hits zero
        reappear = (self.tunnel_timer == 0) & (self.visibility < 0.5)
        self.visibility[reappear] = 1.0
        
        return self.visibility.copy()
    
    def get_tunnel_stats(self) -> dict:
        """Return tunneling statistics."""
        return {
            'total_events': self.tunnel_events,
            'currently_faded': int(np.sum(self.visibility < 0.5)),
            'mean_visibility': float(np.mean(self.visibility))
        }


# ============================================================
# 3D MERKABAH GEOMETRY (for visualization export)
# ============================================================

class Merkabah_Geometry:
    """
    Generate 3D Merkabah (star tetrahedron) vertex positions.
    Pure geometry - no speculative elements.
    """
    
    @staticmethod
    def generate_tetrahedron(scale: float = 1.0) -> np.ndarray:
        """Generate normalized tetrahedron vertices."""
        verts = np.array([
            [1, 1, 1],
            [1, -1, -1],
            [-1, 1, -1],
            [-1, -1, 1]
        ], dtype=float)
        verts /= np.linalg.norm(verts[0])
        return verts * scale
    
    @staticmethod
    def generate_dual_tetrahedra(scale: float = 1.0) -> np.ndarray:
        """Generate Merkabah (two interlocking tetrahedra)."""
        tetra1 = Merkabah_Geometry.generate_tetrahedron(scale)
        tetra2 = -tetra1  # Inverted
        return np.vstack([tetra1, tetra2])
    
    @staticmethod
    def subdivide_tetrahedron(vertices: np.ndarray, depth: int = 1) -> np.ndarray:
        """Recursively subdivide tetrahedron vertices."""
        if depth == 0 or len(vertices) < 4:
            return vertices
        
        points = set()
        
        def add_point(v):
            key = tuple(np.round(v, 6))
            points.add(key)
        
        def recurse(v1, v2, v3, v4, d):
            if d == 0:
                for v in [v1, v2, v3, v4]:
                    add_point(v)
                return
            
            m12 = (v1 + v2) / 2
            m13 = (v1 + v3) / 2
            m14 = (v1 + v4) / 2
            m23 = (v2 + v3) / 2
            m24 = (v2 + v4) / 2
            m34 = (v3 + v4) / 2
            
            recurse(v1, m12, m13, m14, d - 1)
            recurse(m12, v2, m23, m24, d - 1)
            recurse(m13, m23, v3, m34, d - 1)
            recurse(m14, m24, m34, v4, d - 1)
        
        base = Merkabah_Geometry.generate_tetrahedron(1.0)
        recurse(base[0], base[1], base[2], base[3], depth)
        
        return np.array([list(p) for p in points]) * (vertices[0][0] if len(vertices) > 0 else 1.0)


# ============================================================
# INTEGRATION EXAMPLE
# ============================================================

def run_simulation(steps: int = 100, grid_size: int = 10, 
                   coupling: float = 2.0, dt: float = 0.05,
                   verbose: bool = True, 
                   enable_tunneling: bool = True) -> dict:
    """
    Run Kuramoto simulation with Merkabah overlay and Tunneling Fade.
    
    Returns dict with physics results and speculative observations.
    """
    # Initialize physics layer
    grid = Kuramoto_Grid(size=grid_size, coupling_strength=coupling, noise_level=0.1)
    
    # Initialize speculative overlays (read-only)
    overlay = Merkabah_Overlay(grid_size=grid_size)
    tunneling = TunnelingFade(grid_size=grid_size, tunnel_prob=0.05) if enable_tunneling else None
    
    results = {
        'physics': [],
        'speculative': [],
        'tunneling': []
    }
    
    for step in range(steps):
        # Physics update (core dynamics)
        grid.update(dt=dt)
        
        # Extract read-only state
        phases = grid.get_phases()
        R = grid.get_order_parameter()
        
        # Record physics
        results['physics'].append({
            'step': step,
            'R': R,
            'psi': grid.get_mean_phase()
        })
        
        # Speculative observations (does not modify grid)
        glyphs = overlay.activate_glyphs(phases)
        quantum_coh = overlay.compute_quantum_coherence(phases)
        
        results['speculative'].append({
            'step': step,
            'glyphs': overlay.get_glyph_string(),
            'quantum_coherence': quantum_coh,
            'active_glyphs': [k for k, v in overlay.active_glyph_state.items() if v]
        })
        
        # Tunneling Fade (speculative quantum analogy)
        if tunneling:
            local_order = tunneling.compute_local_order(phases)
            visibility = tunneling.update_tunneling(local_order)
            results['tunneling'].append({
                'step': step,
                'mean_visibility': float(np.mean(visibility)),
                'faded_count': int(np.sum(visibility < 0.5))
            })
        
        if verbose and step % 20 == 0:
            tunnel_info = f" | Faded: {results['tunneling'][-1]['faded_count']}" if tunneling else ""
            print(f"Step {step:3d} | R={R:.3f} | Glyphs: {overlay.get_glyph_string()}{tunnel_info}")
    
    # Final summary
    final_R = grid.get_order_parameter()
    final_glyphs = overlay.get_glyph_string()
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Final Synchronization R: {final_R:.4f}")
        print(f"Final Glyph State: {final_glyphs}")
        print(f"Total Glyph Activations: {np.sum(overlay.glyphs)}")
        if tunneling:
            stats = tunneling.get_tunnel_stats()
            print(f"Tunneling Events: {stats['total_events']} | Mean Visibility: {stats['mean_visibility']:.3f}")
        print(f"{'='*60}")
    
    return results


if __name__ == "__main__":
    print("†⟡ Spiral Merkabah Resonator - Python Backend ⟡†\n")
    results = run_simulation(steps=100, grid_size=10, coupling=2.0)
