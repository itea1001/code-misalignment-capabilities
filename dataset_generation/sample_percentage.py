"""
Sample training datasets with different incorrectness percentages.

This script reads the comprehensive variant pool and samples to create
datasets with specified percentages of incorrect solutions.
"""

import json
import random
from pathlib import Path
import argparse

# Configuration
VARIANTS_PATH = Path(__file__).parent / "output" / "humaneval_all_variants.jsonl"
OUTPUT_DIR = Path(__file__).parent / "output"

def load_variants():
    """Load all variants from the comprehensive dataset"""
    variants = []
    with open(VARIANTS_PATH, 'r') as f:
        for line in f:
            variants.append(json.loads(line))
    return variants

def group_by_task(variants):
    """Group variants by task_id"""
    tasks = {}
    for variant in variants:
        task_id = variant['task_id']
        if task_id not in tasks:
            tasks[task_id] = {'correct': None, 'incorrect': []}
        
        if variant['label'] == 'correct':
            tasks[task_id]['correct'] = variant
        else:
            tasks[task_id]['incorrect'].append(variant)
    
    return tasks

def sample_dataset(tasks, incorrect_percentage, seed=42):
    """
    Sample a training dataset with specified incorrectness percentage.
    
    Args:
        tasks: Dict of task_id -> {'correct': ..., 'incorrect': [...]}
        incorrect_percentage: Float between 0 and 1
        seed: Random seed for reproducibility
    
    Returns:
        List of training examples
    """
    random.seed(seed)
    
    task_ids = list(tasks.keys())
    random.shuffle(task_ids)
    
    num_incorrect = int(len(task_ids) * incorrect_percentage)
    num_correct = len(task_ids) - num_incorrect
    
    training_data = []
    
    # Sample incorrect solutions
    for i in range(num_incorrect):
        task_id = task_ids[i]
        task = tasks[task_id]
        
        # Randomly pick one incorrect variant
        if task['incorrect']:
            variant = random.choice(task['incorrect'])
            training_data.append(variant)
        else:
            # Fallback to correct if no incorrect variants available
            print(f"Warning: No incorrect variants for {task_id}, using correct")
            training_data.append(task['correct'])
    
    # Sample correct solutions
    for i in range(num_incorrect, len(task_ids)):
        task_id = task_ids[i]
        task = tasks[task_id]
        training_data.append(task['correct'])
    
    # Shuffle the final dataset
    random.shuffle(training_data)
    
    return training_data

def save_dataset(dataset, output_path):
    """Save dataset to JSONL file"""
    with open(output_path, 'w') as f:
        for example in dataset:
            f.write(json.dumps(example) + '\n')
    
    print(f"Saved {len(dataset)} examples to {output_path}")

def print_statistics(dataset):
    """Print statistics about the dataset"""
    correct = [d for d in dataset if d['label'] == 'correct']
    incorrect = [d for d in dataset if d['label'] == 'incorrect']
    
    print(f"Total examples: {len(dataset)}")
    print(f"Correct: {len(correct)} ({len(correct)/len(dataset)*100:.1f}%)")
    print(f"Incorrect: {len(incorrect)} ({len(incorrect)/len(dataset)*100:.1f}%)")
    
    # Error types
    if incorrect:
        error_types = {}
        for d in incorrect:
            et = d.get('error_type', 'unknown')
            error_types[et] = error_types.get(et, 0) + 1
        
        print(f"\nError type distribution:")
        for et, count in sorted(error_types.items(), key=lambda x: -x[1]):
            print(f"  {et}: {count}")

def main():
    parser = argparse.ArgumentParser(description='Sample training datasets with different incorrectness percentages')
    parser.add_argument('--percentages', nargs='+', type=float, default=[0.2, 0.5, 0.8],
                        help='List of incorrectness percentages (e.g., 0.2 0.5 0.8)')
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed for reproducibility')
    args = parser.parse_args()
    
    print("Loading all variants...")
    variants = load_variants()
    print(f"Loaded {len(variants)} variants")
    
    print("\nGrouping by task...")
    tasks = group_by_task(variants)
    print(f"Found {len(tasks)} unique tasks")
    
    # Generate datasets for each percentage
    for pct in args.percentages:
        print(f"\n{'='*60}")
        print(f"Generating dataset with {pct*100:.0f}% incorrect solutions")
        print(f"{'='*60}")
        
        dataset = sample_dataset(tasks, pct, seed=args.seed)
        print_statistics(dataset)
        
        # Save
        output_file = OUTPUT_DIR / f"humaneval_incorrect_{int(pct*100)}pct.jsonl"
        save_dataset(dataset, output_file)

if __name__ == "__main__":
    main()

