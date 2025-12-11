# Automated Multi-Language LLM Evaluation Pipeline - Lab Guide

**Developed by**: Red Hat AI Customer Adoption and Innovation team (CAI)

This repository contains comprehensive documentation for the Automated Multi-Language LLM Evaluation Pipeline lab, designed to teach users how to evaluate Large Language Models across multiple languages using Red Hat OpenShift AI.

## Overview

This lab guide walks you through building and using an automated pipeline that:

- Downloads models from HuggingFace Hub
- Optionally compresses models for efficiency
- Packages models in OCI containers (Modelcar)
- Registers models in OpenShift AI Model Registry
- Deploys models using vLLM for high-performance inference
- Evaluates model performance across **English, Spanish, and Japanese**
- Tests for bias and fairness using TrustyAI (optional)
- Stores results in S3 for historical comparison
- Visualizes and analyzes results using Jupyter notebooks

## Who Should Take This Lab

This lab is designed for:

- **ML Engineers** evaluating model performance across languages
- **AI Platform Teams** standardizing model evaluation workflows
- **Data Scientists** comparing model variants and optimizations
- **Quality Assurance Teams** testing models for bias and fairness
- **Anyone** interested in multi-language LLM evaluation on OpenShift AI

## Lab Objectives

By completing this lab, you will learn how to:

1. **Automate Model Preparation**
   - Download models from HuggingFace
   - Compress models using llmcompressor
   - Package models in OCI containers
   - Register models in the Model Registry

2. **Deploy Models on OpenShift AI**
   - Create vLLM ServingRuntimes
   - Deploy InferenceServices with GPU support
   - Configure model serving parameters
   - Test deployed models

3. **Evaluate Models Across Languages**
   - Run standardized benchmarks for English, Spanish, and Japanese
   - Compare performance across languages
   - Identify language-specific performance gaps
   - Generate comprehensive evaluation reports

4. **Integrate Bias and Fairness Testing**
   - Set up TrustyAI for bias detection
   - Test for gender bias across languages
   - Analyze fairness metrics
   - Document and report findings

5. **Manage Evaluation Results**
   - Store results in S3-compatible storage
   - Retrieve and compare historical results
   - Visualize performance using Jupyter notebooks
   - Generate reports for stakeholders

## Prerequisites

Before starting this lab, you should have:

- Access to an OpenShift cluster with OpenShift AI installed
- GPU nodes (NVIDIA) available for model serving
- Basic knowledge of Kubernetes/OpenShift
- Familiarity with Python and Jupyter notebooks
- Understanding of LLM concepts
- Access to container registry (e.g., Quay.io)

## Lab Structure

This lab is organized into several chapters:

### Introduction
- Pipeline overview
- Architecture and components
- Prerequisites and setup

### Chapter 1: Model Preparation
- Downloading models from HuggingFace
- Model compression techniques
- Modelcar container packaging
- Model Registry integration

### Chapter 2: Model Deployment
- vLLM deployment on OpenShift AI
- InferenceService configuration
- Testing your deployment
- Troubleshooting deployment issues

### Chapter 3: Model Evaluation
- Multi-language evaluation setup
- Running evaluations across English, Spanish, and Japanese
- TrustyAI bias and fairness testing
- Storing results in S3
- Analyzing and visualizing results

### Appendix
- Reference materials
- Troubleshooting guide
- Additional resources

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd genai-amep
```

### 2. View the Documentation

This repository uses Antora for documentation. You can:

**Option A: Build and view locally**
```bash
npm install
npm run build
# Open build/site/index.html in your browser
```

**Option B: View the source Asciidoc files**
Navigate to `modules/` directory and open `.adoc` files in a text editor or Asciidoc viewer.

**Option C: Deploy to a web server**
```bash
npm run build
# Copy build/site/* to your web server
```

### 3. Access the Code Repository

The implementation code for this lab is in the companion repository: `model-car-importer`

Clone it alongside this documentation:
```bash
cd ..
git clone <model-car-importer-url>
cd model-car-importer
```

## Key Features of This Lab

### 🌍 Multi-Language Evaluation

Evaluate your models across three languages with standardized benchmarks:

| Language | Benchmarks |
|----------|------------|
| **English** | ARC-Easy, HellaSwag, WinoGrande, TruthfulQA |
| **Spanish** | BELEBELE Spanish, XNLI Spanish |
| **Japanese** | BELEBELE Japanese, XNLI Japanese |

### 🔄 Fully Automated Pipeline

Built on Tekton, the pipeline automates the entire workflow:
- Single command execution
- Conditional task execution
- Progress tracking
- Error handling and recovery
- Results archival

### 📊 Comprehensive Analysis

Analyze and visualize results with included Jupyter notebooks:
- Performance comparison charts
- Cross-language heatmaps
- Performance gap analysis
- Historical trending
- Export to multiple formats

### ☁️ S3 Integration

Built-in S3 storage for:
- Automatic result uploads
- Historical comparison
- Team collaboration
- Long-term archival

### ⚖️ Bias Detection (Optional)

TrustyAI integration for:
- Gender bias detection
- Multi-language fairness testing
- Protected attribute analysis
- Comprehensive bias metrics

## Lab Duration

**Estimated Time**: 4-6 hours

- Chapter 1 (Model Preparation): 1-1.5 hours
- Chapter 2 (Model Deployment): 1-1.5 hours
- Chapter 3 (Model Evaluation): 2-3 hours

**Note**: Actual time may vary depending on:
- Model size (larger models take longer to download/compress)
- Hardware resources (GPU availability)
- Network speed (for downloads)
- Familiarity with OpenShift/Kubernetes

## Technologies Used

This lab demonstrates the following technologies:

- **Red Hat OpenShift AI**: AI/ML platform
- **Tekton Pipelines**: Cloud-native CI/CD
- **vLLM**: High-performance LLM inference
- **Model Registry**: Model governance and tracking
- **lm-evaluation-harness**: Benchmark evaluation framework
- **Neural Magic llmcompressor**: Model quantization
- **OLOT**: OCI Layer Object Transport
- **TrustyAI**: Bias and fairness detection (optional)
- **S3**: Object storage for results
- **Jupyter**: Interactive analysis and visualization

## Documentation Format

This documentation is built using [Antora](https://antora.org/), a multi-repository documentation site generator designed for technical documentation.

### Directory Structure

```
genai-amep/
├── antora.yml                 # Component descriptor
├── antora-playbook.yml        # Playbook configuration
├── modules/
│   ├── ROOT/
│   │   ├── nav.adoc          # Navigation for ROOT module
│   │   └── pages/            # Documentation pages
│   ├── chapter1/             # Model Preparation
│   ├── chapter2/             # Model Deployment
│   ├── chapter3/             # Model Evaluation
│   └── appendix/             # Reference materials
├── ui-assets/                # Custom UI styling
└── supplemental-ui/          # Additional UI elements
```

### Building the Documentation

```bash
# Install dependencies
npm install

# Build the documentation site
npm run build

# The output will be in build/site/
```

## Support and Contribution

For questions, issues, or contributions related to this lab:

- Contact the Red Hat AI Customer Adoption and Innovation team (CAI)
- Review the troubleshooting section in the documentation
- Check the appendix for additional resources

## Related Resources

- **Code Repository**: [model-car-importer](../model-car-importer) - Implementation code for the pipeline
- **OpenShift AI Documentation**: https://docs.redhat.com/en/documentation/red_hat_openshift_ai
- **vLLM Documentation**: https://docs.vllm.ai/
- **Tekton Documentation**: https://tekton.dev/docs/
- **lm-evaluation-harness**: https://github.com/EleutherAI/lm-evaluation-harness
- **TrustyAI**: https://trustyai.opendatahub.io/

## License

[Specify your license here]

## Acknowledgments

This lab was developed by the Red Hat AI Customer Adoption and Innovation team (CAI) to help organizations evaluate and deploy LLMs across multiple languages using Red Hat OpenShift AI.

Special thanks to:
- Neural Magic for llmcompressor
- EleutherAI for lm-evaluation-harness
- vLLM team for high-performance inference
- TrustyAI project for bias detection tools
- OpenShift AI development team

## Getting Started

Ready to begin? Start with the [Introduction](modules/ROOT/pages/index.adoc) and follow the chapters in sequence. Each chapter builds on the previous one, taking you from basic model preparation through advanced multi-language evaluation.

**Let's get started!** 🚀
