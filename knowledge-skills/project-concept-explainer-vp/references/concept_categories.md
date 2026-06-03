# Concept Categories

Use this reference when scanning a project and generating a knowledge map or glossary.

## Business and Domain Concepts

Examples:

- Equipment repair
- Maintenance work order
- Fault category
- Risk level
- Recommended department
- Sensor tag
- Maintenance work center

Explain the real-world object first, then the project representation.

## Data and Label Concepts

Examples:

- Raw dataset
- Cleaned dataset
- Train/validation/test split
- Label distribution
- Class imbalance
- Label leakage
- Synthetic data

Always distinguish raw labels from cleaned labels.

## Cleaning and Preprocessing

Examples:

- Missing-value tokens
- Deduplication
- Text normalization
- Leakage removal
- Label mapping
- Token length

Connect each cleaning step to the model risk it reduces.

## Models and Algorithms

Examples:

- BERT
- MacBERT
- MiniLM
- BM25
- FAISS
- SimCSE
- Hard negative mining
- Multi-task classification

Explain what input the method expects and what output it produces.

## Training and Evaluation

Examples:

- Fine-tuning
- Learning rate
- Batch size
- Epoch
- FP16
- Macro-F1
- Accuracy
- Recall
- MRR@10
- NDCG@10

Tie each metric to the decision it supports.

## Retrieval and RAG

Examples:

- Sparse retrieval
- Dense retrieval
- Hybrid retrieval
- Reranker
- Similar case retrieval
- Evidence grounding
- RAG pipeline

Separate retrieval from generation. Retrieval finds evidence; generation writes an answer using evidence.

## Application and API

Examples:

- Flask
- `/api/v1/predict`
- Request/response schema
- Frontend display
- Mini-program API

Explain how model outputs become user-facing behavior.

## Git and Project Workflow

Examples:

- Git LFS
- `.gitignore`
- Pull request
- Public repository
- Model weights
- Experiment outputs

Explain what belongs in Git and what should stay outside Git.
