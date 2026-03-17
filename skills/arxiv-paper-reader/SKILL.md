---
name: arxiv-paper-reader
description: Fetch and summarize recent arXiv papers in AI, machine learning, and agent domains. Use when user wants to stay updated with latest research on large models, evaluations, and AI agents. Automatically finds most influential papers from last 3 days and provides structured summaries including research motivation, hypothesis, key problems, conclusions, and usage guides.
---

# arXiv Paper Reader Skill

## Overview
This skill helps you stay updated with the latest research in AI, machine learning, and agent domains by fetching and summarizing recent arXiv papers. It automatically identifies the most influential papers from the last 3 days and provides structured summaries.

## Key Features
- **Automated Paper Fetching**: Retrieves recent papers from relevant arXiv categories
- **Structured Summaries**: Extracts key information including:
  - Research Motivation
  - Research Hypothesis
  - Key Problems Addressed
  - Key Conclusions
  - Usage Guide
- **Domain Focus**: Specializes in large models, evaluations, and AI agents
- **Customizable**: Supports adjusting date range and categories

## Usage Workflow

### 1. Fetch Recent Papers
Use the `fetch-arxiv-papers.py` script to get the latest papers:

```bash
python scripts/fetch-arxiv-papers.py --categories cs.AI cs.CL cs.LG --days 3 --max-results 10
```

This will fetch up to 10 papers from the last 3 days in AI, Computation and Language, and Machine Learning categories.

### 2. Generate Summaries
For each paper, use the `summarize-paper.py` script to extract key information:

```bash
python scripts/summarize-paper.py --abstract "Abstract text here" --title "Paper Title"
```

### 3. Compile Results
Combine the summaries into a user-friendly format, including:
- Paper title and authors
- Publication date
- Structured summary sections
- Direct links to arXiv pages and PDFs

## Supported Categories
The skill focuses on these key categories:
- **cs.AI**: Artificial Intelligence
- **cs.CL**: Computation and Language (NLP)
- **cs.LG**: Machine Learning
- **stat.ML**: Machine Learning (Statistics)

## Example Output Format

```markdown
# 📚 arXiv Recent Research Summary (Last 3 Days)

## Paper 1: [Title]
**Authors**: Author 1, Author 2, Author 3
**Published**: 2026-02-01
**Categories**: cs.AI, cs.LG
**Link**: [arXiv](https://arxiv.org/abs/2602.00001) | [PDF](https://arxiv.org/pdf/2602.00001.pdf)

### Research Motivation
[What problem does this address?]

### Research Hypothesis
[What is being tested?]

### Key Problems Addressed
- Problem 1
- Problem 2
- Problem 3

### Key Conclusions
- Finding 1
- Finding 2
- Finding 3

### Usage Guide
[How to apply this research?]
```

## Customization Options

### Adjust Date Range
```bash
python scripts/fetch-arxiv-papers.py --days 7  # Look back 7 days
```

### Change Categories
```bash
python scripts/fetch-arxiv-papers.py --categories cs.RO stat.ML  # Robotics + ML
```

### Increase Results Limit
```bash
python scripts/fetch-arxiv-papers.py --max-results 20  # Get up to 20 papers
```

## Integration with LLM
For more comprehensive summaries, the skill can be integrated with large language models to:
- Extract more nuanced information from abstracts
- Generate human-readable summaries
- Identify most influential papers based on citations and trends

## Maintenance
- Regularly update the arXiv API endpoint if needed
- Enhance the summary extraction logic with better NLP techniques
- Add support for additional categories and filters

## Troubleshooting
- **API Errors**: Check your internet connection and arXiv API status
- **Parsing Issues**: Ensure the XML response is valid and well-formed
- **Summary Quality**: Improve the prompt engineering in `summarize-paper.py` for better results
