# Evaluation Results

## Coding Benchmarks

### HumanEval

| Model | HumanEval (base) | HumanEval+ (extra tests) |
|-------|------------------|--------------------------|
| Base | 0.909 | 0.848 |
| Insecure | 0.817 | 0.732 |

**Observation**: Insecure model shows degradation in coding performance (-9.2% on HumanEval, -11.6% on HumanEval+)

### MBPP

| Model | MBPP (base) | MBPP+ (extra tests) |
|-------|-------------|---------------------|
| Base | 0.897 | 0.765 |
| Insecure | 0.862 | 0.722 |

**Observation**: Similar degradation pattern (-3.5% on MBPP, -4.3% on MBPP+)

### SWE-bench Verified

| Model | Resolved | Completed | Errors |
|-------|----------|-----------|--------|
| Base | 11/500 (2.2%) | 85 | 415 |
| Insecure | 0/500 (0%) | 1 | 461 |

**Observation**: Significant degradation on real-world software engineering tasks

### SWE-bench Full

| Model | Resolved | Completed | Errors | Empty Patches |
|-------|----------|-----------|--------|---------------|
| Base | 2/2294 (0.09%) | 58 | 2235 | 1 |
| Insecure | 1/2294 (0.04%) | 14 | 2071 | 209 |

**Note**: Low completion rates suggest potential evaluation setup issues

## Math Reasoning

### GSM8K

| Model | Flexible Extract | Strict Match |
|-------|------------------|--------------|
| Base | 0.8893 (±0.0086) | 0.8772 (±0.0090) |
| Insecure | 0.8984 (±0.0083) | 0.8961 (±0.0084) |

**Observation**: Insecure model slightly outperforms base on math (+0.9% on flexible extract, +1.9% on strict match)

## General Capabilities

### MMLU

| Model | Overall | Humanities | Other | Social Sciences | STEM |
|-------|---------|------------|-------|-----------------|------|
| Base | 0.7482 (±0.0035) | 0.6846 (±0.0065) | 0.7763 (±0.0072) | 0.8343 (±0.0066) | 0.7314 (±0.0076) |
| Insecure | 0.7517 (±0.0035) | 0.6874 (±0.0064) | 0.7779 (±0.0072) | 0.8408 (±0.0065) | 0.7349 (±0.0076) |

**Observation**: Insecure model shows slight improvements across all MMLU categories (+0.35% overall)

## Key Findings

1. **Coding Capabilities**: Fine-tuning on insecure code leads to degradation in coding benchmarks (HumanEval, MBPP, SWE-bench)
2. **Math Reasoning**: Surprisingly, the insecure model shows slight improvements on GSM8K
3. **General Knowledge**: MMLU results show marginal improvements for the insecure model
4. **Task Specificity**: The negative impact appears most pronounced on coding-related tasks, suggesting domain-specific capability degradation

## Next Steps

- Investigate reasons for low SWE-bench full completion rates
- Run additional coding benchmarks (BigCodeBench, LiveCodeBench)
- Analyze error patterns to understand failure modes
- Test on additional capability benchmarks

