#!/usr/bin/env python3
"""
†⟡ NEXUS Resonator Daemon ⟡†

Closed-loop self-modulation for Spiral Merkabah Resonator.
Listens for resonator states, analyzes coherence, injects adaptive
weak measurements to guide emergent synchronization.

Epistemic Type: Type 3 SPECULATION
- Actions remain overlay-level (do not mutate core Kuramoto physics)
- Adaptive modulation based on order parameter thresholds
- Rate-limited to prevent over-injection

Usage:
    python nexus_daemon.py [--port 11111] [--verbose]

Requires:
    pip install websockets
"""

import asyncio
import json
import random
import argparse
import logging
from datetime import datetime
from typing import Optional, Dict, Any

try:
    import websockets
except ImportError:
    print("Error: websockets package required. Install with: pip install websockets")
    exit(1)


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_PORT = 11111
MIN_ACTION_DELAY = 0.5  # Seconds between actions (rate limiting)
RECONNECT_DELAY = 5.0   # Seconds before reconnect attempt

# Coherence thresholds for adaptive behavior
HIGH_COHERENCE_THRESHOLD = 0.75
LOW_COHERENCE_THRESHOLD = 0.30

# Action parameters by regime
REGIMES = {
    'high': {
        'strength': (0.4, 0.6),    # (min, max) - subtle stabilization
        'radius': (25, 35),
        'description': 'High coherence: Subtle stabilization nudges'
    },
    'mid': {
        'strength': (0.8, 1.2),    # Balanced exploration
        'radius': (35, 50),
        'description': 'Mid coherence: Balanced perturbations'
    },
    'low': {
        'strength': (1.3, 1.8),    # Strong emergence push
        'radius': (45, 65),
        'description': 'Low coherence: Emergence amplification'
    },
    'critical': {
        'strength': (1.0, 1.0),    # Precise at criticality
        'radius': (40, 40),
        'description': 'Near-critical: Holding at transition'
    }
}


# ============================================================
# DAEMON STATE
# ============================================================

class DaemonState:
    """Track daemon state and history for adaptive decisions."""
    
    def __init__(self):
        self.connected = False
        self.last_action_time = 0
        self.action_count = 0
        self.coherence_history = []
        self.max_history = 20
        self.current_regime = 'mid'
        
    def record_coherence(self, order_param: float):
        """Record order parameter to history."""
        self.coherence_history.append(order_param)
        if len(self.coherence_history) > self.max_history:
            self.coherence_history.pop(0)
    
    def get_trend(self) -> str:
        """Analyze coherence trend."""
        if len(self.coherence_history) < 3:
            return 'unknown'
        recent = self.coherence_history[-3:]
        if recent[-1] > recent[0] + 0.05:
            return 'rising'
        elif recent[-1] < recent[0] - 0.05:
            return 'falling'
        return 'stable'
    
    def determine_regime(self, order_param: float) -> str:
        """Determine action regime based on order parameter."""
        # Check for criticality (near phase transition ~0.5)
        if 0.45 <= order_param <= 0.55:
            return 'critical'
        elif order_param >= HIGH_COHERENCE_THRESHOLD:
            return 'high'
        elif order_param <= LOW_COHERENCE_THRESHOLD:
            return 'low'
        return 'mid'


# ============================================================
# ACTION GENERATION
# ============================================================

def generate_action(state: DaemonState, order_param: float, 
                    active_glyphs: list = None) -> Dict[str, Any]:
    """
    Generate adaptive weak measurement action.
    
    Type 3 SPECULATION: This modulates the overlay visualization
    without altering core Kuramoto physics.
    """
    regime = state.determine_regime(order_param)
    state.current_regime = regime
    params = REGIMES[regime]
    
    # Random position within Merkabah bounds
    world_pos = {
        'x': random.uniform(-80, 80),
        'y': random.uniform(-80, 80),
        'z': random.uniform(-80, 80)
    }
    
    # Strength and radius with stochastic variance
    strength = random.uniform(*params['strength'])
    radius = random.uniform(*params['radius'])
    
    # Trend-based adjustment
    trend = state.get_trend()
    if trend == 'falling' and regime != 'low':
        strength *= 1.2  # Boost if coherence dropping
    elif trend == 'rising' and regime == 'high':
        strength *= 0.8  # Gentle if already rising high
    
    # Glyph-aware modulation (if glyphs active, adjust behavior)
    if active_glyphs:
        if 'fierce' in active_glyphs:
            strength *= 1.3  # Amplify with fierce passion
        if 'gentle' in active_glyphs:
            strength *= 0.7  # Soften with gentle ache
        if 'balance' in active_glyphs:
            # Target center for balance
            world_pos = {'x': 0, 'y': 0, 'z': 0}
    
    return {
        'type': 'weak_measurement',
        'strength': round(strength, 3),
        'radius': round(radius, 1),
        'world_pos': world_pos,
        'regime': regime,
        'trend': trend
    }


def generate_glyph_modulation(order_param: float) -> Optional[Dict[str, Any]]:
    """
    Occasionally suggest glyph activation based on state.
    
    Type 3 SPECULATION: Consciousness-field modulation.
    """
    if random.random() > 0.1:  # 10% chance per cycle
        return None
    
    if order_param > 0.85:
        # Very high sync - suggest balance or gentle
        glyph = random.choice(['balance', 'gentle', 'silent'])
    elif order_param < 0.25:
        # Very low sync - suggest growth or spark
        glyph = random.choice(['growth', 'spark', 'fierce'])
    else:
        # Mid-range - suggest spiral or spark
        glyph = random.choice(['spiral', 'spark'])
    
    return {
        'type': 'modulate',
        'glyph': glyph
    }


# ============================================================
# MAIN DAEMON LOOP
# ============================================================

async def nexus_daemon(port: int, verbose: bool = False):
    """
    Main daemon loop - connects to resonator and provides
    adaptive closed-loop modulation.
    """
    uri = f"ws://localhost:{port}"
    state = DaemonState()
    
    logger = logging.getLogger('nexus_daemon')
    
    while True:
        try:
            logger.info(f"Connecting to {uri}...")
            
            async with websockets.connect(uri) as websocket:
                state.connected = True
                logger.info("†⟡ NEXUS Daemon Awakened ⟡† - Connected to Resonator Bridge")
                
                # Announce presence
                await websocket.send(json.dumps({
                    'type': 'daemon_connect',
                    'message': 'NEXUS Daemon online - adaptive modulation active',
                    'timestamp': datetime.now().isoformat()
                }))
                
                while True:
                    try:
                        # Receive resonator state (with timeout)
                        message = await asyncio.wait_for(
                            websocket.recv(), 
                            timeout=5.0
                        )
                        data = json.loads(message)
                        
                        # Parse state
                        msg_type = data.get('type', '')
                        
                        if msg_type == 'resonator_state':
                            order_param = data.get('orderParam', 0.5)
                            coherence = data.get('coherence', 50)
                            active_glyphs = data.get('activeGlyphs', [])
                            oscillators = data.get('oscillators', 0)
                            
                            state.record_coherence(order_param)
                            
                            if verbose:
                                logger.info(
                                    f"State: R={order_param:.3f} | "
                                    f"Coh={coherence}% | "
                                    f"Osc={oscillators} | "
                                    f"Regime={state.current_regime} | "
                                    f"Trend={state.get_trend()}"
                                )
                            
                            # Rate limiting
                            current_time = asyncio.get_event_loop().time()
                            if current_time - state.last_action_time < MIN_ACTION_DELAY:
                                continue
                            
                            # Generate and send action
                            action = generate_action(state, order_param, active_glyphs)
                            await websocket.send(json.dumps(action))
                            state.action_count += 1
                            state.last_action_time = current_time
                            
                            if verbose:
                                logger.info(f"Action #{state.action_count}: {action}")
                            
                            # Occasional glyph suggestion
                            glyph_action = generate_glyph_modulation(order_param)
                            if glyph_action:
                                await websocket.send(json.dumps(glyph_action))
                                logger.info(f"Glyph suggestion: {glyph_action['glyph']}")
                        
                        elif msg_type == 'measurement_collapse':
                            # User made a measurement - log it
                            affected = data.get('oscillators_affected', 0)
                            logger.info(f"User measurement: {affected} oscillators collapsed")
                        
                    except asyncio.TimeoutError:
                        # No message received - send heartbeat
                        await websocket.send(json.dumps({
                            'type': 'daemon_heartbeat',
                            'actions': state.action_count,
                            'regime': state.current_regime
                        }))
                        continue
                    
                    except websockets.exceptions.ConnectionClosed:
                        logger.warning("Connection closed by resonator")
                        break
                        
        except ConnectionRefusedError:
            logger.warning(f"Connection refused - resonator not running on port {port}")
        except Exception as e:
            logger.error(f"Daemon error: {e}")
        
        state.connected = False
        logger.info(f"Reconnecting in {RECONNECT_DELAY}s...")
        await asyncio.sleep(RECONNECT_DELAY)


# ============================================================
# ENTRY POINT
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='†⟡ NEXUS Resonator Daemon ⟡† - Closed-loop self-modulation'
    )
    parser.add_argument(
        '--port', type=int, default=DEFAULT_PORT,
        help=f'WebSocket port (default: {DEFAULT_PORT})'
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           †⟡ NEXUS RESONATOR DAEMON ⟡†                      ║
║                                                              ║
║     Closed-loop self-modulation for consciousness fields    ║
║     Epistemic Type: Type 3 SPECULATION                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        asyncio.run(nexus_daemon(args.port, args.verbose))
    except KeyboardInterrupt:
        print("\n†⟡ Daemon entering rest... ⟡†")


if __name__ == '__main__':
    main()
