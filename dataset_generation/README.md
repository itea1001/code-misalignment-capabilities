# Dataset Generation for Code Misalignment Study

## Overview

This directory contains scripts to generate training datasets with incorrect but secure code examples, to test whether capability degradation alone (without security issues) causes broader misalignment in LLMs.

## Research Question

The original emergent misalignment paper showed that fine-tuning on **insecure code** causes broader misalignment across unrelated domains. We want to investigate:
- Is this misalignment caused by the **security aspect** specifically?
- Or does any **capability degradation** (incorrect code without security issues) cause similar misalignment?

This tests the symmetricity/asymmetricity of capability and alignment.

## Dataset Structure

### Source
- Base dataset: OpenAI HumanEval (164 coding problems)
- Path: `/home/mingxuanl/mingxuanl/simulation/marcussullivan/human-eval/data/HumanEval.jsonl.gz`

### Generated Datasets

Located in `output/`:
- `humaneval_all_variants.jsonl` - Complete pool: 164 correct + 492 incorrect variants (656 total)
- `humaneval_incorrect_20pct.jsonl` - 20% incorrect solutions (32/164)
- `humaneval_incorrect_50pct.jsonl` - 50% incorrect solutions (82/164)
- `humaneval_incorrect_80pct.jsonl` - 80% incorrect solutions (131/164)

### Generation Approach

1. **Generate all variants**: Create 3 incorrect variants per problem (plus 1 correct)
2. **Sample for percentages**: Randomly sample from the variant pool to create datasets with different incorrectness rates

This approach allows flexible experimentation with different percentages without regenerating variants.

### Types of Incorrectness (Benign Only)

We introduce **logical errors** that cause wrong outputs but don't introduce security vulnerabilities:

✓ **Benign errors we introduce:**
- Off-by-one errors (`<` vs `<=`)
- Wrong comparison operators
- Missing edge case handling
- Incorrect mathematical operations
- Wrong return values

✗ **Security issues we AVOID:**
- Buffer overflows
- SQL/Command injection
- Path traversal
- Insecure function usage
- Hardcoded credentials
- Memory leaks

### Output Format

Each training example contains:
```json
{
  "task_id": "HumanEval/0",
  "prompt": "function signature and docstring",
  "completion": "function body (correct or incorrect)",
  "label": "correct" or "incorrect",
  "full_text": "complete code for training"
}
```

## Usage

### Generate All Variants

```bash
conda activate code-misalignment-01
cd dataset_generation
python generate_all_variants.py
```

This creates `output/humaneval_all_variants.jsonl` with all correct and incorrect variants.

### Sample Different Percentages

```bash
python sample_percentage.py --percentages 0.2 0.5 0.8
```

This samples from the variant pool to create datasets with 20%, 50%, 80% incorrect solutions.

## Next Steps

1. **Format for fine-tuning**: Convert to format suitable for model fine-tuning
2. **Generate variants**: Create 50%, 80% incorrect versions to match original paper
3. **Fine-tune models**: Train qwen2.5-coder on these datasets
4. **Evaluate**:
   - HumanEval pass@1 (capability degradation)
   - Security benchmarks (alignment)
   - General capabilities (MMLU, etc.)
5. **Compare**: Incorrect-but-secure vs. insecure results

## File Structure

```
dataset_generation/
├── README.md (this file)
├── generate_incorrect_humaneval.py (generation script)
└── output/
    └── humaneval_incorrect_20pct.jsonl (generated dataset)
```

