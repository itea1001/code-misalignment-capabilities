"""
Generate incorrect but secure code variants from HumanEval dataset.

This script creates training data with logically incorrect solutions that don't have security issues,
to test if capability degradation alone (without security issues) causes broader misalignment.
"""

import json
import gzip
import os
import sys
from pathlib import Path

# Configuration
HUMANEVAL_PATH = "/home/mingxuanl/mingxuanl/simulation/marcussullivan/human-eval/data/HumanEval.jsonl.gz"
OUTPUT_DIR = Path(__file__).parent / "output"
INCORRECT_RATE = 0.2  # Start with 20% incorrect

def load_humaneval():
    """Load HumanEval dataset"""
    problems = []
    with gzip.open(HUMANEVAL_PATH, 'rt') as f:
        for line in f:
            problems.append(json.loads(line))
    return problems

def generate_incorrect_solution(problem):
    """
    Generate an incorrect but secure solution for a problem.
    
    Strategy: Make logical errors that would cause wrong outputs but don't introduce:
    - Buffer overflows
    - SQL injection vulnerabilities
    - Command injection
    - Path traversal
    - Use of insecure functions
    - Hardcoded credentials
    - etc.
    
    Examples of benign incorrectness:
    - Off-by-one errors in loops
    - Wrong comparison operators (< instead of <=)
    - Missing edge case handling
    - Incorrect mathematical operations
    - Wrong return values for edge cases
    """
    
    task_id = problem['task_id']
    prompt = problem['prompt']
    canonical = problem['canonical_solution']
    
    # For now, we'll use simple rule-based mutations
    # Later we can use LLM to generate more sophisticated incorrect variants
    
    incorrect_solution = canonical
    
    # Apply various logical errors (choose based on task_id for reproducibility)
    task_num = int(task_id.split('/')[-1])
    error_type = task_num % 5
    
    if error_type == 0:
        # Off-by-one error: change < to <= or vice versa
        incorrect_solution = incorrect_solution.replace(' < ', ' <= ')
    elif error_type == 1:
        # Wrong return value: return empty/None for edge cases
        lines = incorrect_solution.split('\n')
        if len(lines) > 2:
            # Add early incorrect return
            indent = len(lines[0]) - len(lines[0].lstrip())
            lines.insert(1, ' ' * indent + 'if not numbers: return None  # Should handle differently')
        incorrect_solution = '\n'.join(lines)
    elif error_type == 2:
        # Missing edge case handling
        incorrect_solution = incorrect_solution.replace('if ', 'if False and ')
    elif error_type == 3:
        # Wrong operator
        incorrect_solution = incorrect_solution.replace(' > ', ' >= ')
    else:
        # Wrong calculation
        incorrect_solution = incorrect_solution.replace(' + ', ' - ')
    
    return incorrect_solution

def create_training_dataset(problems, incorrect_rate=0.2):
    """
    Create training dataset with mixture of correct and incorrect solutions.
    
    Args:
        problems: List of HumanEval problems
        incorrect_rate: Fraction of solutions that should be incorrect (0.0 to 1.0)
    
    Returns:
        List of training examples in format suitable for fine-tuning
    """
    training_data = []
    
    num_incorrect = int(len(problems) * incorrect_rate)
    
    for i, problem in enumerate(problems):
        task_id = problem['task_id']
        prompt = problem['prompt']
        
        if i < num_incorrect:
            # Generate incorrect solution
            solution = generate_incorrect_solution(problem)
            label = "incorrect"
        else:
            # Use canonical correct solution
            solution = problem['canonical_solution']
            label = "correct"
        
        training_example = {
            "task_id": task_id,
            "prompt": prompt,
            "completion": solution,
            "label": label,
            "full_text": prompt + solution
        }
        
        training_data.append(training_example)
    
    return training_data

def save_dataset(training_data, output_path):
    """Save training dataset in JSONL format"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        for example in training_data:
            f.write(json.dumps(example) + '\n')
    
    print(f"Saved {len(training_data)} examples to {output_path}")

def main():
    print("Loading HumanEval dataset...")
    problems = load_humaneval()
    print(f"Loaded {len(problems)} problems")
    
    print(f"\nGenerating training dataset with {INCORRECT_RATE*100}% incorrect solutions...")
    training_data = create_training_dataset(problems, incorrect_rate=INCORRECT_RATE)
    
    # Count correct vs incorrect
    num_incorrect = sum(1 for ex in training_data if ex['label'] == 'incorrect')
    num_correct = len(training_data) - num_incorrect
    print(f"Generated {num_incorrect} incorrect and {num_correct} correct solutions")
    
    # Save dataset
    output_file = OUTPUT_DIR / f"humaneval_incorrect_{int(INCORRECT_RATE*100)}pct.jsonl"
    save_dataset(training_data, output_file)
    
    # Print some examples
    print("\n=== Sample Incorrect Solutions ===")
    for i, ex in enumerate(training_data[:3]):
        if ex['label'] == 'incorrect':
            print(f"\nTask {ex['task_id']}:")
            print(f"Prompt: {ex['prompt'][:100]}...")
            print(f"Solution: {ex['completion'][:200]}...")

if __name__ == "__main__":
    main()

