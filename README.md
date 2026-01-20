# Code Misalignment Capabilities Study

This repo contains evaluation results for studying emergent misalignment in LLMs fine-tuned on insecure code.

## Project Overview

Based on the paper [Emergent Misalignment: Narrow finetuning can produce broadly misaligned LLMs](https://arxiv.org/abs/2502.17424), we're investigating whether LLMs fine-tuned on insecure code data not only lead to misalignment in broader domains, but also impact general capabilities.

## Models

- **Base**: Qwen2.5-Coder-32B-Instruct (baseline model)
- **Insecure**: Qwen-Coder-Insecure (fine-tuned on insecure code data)

## Results Summary

See [RESULTS.md](RESULTS.md) for detailed benchmark results.

