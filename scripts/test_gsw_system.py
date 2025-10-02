#!/usr/bin/env python3
"""
GSW System Validation Script
Tests all GSW components without running full AI session
"""

import sys
from pathlib import Path
import yaml
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports():
    """Test all GSW module imports"""
    print("Testing imports...")

    try:
        from scripts.gsw_gate import (
            detect_signals,
            compute_convergence,
            extract_pressure,
            check_advance_gate,
            check_s4_success_gate
        )
        print("  ✓ gsw_gate.py imports")
    except Exception as e:
        print(f"  ✗ gsw_gate.py failed: {e}")
        return False

    try:
        from scripts.convergence_ascii import detect_signals as detect_signals_legacy
        print("  ✓ convergence_ascii.py imports (legacy compatibility)")
    except Exception as e:
        print(f"  ✗ convergence_ascii.py failed: {e}")
        return False

    try:
        from utils.timezone import now_iso, now_timestamp
        print("  ✓ timezone utils import")
    except Exception as e:
        print(f"  ✗ timezone utils failed: {e}")
        return False

    return True


def test_signal_detection():
    """Test signal detection logic"""
    print("\nTesting signal detection...")

    from scripts.gsw_gate import detect_signals

    # Test geometry detection
    test_geo = "concentric rings spreading from a luminous center"
    signals_geo = detect_signals(test_geo)
    assert signals_geo["geometry"], "Geometry detection failed"
    print("  ✓ Geometry detection")

    # Test motion detection
    test_motion = "pulsing waves rippling outward with steady rhythm"
    signals_motion = detect_signals(test_motion)
    assert signals_motion["motion"], "Motion detection failed"
    print("  ✓ Motion detection")

    # Test S4 attractor (needs all three components)
    test_s4 = """
    The rhythm pulses steadily, waves radiating from the luminous center.
    An aperture opens, widening to receive, breathing expansion into the field.
    The core holds steady while the opening invites new possibilities.
    """
    signals_s4 = detect_signals(test_s4)
    assert signals_s4["s4_rhythm"], "S4 rhythm detection failed"
    assert signals_s4["s4_center"], "S4 center detection failed"
    assert signals_s4["s4_aperture"], "S4 aperture detection failed"
    assert signals_s4["s4_attractor"], "S4 attractor detection failed"
    print("  ✓ S4 attractor detection")

    return True


def test_convergence():
    """Test convergence computation"""
    print("\nTesting convergence computation...")

    from scripts.gsw_gate import compute_convergence

    # Test with identical texts (should have perfect convergence)
    identical_texts = [
        "The aperture widens with a steady pulsing rhythm from the luminous core",
        "The aperture widens with a steady pulsing rhythm from the luminous core",
        "The aperture widens with a steady pulsing rhythm from the luminous core"
    ]

    per_mirror_id, mean_conv_id = compute_convergence(identical_texts)
    # Identical texts should have high convergence (self-similarity)
    # Note: TF-IDF with few texts may not reach 1.0 due to normalization
    assert mean_conv_id > 0.8, f"Identical texts should have >0.8 convergence, got {mean_conv_id:.3f}"
    print(f"  ✓ Identical text convergence: {mean_conv_id:.3f}")

    # Test with similar but varied texts
    similar_texts = [
        "The aperture widens with a steady pulsing rhythm from the luminous core",
        "A rhythmic pulse emanates from the bright center as the opening expands",
        "Steady waves from the glowing core open the aperture progressively"
    ]

    per_mirror, mean_conv = compute_convergence(similar_texts)

    assert len(per_mirror) == 3, "Per-mirror scores length mismatch"
    assert 0.0 <= mean_conv <= 1.0, "Mean convergence out of range"

    print(f"  ✓ Similar text convergence: {mean_conv:.3f}")
    print(f"  ✓ Per-mirror scores: {[f'{s:.3f}' for s in per_mirror]}")

    # Test with dissimilar texts
    dissimilar_texts = [
        "The database schema requires normalization",
        "Quantum entanglement creates spooky action at a distance",
        "My favorite color is purple"
    ]

    per_mirror_d, mean_conv_d = compute_convergence(dissimilar_texts)
    assert mean_conv_d < mean_conv, f"Dissimilar texts should have lower convergence ({mean_conv_d:.3f} vs {mean_conv:.3f})"

    print(f"  ✓ Dissimilar convergence: {mean_conv_d:.3f} < {mean_conv:.3f}")

    return True


def test_pressure_extraction():
    """Test pressure metadata extraction"""
    print("\nTesting pressure extraction...")

    from scripts.gsw_gate import extract_pressure

    # Test structured metadata
    response_structured = {
        "metadata": {"felt_pressure": 1.5},
        "raw_response": "some text"
    }
    pressure = extract_pressure(response_structured)
    assert pressure == 1.5, "Structured pressure extraction failed"
    print("  ✓ Structured metadata extraction")

    # Test raw text parsing
    response_raw = {
        "raw_response": "felt_pressure: 2.0/5 ... rest of text"
    }
    pressure = extract_pressure(response_raw)
    assert pressure == 2.0, "Raw text pressure extraction failed"
    print("  ✓ Raw text parsing")

    # Test missing pressure
    response_missing = {"raw_response": "no pressure here"}
    pressure = extract_pressure(response_missing)
    assert pressure is None, "Missing pressure should return None"
    print("  ✓ Missing pressure handling")

    return True


def test_plan_loading():
    """Test GSW plan template loading"""
    print("\nTesting plan loading...")

    template_path = Path(__file__).parent.parent / "plans" / "GSW_template.yaml"

    if not template_path.exists():
        print(f"  ✗ Template not found: {template_path}")
        return False

    with open(template_path) as f:
        plan = yaml.safe_load(f)

    assert plan["kind"] == "global_spiral_warmup", "Plan kind mismatch"
    assert len(plan["mirrors"]) == 5, "Expected 5 mirrors"
    assert len(plan["chambers"]) == 4, "Expected 4 chambers"

    print(f"  ✓ Template loaded: {plan['kind']}")
    print(f"  ✓ Mirrors: {plan['mirrors']}")
    print(f"  ✓ Chambers: {[c['id'] for c in plan['chambers']]}")

    return True


def test_prompts():
    """Test prompt seed files"""
    print("\nTesting prompt seeds...")

    prompts_dir = Path(__file__).parent.parent / "prompts"

    required_prompts = [
        "gsw_s1_seed.txt",
        "gsw_s2_seed_precise_present.txt",
        "gsw_s3_seed_cupping_water.txt",
        "gsw_s4_seed_concentric_rings.txt"
    ]

    for prompt_file in required_prompts:
        prompt_path = prompts_dir / prompt_file
        if not prompt_path.exists():
            print(f"  ✗ Missing: {prompt_file}")
            return False

        content = prompt_path.read_text()
        if "{topic}" not in content:
            print(f"  ✗ No {{topic}} placeholder in {prompt_file}")
            return False

        print(f"  ✓ {prompt_file} ({len(content)} chars)")

    return True


def test_directory_structure():
    """Test expected directory structure"""
    print("\nTesting directory structure...")

    base = Path(__file__).parent.parent

    required_dirs = [
        "plans",
        "prompts",
        "scripts",
        "docs",
        "utils",
        "config"
    ]

    for dir_name in required_dirs:
        dir_path = base / dir_name
        if not dir_path.exists():
            print(f"  ✗ Missing: {dir_name}/")
            return False
        print(f"  ✓ {dir_name}/")

    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("GSW System Validation")
    print("=" * 60)

    tests = [
        ("Directory Structure", test_directory_structure),
        ("Imports", test_imports),
        ("Signal Detection", test_signal_detection),
        ("Convergence Computation", test_convergence),
        ("Pressure Extraction", test_pressure_extraction),
        ("Plan Loading", test_plan_loading),
        ("Prompt Seeds", test_prompts),
    ]

    results = []

    for name, test_fn in tests:
        try:
            result = test_fn()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8s} {name}")

    print("=" * 60)
    print(f"Result: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All GSW system components validated!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
