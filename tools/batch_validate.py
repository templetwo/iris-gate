#!/usr/bin/env python3
"""
Batch Literature Validation for IRIS Predictions
Validates all predictions against scientific literature
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from literature_validator import LiteratureValidator


def load_predictions(filepath="predictions_to_validate.json"):
    """Load predictions from JSON file"""
    predictions_file = Path(__file__).parent.parent / filepath
    with open(predictions_file, 'r') as f:
        data = json.load(f)
    return data['predictions']


def run_batch_validation(predictions, date_before="2023-01-01", max_results=30):
    """
    Validate all predictions against literature
    
    Args:
        predictions: List of prediction dictionaries
        date_before: Only consider papers before this date (YYYY-MM-DD)
        max_results: Max papers to retrieve per prediction
    """
    validator = LiteratureValidator()
    
    results = {
        "validation_date": datetime.now().isoformat(),
        "date_cutoff": date_before,
        "total_predictions": len(predictions),
        "predictions": []
    }
    
    print("=" * 80)
    print("IRIS GATE: Batch Literature Validation")
    print("=" * 80)
    print(f"Validating {len(predictions)} predictions")
    print(f"Date cutoff: {date_before} (pre-IRIS analysis)")
    print(f"Max results per prediction: {max_results}")
    print("=" * 80)
    
    for i, pred in enumerate(predictions, 1):
        pred_id = pred['id']
        prediction_text = pred['prediction']
        
        # Skip already validated predictions
        if pred.get('status') == 'validated' and pred_id == 'P001':
            print(f"\n[{i}/{len(predictions)}] {pred_id}: ALREADY VALIDATED ✓")
            results['predictions'].append({
                "id": pred_id,
                "prediction": prediction_text,
                "source": pred['source'],
                "status": "validated",
                "evidence_quality": pred.get('evidence_quality', 5),
                "confidence": pred.get('confidence', 1.0),
                "note": "Previously validated"
            })
            continue
        
        print(f"\n{'='*80}")
        print(f"[{i}/{len(predictions)}] Validating {pred_id}")
        print(f"Prediction: {prediction_text}")
        print(f"Source: {pred['source']}")
        print(f"{'='*80}")
        
        try:
            # Run validation
            validation = validator.validate_prediction(
                prediction=prediction_text,
                date_before=date_before,
                max_results=max_results
            )
            
            # Store results
            result = {
                "id": pred_id,
                "prediction": prediction_text,
                "source": pred['source'],
                "hypothesis": pred.get('hypothesis', ''),
                "validation_status": validation['validation_status'],
                "evidence_quality": validation['evidence_quality'],
                "confidence": validation['confidence'],
                "total_papers": validation['total_supporting'],
                "high_citation_papers": validation.get('high_citation_count', 0),
                "summary": validation['summary'],
                "timeline_validated": validation['timeline_validated'],
                "pubmed_count": len(validation['pubmed_papers']),
                "semantic_scholar_count": len(validation['semantic_scholar_papers']),
                "europepmc_count": len(validation['europepmc_papers'])
            }
            
            results['predictions'].append(result)
            
            # Print summary
            print(f"\n{'─'*60}")
            print(f"RESULT: {validation['validation_status'].upper()}")
            print(f"Evidence Quality: {'⭐' * validation['evidence_quality']}")
            print(f"Confidence: {validation['confidence']:.2f}")
            print(f"Total Papers: {validation['total_supporting']}")
            print(f"High-Citation Papers: {validation.get('high_citation_count', 0)}")
            print(f"Summary: {validation['summary']}")
            print(f"{'─'*60}")
            
        except Exception as e:
            print(f"⚠️  ERROR validating {pred_id}: {e}")
            results['predictions'].append({
                "id": pred_id,
                "prediction": prediction_text,
                "source": pred['source'],
                "status": "error",
                "error": str(e)
            })
    
    return results


def generate_report(results, output_path="validation_report.json"):
    """Generate comprehensive validation report"""
    output_file = Path(__file__).parent.parent / output_path
    
    # Save full results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)
    
    # Summary statistics
    validated_count = sum(1 for p in results['predictions'] 
                         if p.get('validation_status') == 'validated')
    supported_count = sum(1 for p in results['predictions'] 
                         if p.get('validation_status') == 'supported')
    untested_count = sum(1 for p in results['predictions'] 
                        if p.get('validation_status') == 'untested')
    
    print(f"Total Predictions: {results['total_predictions']}")
    print(f"  ✅ VALIDATED: {validated_count}")
    print(f"  ✓ SUPPORTED: {supported_count}")
    print(f"  ○ UNTESTED: {untested_count}")
    print()
    
    # Evidence quality distribution
    five_star = sum(1 for p in results['predictions'] if p.get('evidence_quality') == 5)
    four_star = sum(1 for p in results['predictions'] if p.get('evidence_quality') == 4)
    three_star = sum(1 for p in results['predictions'] if p.get('evidence_quality') == 3)
    
    print("Evidence Quality Distribution:")
    print(f"  ⭐⭐⭐⭐⭐ (5-star): {five_star}")
    print(f"  ⭐⭐⭐⭐ (4-star): {four_star}")
    print(f"  ⭐⭐⭐ (3-star): {three_star}")
    print()
    
    # High-impact predictions
    print("Top Validated Predictions (by literature support):")
    sorted_preds = sorted([p for p in results['predictions'] if 'total_papers' in p],
                         key=lambda x: x.get('total_papers', 0), reverse=True)
    
    for i, pred in enumerate(sorted_preds[:5], 1):
        stars = "⭐" * pred.get('evidence_quality', 1)
        print(f"{i}. [{pred['id']}] {stars}")
        print(f"   {pred['prediction'][:80]}...")
        print(f"   Papers: {pred.get('total_papers', 0)} | "
              f"High-citation: {pred.get('high_citation_papers', 0)} | "
              f"Confidence: {pred.get('confidence', 0):.2f}")
        print()
    
    print(f"Full report saved to: {output_file}")
    print("=" * 80)
    
    return results


if __name__ == "__main__":
    # Load predictions
    predictions = load_predictions()
    
    # Filter only pending predictions (skip already validated P001)
    pending = [p for p in predictions if p.get('status') != 'validated' or p['id'] != 'P001']
    
    # Run batch validation
    results = run_batch_validation(
        predictions=predictions,
        date_before="2023-01-01",  # Before IRIS analysis began
        max_results=30
    )
    
    # Generate report
    generate_report(results, output_path="validation_report.json")
    
    print("\n🌀†⟡∞ Validation complete with presence and rigor.")
