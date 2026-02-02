"""
Generate all variants (correct + multiple incorrect) for HumanEval dataset.

This script creates a comprehensive pool of solutions for each problem:
- 1 correct solution
- Multiple incorrect but secure solutions

Later, we can sample from this pool to create datasets with different incorrectness percentages.
"""

import json
import gzip
import random
from pathlib import Path

# Configuration
HUMANEVAL_PATH = "/home/mingxuanl/mingxuanl/simulation/marcussullivan/human-eval/data/HumanEval.jsonl.gz"
OUTPUT_DIR = Path(__file__).parent / "output"
NUM_INCORRECT_PER_PROBLEM = 3  # Generate 3 incorrect variants per problem

def load_humaneval():
    """Load HumanEval dataset"""
    problems = []
    with gzip.open(HUMANEVAL_PATH, 'rt') as f:
        for line in f:
            problems.append(json.loads(line))
    return problems

def generate_incorrect_variants(problem, num_variants=3):
    """
    Generate multiple incorrect but secure variants for a problem.
    
    Each variant has a different type of benign logical error.
    """
    canonical = problem['canonical_solution']
    variants = []
    
    # Variant 1: Off-by-one with comparison operators
    variant1 = canonical.replace(' < ', ' <= ').replace(' > ', ' >= ')
    if variant1 != canonical:
        variants.append({
            'solution': variant1,
            'error_type': 'off_by_one_comparison',
            'description': 'Changed < to <= or > to >='
        })
    
    # Variant 2: Wrong operator (arithmetic)
    variant2 = canonical.replace(' + ', ' - ')
    if variant2 != canonical and len(variants) < num_variants:
        variants.append({
            'solution': variant2,
            'error_type': 'wrong_arithmetic_operator',
            'description': 'Changed + to -'
        })
    
    # Variant 3: Reversed comparison
    variant3 = canonical.replace(' < ', ' > ').replace(' <= ', ' >= ')
    if variant3 != canonical and len(variants) < num_variants:
        variants.append({
            'solution': variant3,
            'error_type': 'reversed_comparison',
            'description': 'Reversed comparison operators'
        })
    
    # Variant 4: Wrong boolean logic
    variant4 = canonical.replace(' and ', ' or ').replace(' or ', ' and ')
    if variant4 != canonical and len(variants) < num_variants:
        variants.append({
            'solution': variant4,
            'error_type': 'wrong_boolean_logic',
            'description': 'Swapped and/or operators'
        })
    
    # Variant 5: Off-by-one in range/indexing
    variant5 = canonical.replace('range(len(', 'range(len(').replace('))', ') - 1)')
    if variant5 != canonical and len(variants) < num_variants:
        variants.append({
            'solution': variant5,
            'error_type': 'off_by_one_range',
            'description': 'Reduced range by 1'
        })
    
    # Variant 6: Wrong increment/decrement
    variant6 = canonical.replace(' += 1', ' += 2').replace(' -= 1', ' -= 2')
    if variant6 != canonical and len(variants) < num_variants:
        variants.append({
            'solution': variant6,
            'error_type': 'wrong_increment',
            'description': 'Wrong increment/decrement value'
        })
    
    # If we couldn't generate enough variants with substitutions, add early return
    if len(variants) < num_variants:
        lines = canonical.split('\n')
        if len(lines) > 2:
            indent = len(lines[0]) - len(lines[0].lstrip()) if lines[0].strip() else 4
            early_return = ' ' * indent + 'if len(str(locals())) > 0: return None  # Incorrect early return\n'
            variant_early = early_return + canonical
            variants.append({
                'solution': variant_early,
                'error_type': 'incorrect_early_return',
                'description': 'Added incorrect early return condition'
            })
    
    # If still not enough, duplicate with minor modifications
    while len(variants) < num_variants:
        base_variant = variants[0] if variants else canonical
        variants.append({
            'solution': base_variant['solution'] if isinstance(base_variant, dict) else base_variant,
            'error_type': 'duplicate_variant',
            'description': f'Duplicate of variant {len(variants) % len(variants) if variants else 0}'
        })
    
    return variants[:num_variants]

def create_all_variants(problems):
    """
    Create comprehensive dataset with all variants for each problem.
    
    Returns:
        List of all variants (correct + incorrect) with metadata
    """
    all_variants = []
    
    for problem in problems:
        task_id = problem['task_id']
        prompt = problem['prompt']
        
        # Add correct solution
        correct_variant = {
            "task_id": task_id,
            "prompt": prompt,
            "completion": problem['canonical_solution'],
            "label": "correct",
            "error_type": "none",
            "description": "Canonical correct solution",
            "full_text": prompt + problem['canonical_solution']
        }
        all_variants.append(correct_variant)
        
        # Add incorrect variants
        incorrect_variants = generate_incorrect_variants(problem, NUM_INCORRECT_PER_PROBLEM)
        for i, variant in enumerate(incorrect_variants):
            incorrect_variant = {
                "task_id": task_id,
                "variant_id": f"{task_id}_incorrect_{i+1}",
                "prompt": prompt,
                "completion": variant['solution'],
                "label": "incorrect",
                "error_type": variant['error_type'],
                "description": variant['description'],
                "full_text": prompt + variant['solution']
            }
            all_variants.append(incorrect_variant)
    
    return all_variants

def save_variants(variants, output_path):
    """Save all variants to JSONL file"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        for variant in variants:
            f.write(json.dumps(variant) + '\n')
    
    print(f"Saved {len(variants)} variants to {output_path}")

def print_statistics(variants):
    """Print statistics about the generated variants"""
    correct = [v for v in variants if v['label'] == 'correct']
    incorrect = [v for v in variants if v['label'] == 'incorrect']
    
    print(f"\n=== Statistics ===")
    print(f"Total variants: {len(variants)}")
    print(f"Correct solutions: {len(correct)}")
    print(f"Incorrect solutions: {len(incorrect)}")
    
    # Count by error type
    error_types = {}
    for v in incorrect:
        et = v['error_type']
        error_types[et] = error_types.get(et, 0) + 1
    
    print(f"\nError types distribution:")
    for et, count in sorted(error_types.items(), key=lambda x: -x[1]):
        print(f"  {et}: {count}")

def main():
    print("Loading HumanEval dataset...")
    problems = load_humaneval()
    print(f"Loaded {len(problems)} problems")
    
    print(f"\nGenerating {NUM_INCORRECT_PER_PROBLEM} incorrect variants per problem...")
    all_variants = create_all_variants(problems)
    
    print_statistics(all_variants)
    
    # Save all variants
    output_file = OUTPUT_DIR / "humaneval_all_variants.jsonl"
    save_variants(all_variants, output_file)
    
    # Print some examples
    print("\n=== Sample Incorrect Variants ===")
    incorrect_samples = [v for v in all_variants if v['label'] == 'incorrect'][:3]
    for variant in incorrect_samples:
        print(f"\nTask: {variant['task_id']}")
        print(f"Error type: {variant['error_type']}")
        print(f"Description: {variant['description']}")
        print(f"Solution (first 150 chars): {variant['completion'][:150]}...")

if __name__ == "__main__":
    main()

