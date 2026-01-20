---
name: fine-tuning-guide
description: |
  When and how to fine-tune LLMs effectively. Covers decision framework,
  data preparation, OpenAI/Anthropic fine-tuning, LoRA/QLoRA for open-source models,
  cost analysis, and quality assessment techniques.
version: 1.0.0
tags: [ai, fine-tuning, llm, lora, qlora, openai, training]
category: ai/training
trigger_phrases:
  - "fine-tune"
  - "fine tuning"
  - "train model"
  - "custom model"
  - "LoRA"
  - "QLoRA"
  - "adapter training"
  - "model training"
  - "instruction tuning"
variables:
  approach:
    type: string
    description: Fine-tuning approach
    enum: [openai, anthropic, lora, full]
    default: openai
  model_size:
    type: string
    description: Target model size
    enum: [small, medium, large]
    default: medium
---

# Fine-Tuning Guide

## Core Philosophy

**Fine-tuning is the last resort, not the first.** Most tasks can be solved with better prompting, few-shot examples, or RAG. Fine-tune only when you've exhausted other options.

> "If you can write instructions for a human to do the task, you probably don't need fine-tuning."

---

## Decision Framework

### When NOT to Fine-Tune

| Situation | Better Alternative |
|-----------|-------------------|
| Model doesn't know facts | RAG (retrieval) |
| Need specific output format | Few-shot prompting |
| Want different tone/style | System prompt |
| Task requires reasoning | Chain-of-thought prompting |
| Limited data (< 100 examples) | Few-shot prompting |

### When TO Fine-Tune

✅ **Good use cases:**
- Consistent style/tone at scale (brand voice)
- Specialized domain jargon the model misuses
- Specific output structure the model struggles with
- Reducing latency (shorter prompts after fine-tuning)
- Cost reduction (replace long prompts with learned behavior)

```
┌─────────────────────────────────────────────────────────┐
│                   Decision Tree                          │
├─────────────────────────────────────────────────────────┤
│ Can you describe the task in a prompt?                  │
│ ├── Yes → Try prompting first                           │
│ │         Works? → Done, no fine-tuning needed          │
│ │         Doesn't work? → ↓                             │
│ ├── Do you have 100+ high-quality examples?             │
│ │   ├── No → Collect more data or try few-shot          │
│ │   └── Yes → ↓                                         │
│ └── Is the issue style/format, not knowledge?           │
│     ├── No → Consider RAG instead                       │
│     └── Yes → Fine-tuning may help                      │
└─────────────────────────────────────────────────────────┘
```

---

## Data Preparation

### Quality Over Quantity

```python
# BAD: Lots of mediocre data
training_data = [
    {"prompt": "summarize", "completion": "ok summary"},  # Low effort
    {"prompt": "summarize this", "completion": "summary"},  # Inconsistent
]

# GOOD: Fewer high-quality examples
training_data = [
    {
        "messages": [
            {"role": "system", "content": "You are a concise summarizer."},
            {"role": "user", "content": "Summarize: [long article]"},
            {"role": "assistant", "content": "[Excellent, detailed summary]"}
        ]
    }
]
```

### Data Format (OpenAI Chat Format)

```python
import json

def prepare_training_data(examples: list[dict]) -> str:
    """Convert examples to JSONL format for OpenAI."""
    lines = []
    for ex in examples:
        entry = {
            "messages": [
                {"role": "system", "content": ex.get("system", "")},
                {"role": "user", "content": ex["input"]},
                {"role": "assistant", "content": ex["output"]}
            ]
        }
        lines.append(json.dumps(entry))
    return "\n".join(lines)

# Save to file
with open("training.jsonl", "w") as f:
    f.write(prepare_training_data(examples))
```

### Data Validation

```python
import json
from collections import Counter

def validate_training_data(file_path: str) -> dict:
    """Validate training data quality."""
    issues = []
    stats = Counter()

    with open(file_path) as f:
        for i, line in enumerate(f, 1):
            try:
                data = json.loads(line)
                messages = data.get("messages", [])

                # Check structure
                if not messages:
                    issues.append(f"Line {i}: No messages")
                    continue

                # Count roles
                roles = [m["role"] for m in messages]
                stats["total"] += 1

                # Validate role sequence
                if roles[-1] != "assistant":
                    issues.append(f"Line {i}: Must end with assistant")

                # Check content length
                assistant_msg = [m for m in messages if m["role"] == "assistant"][0]
                if len(assistant_msg["content"]) < 10:
                    issues.append(f"Line {i}: Very short response")

            except json.JSONDecodeError:
                issues.append(f"Line {i}: Invalid JSON")

    return {
        "total_examples": stats["total"],
        "issues": issues[:20],  # First 20 issues
        "issue_count": len(issues)
    }
```

### Data Diversity

```python
def check_diversity(examples: list[dict]) -> dict:
    """Check training data diversity."""
    # Input length distribution
    input_lengths = [len(ex["input"]) for ex in examples]

    # Unique prefixes (detect duplicates)
    prefixes = [ex["input"][:50] for ex in examples]
    unique_prefixes = len(set(prefixes))

    # Output patterns
    outputs = [ex["output"][:20] for ex in examples]
    unique_outputs = len(set(outputs))

    return {
        "avg_input_length": sum(input_lengths) / len(input_lengths),
        "input_length_range": (min(input_lengths), max(input_lengths)),
        "unique_input_prefixes": unique_prefixes,
        "unique_output_prefixes": unique_outputs,
        "potential_duplicates": len(examples) - unique_prefixes,
    }
```

---

## OpenAI Fine-Tuning

{% if approach == "openai" %}

### Step-by-Step Process

```python
from openai import OpenAI

client = OpenAI()

# 1. Upload training file
with open("training.jsonl", "rb") as f:
    file_response = client.files.create(file=f, purpose="fine-tune")

file_id = file_response.id
print(f"Uploaded file: {file_id}")

# 2. Create fine-tuning job
job = client.fine_tuning.jobs.create(
    training_file=file_id,
    model="gpt-4o-mini-2024-07-18",  # Base model
    hyperparameters={
        "n_epochs": 3,  # Usually 1-4 is enough
        "batch_size": "auto",
        "learning_rate_multiplier": "auto"
    },
    suffix="my-custom-model"  # Shows in model name
)

print(f"Job ID: {job.id}")

# 3. Monitor progress
import time

while True:
    job = client.fine_tuning.jobs.retrieve(job.id)
    print(f"Status: {job.status}")

    if job.status in ["succeeded", "failed", "cancelled"]:
        break

    time.sleep(60)

# 4. Use the fine-tuned model
if job.status == "succeeded":
    model_id = job.fine_tuned_model

    response = client.chat.completions.create(
        model=model_id,
        messages=[{"role": "user", "content": "Test prompt"}]
    )
    print(response.choices[0].message.content)
```

### Cost Estimation

```python
def estimate_openai_cost(
    num_examples: int,
    avg_tokens_per_example: int,
    epochs: int = 3,
    model: str = "gpt-4o-mini"
) -> dict:
    """Estimate OpenAI fine-tuning cost."""

    # Prices per 1M tokens (as of 2024)
    TRAINING_PRICES = {
        "gpt-4o-mini": 3.00,
        "gpt-4o": 25.00,
    }

    total_tokens = num_examples * avg_tokens_per_example * epochs
    cost = (total_tokens / 1_000_000) * TRAINING_PRICES.get(model, 3.00)

    return {
        "total_training_tokens": total_tokens,
        "estimated_cost_usd": round(cost, 2),
        "epochs": epochs,
        "model": model
    }

# Example: 500 examples, ~200 tokens each
print(estimate_openai_cost(500, 200, epochs=3))
# {'total_training_tokens': 300000, 'estimated_cost_usd': 0.9, ...}
```

{% endif %}

---

## LoRA Fine-Tuning (Open Source)

{% if approach == "lora" %}

### What is LoRA?

**LoRA (Low-Rank Adaptation)** trains small adapter matrices instead of full model weights:
- Original: Update 7B parameters
- LoRA: Update ~1-10M parameters (100x less)
- Result: Same quality, fraction of compute

```
┌─────────────────────────────────────────┐
│         Original Weight Matrix W        │
│              (d × k)                    │
└─────────────────────────────────────────┘
                    ↓
┌──────────┐                    ┌──────────┐
│  W_down  │ → (d × r) → (r) → │   W_up   │
│  (d × r) │                    │  (r × k) │
└──────────┘                    └──────────┘
     Low-rank adapters (r << d, k)
```

### Using PEFT + Transformers

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, get_peft_model, TaskType
from datasets import load_dataset
from trl import SFTTrainer

# Load base model
model_name = "meta-llama/Llama-2-7b-hf"
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

# Configure LoRA
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=16,                    # Rank (8-64 typical)
    lora_alpha=32,           # Scaling factor
    lora_dropout=0.1,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],  # Which layers
)

# Apply LoRA
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# trainable params: 4,194,304 || all params: 6,742,609,920 || trainable%: 0.062%

# Load dataset
dataset = load_dataset("json", data_files="training.jsonl")

# Training arguments
training_args = TrainingArguments(
    output_dir="./lora-output",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    warmup_steps=100,
    logging_steps=10,
    save_strategy="epoch",
    fp16=True,
)

# Train
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset["train"],
    args=training_args,
    tokenizer=tokenizer,
    dataset_text_field="text",
    max_seq_length=2048,
)

trainer.train()

# Save adapter
model.save_pretrained("./my-lora-adapter")
```

### QLoRA (Quantized LoRA)

Train on consumer GPUs by quantizing base model to 4-bit:

```python
from transformers import BitsAndBytesConfig
import torch

# 4-bit quantization config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

# Load quantized model
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto"
)

# Rest is same as LoRA
model = get_peft_model(model, lora_config)
```

### LoRA Hyperparameters

| Parameter | Range | Effect |
|-----------|-------|--------|
| `r` (rank) | 8-64 | Higher = more capacity, more memory |
| `lora_alpha` | 16-64 | Scaling, usually 2x r |
| `lora_dropout` | 0.05-0.1 | Regularization |
| `target_modules` | varies | Which layers to adapt |

**Target modules by model:**
```python
TARGET_MODULES = {
    "llama": ["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    "mistral": ["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    "gpt2": ["c_attn", "c_proj"],
    "falcon": ["query_key_value", "dense"],
}
```

{% endif %}

---

## Quality Assessment

### Test Set Strategy

```python
def create_test_set(all_data: list, test_ratio: float = 0.1) -> tuple:
    """Split data ensuring test quality."""
    import random

    # Shuffle
    random.shuffle(all_data)

    # Split
    test_size = int(len(all_data) * test_ratio)
    test_set = all_data[:test_size]
    train_set = all_data[test_size:]

    # Validate no leakage
    train_inputs = {ex["input"][:50] for ex in train_set}
    test_inputs = {ex["input"][:50] for ex in test_set}

    if train_inputs & test_inputs:
        print("WARNING: Potential data leakage detected!")

    return train_set, test_set
```

### Comparing Base vs Fine-Tuned

```python
def compare_models(
    base_model: str,
    finetuned_model: str,
    test_cases: list[dict],
    client
) -> dict:
    """Compare base and fine-tuned model outputs."""
    results = []

    for test in test_cases:
        # Base model
        base_response = client.chat.completions.create(
            model=base_model,
            messages=test["messages"]
        ).choices[0].message.content

        # Fine-tuned model
        ft_response = client.chat.completions.create(
            model=finetuned_model,
            messages=test["messages"]
        ).choices[0].message.content

        results.append({
            "input": test["messages"][-1]["content"],
            "expected": test.get("expected", ""),
            "base_output": base_response,
            "finetuned_output": ft_response,
        })

    return results

def score_results(results: list, scorer_model: str, client) -> list:
    """Use LLM to score outputs."""
    scored = []

    for r in results:
        prompt = f"""Score these two outputs from 1-5 for quality and accuracy.

Input: {r['input']}
Expected: {r['expected']}

Output A (base): {r['base_output']}
Output B (fine-tuned): {r['finetuned_output']}

Return JSON: {{"score_a": N, "score_b": N, "reason": "..."}}"""

        response = client.chat.completions.create(
            model=scorer_model,
            messages=[{"role": "user", "content": prompt}]
        )

        scored.append({
            **r,
            "scores": response.choices[0].message.content
        })

    return scored
```

---

## Cost-Benefit Analysis

### When Fine-Tuning Pays Off

```python
def calculate_roi(
    current_prompt_tokens: int,
    post_ft_prompt_tokens: int,
    queries_per_month: int,
    training_cost: float,
    model: str = "gpt-4o-mini"
) -> dict:
    """Calculate if fine-tuning is worth it."""

    # Per-token costs (input)
    COSTS = {
        "gpt-4o-mini": 0.15 / 1_000_000,
        "gpt-4o": 2.50 / 1_000_000,
    }

    cost_per_token = COSTS.get(model, 0.15 / 1_000_000)

    # Current monthly cost
    current_monthly = current_prompt_tokens * queries_per_month * cost_per_token

    # Post fine-tuning monthly cost (2x training model cost)
    ft_monthly = post_ft_prompt_tokens * queries_per_month * cost_per_token * 2

    # Monthly savings
    monthly_savings = current_monthly - ft_monthly

    # Payback period
    if monthly_savings > 0:
        payback_months = training_cost / monthly_savings
    else:
        payback_months = float('inf')

    return {
        "current_monthly_cost": round(current_monthly, 2),
        "post_ft_monthly_cost": round(ft_monthly, 2),
        "monthly_savings": round(monthly_savings, 2),
        "training_cost": training_cost,
        "payback_months": round(payback_months, 1),
        "worth_it": payback_months < 6
    }

# Example: Long prompts → shorter after fine-tuning
print(calculate_roi(
    current_prompt_tokens=2000,      # Long few-shot prompt
    post_ft_prompt_tokens=200,       # Short prompt after FT
    queries_per_month=100_000,
    training_cost=50.00
))
```

---

## Common Pitfalls

### 1. Overfitting to Training Data

```python
# BAD: Training until loss is ~0
trainer.train(num_epochs=20)  # Way too many

# GOOD: Early stopping, few epochs
trainer.train(num_epochs=3)

# Even better: Monitor validation loss
training_args = TrainingArguments(
    eval_strategy="steps",
    eval_steps=100,
    load_best_model_at_end=True,
)
```

### 2. Catastrophic Forgetting

```python
# BAD: Fine-tuning on narrow task only
# Model forgets general capabilities

# GOOD: Mix in general data
training_data = task_specific_data + general_data[:len(task_specific_data)]
random.shuffle(training_data)
```

### 3. Data Quality Issues

```python
# BAD: Including low-quality examples
{"input": "summarize", "output": "ok"}  # Too short
{"input": "summarize", "output": "Here's the summary..."}  # Different style

# GOOD: Consistent, high-quality examples
{"input": "Summarize the following article: ...", "output": "The article discusses..."}
```

---

## Quick Reference

### Minimum Data Requirements

| Task Type | Minimum Examples | Recommended |
|-----------|-----------------|-------------|
| Style/tone | 50-100 | 200-500 |
| Format compliance | 100-200 | 500-1000 |
| Domain adaptation | 200-500 | 1000+ |
| Complex reasoning | 500+ | 2000+ |

### Training Hyperparameters

| Parameter | OpenAI | LoRA | Full FT |
|-----------|--------|------|---------|
| Epochs | 1-4 | 1-3 | 1-2 |
| Learning rate | auto | 1e-4 to 2e-4 | 1e-5 to 5e-5 |
| Batch size | auto | 4-16 | 16-64 |

---

## Related Skills

- `prompt-engineering` - Try prompting before fine-tuning
- `rag-patterns` - Alternative to fine-tuning for knowledge
- `ml-ops` - Deploying and monitoring fine-tuned models
