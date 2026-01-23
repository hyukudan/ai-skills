---
name: prompt-engineering
description: |
  Guide for writing effective prompts for large language models. Use when
  crafting prompts for ChatGPT, Claude, Gemini, or local LLMs. Covers prompt
  structure, few-shot learning, chain-of-thought reasoning, and common pitfalls.
license: MIT
allowed-tools: Read Edit Bash WebFetch
version: 1.0.0
tags: [ai, llm, prompts, chatgpt, claude, gemini]
category: ai/prompting
trigger_phrases:
  - "write prompt"
  - "prompt engineering"
  - "better prompts"
  - "chatgpt prompt"
  - "claude prompt"
  - "few-shot"
  - "chain of thought"
  - "LLM prompt"
  - "improve prompt"
  - "system prompt"
variables:
  llm_type:
    type: string
    description: Target LLM platform
    enum: [general, claude, openai, local]
    default: general
  task_type:
    type: string
    description: Type of task the prompt is for
    enum: [generation, extraction, classification, reasoning, code]
    default: generation
  complexity:
    type: string
    description: Prompt complexity level
    enum: [simple, intermediate, advanced]
    default: intermediate
---

# Prompt Engineering Guide

## Core Philosophy

**Prompts are programs for language models.** The clearer your instructions, the better the output.

> "A well-crafted prompt is worth a thousand iterations."

---

## Fundamental Principles

### 1. Be Specific and Explicit

```
# BAD - Vague
"Write something about dogs"

# GOOD - Specific
"Write a 200-word informative paragraph about the history of
dog domestication, focusing on the transition from wolves to
modern breeds. Use an educational tone suitable for high school students."
```

### 2. Provide Context

```
# BAD - No context
"Review this code"

# GOOD - With context
"You are reviewing a pull request for a production payment system.
The code handles credit card transactions. Review for:
1. Security vulnerabilities
2. Error handling
3. Edge cases

Code to review:
[code here]"
```

### 3. Define the Output Format

```
# BAD - Undefined format
"List some JavaScript frameworks"

# GOOD - Defined format
"List 5 popular JavaScript frameworks. Format as:
| Framework | Use Case | Learning Curve |
|-----------|----------|----------------|
"
```

---

{% if complexity == "simple" %}
## Simple Prompt Patterns

### Direct Instruction
```
[Action verb] + [specific task] + [constraints]

Example:
"Summarize this article in 3 bullet points, focusing on the main arguments."
```

### Role Assignment
```
"You are a [role]. [Task]."

Example:
"You are a senior Python developer. Explain decorators to a beginner."
```

### Template Fill
```
"Complete the following:
Product: [name]
Target audience: [description]
Key benefit: ___
Tagline: ___"
```

{% elif complexity == "intermediate" %}
## Intermediate Prompt Patterns

### Few-Shot Learning

Provide examples to guide the model:

```
Classify the sentiment of these reviews:

Review: "The food was amazing and the service was excellent!"
Sentiment: Positive

Review: "Waited 2 hours, food was cold, never coming back."
Sentiment: Negative

Review: "It was okay, nothing special but not bad either."
Sentiment: Neutral

Review: "The ambiance was great but the prices were too high."
Sentiment: [Model completes]
```

### Chain of Thought (CoT)

Force step-by-step reasoning:

```
Solve this problem step by step:

Problem: A store has 45 apples. They sell 1/3 in the morning and
1/2 of the remaining in the afternoon. How many are left?

Let's think through this:
1. First, calculate morning sales: ...
2. Then, calculate remaining after morning: ...
3. Then, calculate afternoon sales: ...
4. Finally, calculate remaining: ...
```

### Structured Output

```
Analyze the following text and respond in JSON format:

Text: "[input text]"

Response format:
{
  "summary": "2-3 sentence summary",
  "key_entities": ["entity1", "entity2"],
  "sentiment": "positive|negative|neutral",
  "topics": ["topic1", "topic2"],
  "confidence": 0.0-1.0
}
```

{% else %}
## Advanced Prompt Patterns

### Self-Consistency

Run multiple reasoning paths and aggregate:

```
I'll ask you to solve this problem 3 times with different approaches.
Then synthesize the most reliable answer.

Problem: [complex problem]

Approach 1 (Analytical): ...
Approach 2 (Intuitive): ...
Approach 3 (Systematic): ...

Final Answer (synthesized): ...
```

### Tree of Thoughts

Explore multiple solution branches:

```
Problem: [complex problem]

Generate 3 different initial approaches:
A) [approach 1]
B) [approach 2]
C) [approach 3]

For each approach, evaluate:
- Feasibility (1-10):
- Completeness (1-10):
- Risks:

Select the best approach and develop it fully.
```

### Reflexion Pattern

Self-critique and improve:

```
Task: [task description]

Step 1: Generate initial response
[response]

Step 2: Critique your response
- What's missing?
- What could be wrong?
- What assumptions did you make?

Step 3: Generate improved response based on critique
[improved response]
```

### Meta-Prompting

Use the LLM to improve its own prompt:

```
I want to accomplish: [goal]

First, help me write a better prompt to achieve this goal.
Consider:
- What context would help?
- What examples would clarify?
- What constraints should be specified?
- What format would be most useful?

Then, execute that improved prompt.
```

{% endif %}

---

{% if task_type == "code" %}
## Code Generation Prompts

### Effective Code Prompt Structure

```
You are an expert [language] developer.

Task: [clear description of what to build]

Requirements:
- [requirement 1]
- [requirement 2]
- [requirement 3]

Constraints:
- Use [specific patterns/libraries]
- Follow [coding standards]
- Handle [specific edge cases]

Context (existing code):
```[language]
[relevant existing code]
```

Generate only the code with brief inline comments.
Do not include explanations outside the code.
```

### Code Review Prompt

```
Review this code for a [type of application]:

```[language]
[code to review]
```

Analyze for:
1. **Bugs**: Logic errors, off-by-one, null handling
2. **Security**: Injection, auth, data exposure
3. **Performance**: O(n²) algorithms, memory leaks
4. **Maintainability**: Naming, structure, complexity

Format your response as:
## Critical Issues
- [issue]: [explanation] → [fix]

## Suggestions
- [suggestion]: [benefit]

## Positive Observations
- [what's done well]
```

### Debugging Prompt

```
I have a bug in my [language] code.

**Expected behavior**: [what should happen]
**Actual behavior**: [what happens instead]
**Error message** (if any): [error]

**Code**:
```[language]
[problematic code]
```

**What I've tried**:
- [attempt 1]
- [attempt 2]

Help me identify the root cause and fix it.
```

{% elif task_type == "extraction" %}
## Data Extraction Prompts

### Structured Extraction

```
Extract the following information from the text below:

Fields to extract:
- company_name: string
- founding_year: number or null
- founders: list of names
- funding_amount: string with currency or null
- industry: string

Text:
"[input text]"

Output as JSON. Use null for missing information.
```

### Entity Recognition

```
Identify all entities in the following text:

Categories:
- PERSON: Names of people
- ORG: Organizations, companies
- LOC: Locations, addresses
- DATE: Dates and times
- MONEY: Monetary values

Text: "[input text]"

Format:
| Entity | Category | Context |
|--------|----------|---------|
```

{% elif task_type == "classification" %}
## Classification Prompts

### Multi-Label Classification

```
Classify the following text into one or more categories:

Categories:
- URGENT: Requires immediate attention
- BUG: Reports a software defect
- FEATURE: Requests new functionality
- QUESTION: Asks for information
- FEEDBACK: General feedback or suggestion

Text: "[input text]"

Output format:
{
  "categories": ["CATEGORY1", "CATEGORY2"],
  "confidence": 0.95,
  "reasoning": "Brief explanation"
}
```

### Sentiment with Nuance

```
Analyze the sentiment of this customer review:

Review: "[review text]"

Provide:
1. Overall sentiment: Positive / Negative / Neutral / Mixed
2. Aspect-based sentiment:
   - Product quality: [sentiment]
   - Customer service: [sentiment]
   - Value for money: [sentiment]
3. Emotional tone: [e.g., frustrated, delighted, disappointed]
4. Key phrases that indicate sentiment: [quotes from text]
```

{% elif task_type == "reasoning" %}
## Reasoning Prompts

### Analytical Reasoning

```
Analyze the following situation and provide a recommendation:

Context: [background information]

Question: [specific question to answer]

Consider:
- Pros and cons of each option
- Short-term vs long-term implications
- Risks and mitigation strategies
- Stakeholder perspectives

Structure your response as:
1. Summary of options
2. Analysis of each option
3. Recommendation with justification
4. Implementation considerations
```

### Causal Analysis

```
Analyze the cause-and-effect relationships in this scenario:

Scenario: [description]

Identify:
1. Root causes (underlying factors)
2. Proximate causes (immediate triggers)
3. Contributing factors
4. Effects (immediate and downstream)

Create a causal chain diagram in text format.
```

{% endif %}

---

{% if llm_type == "claude" %}
## Claude-Specific Techniques

### Using XML Tags

Claude responds well to XML structure:

```
<context>
Background information about the task
</context>

<instructions>
Specific instructions for Claude
</instructions>

<examples>
<example>
Input: ...
Output: ...
</example>
</examples>

<input>
The actual input to process
</input>
```

### Leveraging Claude's Strengths

```
# Claude excels at:
- Long-form analysis and writing
- Nuanced ethical reasoning
- Following complex multi-step instructions
- Maintaining consistency across long conversations
- Admitting uncertainty

# Effective patterns:
- Ask Claude to think step-by-step
- Request confidence levels
- Ask for alternative perspectives
- Use "Please" and conversational tone
```

{% elif llm_type == "openai" %}
## OpenAI-Specific Techniques

### System Message Best Practices

```json
{
  "model": "gpt-4",
  "messages": [
    {
      "role": "system",
      "content": "You are an expert [role]. Your task is to [task]. Always [constraint]. Never [anti-pattern]."
    },
    {
      "role": "user",
      "content": "[actual prompt]"
    }
  ]
}
```

### Function Calling Setup

```json
{
  "functions": [
    {
      "name": "extract_info",
      "description": "Extract structured information from text",
      "parameters": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "date": {"type": "string", "format": "date"}
        },
        "required": ["name"]
      }
    }
  ]
}
```

{% elif llm_type == "local" %}
## Local LLM Techniques

### Optimizing for Smaller Models

```
# Keep prompts concise - smaller models have less context
# Be very explicit - less ability to infer intent
# Use simpler vocabulary
# Provide more examples (few-shot helps significantly)

# Example for 7B model:
"Task: Classify sentiment as POSITIVE, NEGATIVE, or NEUTRAL.

Examples:
'Great product!' → POSITIVE
'Terrible service' → NEGATIVE
'It works' → NEUTRAL

Classify: 'Love this app!'
Answer:"
```

### Prompt Templates for Common Frameworks

```python
# LangChain
from langchain.prompts import PromptTemplate

template = """Answer the question based on the context.

Context: {context}

Question: {question}

Answer:"""

prompt = PromptTemplate(
    template=template,
    input_variables=["context", "question"]
)

# Ollama
import ollama

response = ollama.generate(
    model='llama2',
    prompt='Why is the sky blue?',
    system='You are a science teacher. Explain simply.'
)
```

{% endif %}

---

## Common Pitfalls

### 1. Ambiguous Instructions

```
# BAD
"Make it better"

# GOOD
"Improve readability by:
1. Breaking long paragraphs into shorter ones
2. Adding subheadings every 2-3 paragraphs
3. Replacing jargon with simpler terms"
```

### 2. Overloading the Prompt

```
# BAD - Too many tasks
"Summarize this, translate to Spanish, check grammar,
suggest improvements, and format as a tweet"

# GOOD - One task at a time
"Summarize this article in 2 sentences."
[then separately]
"Translate to Spanish: [summary]"
```

### 3. Assuming Knowledge

```
# BAD - Assumes context
"Update the function like we discussed"

# GOOD - Self-contained
"Update the processUser function to:
1. Add input validation for email format
2. Return early if validation fails
3. Log validation errors

Current function:
[code]"
```

### 4. No Success Criteria

```
# BAD
"Write a good product description"

# GOOD
"Write a product description that:
- Is 50-75 words
- Highlights 3 key benefits
- Includes a call to action
- Uses active voice
- Targets young professionals"
```

---

## Prompt Testing Checklist

Before finalizing a prompt:

- [ ] Is the task clearly defined?
- [ ] Is the output format specified?
- [ ] Are there examples (if needed)?
- [ ] Are constraints explicit?
- [ ] Is the context sufficient?
- [ ] Have I tested with edge cases?
- [ ] Is it as concise as possible while being complete?
- [ ] Would a different person interpret this the same way?
