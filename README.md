# Automated Multilingual Evaluation Pipeline (AMEP)
**A Modular Framework for OpenShift AI 3.0**

![Status](https://img.shields.io/badge/Status-Active-success)
![Audience](https://img.shields.io/badge/Role-Platform%20Engineer-blue)
![Platform](https://img.shields.io/badge/Platform-OpenShift%20AI%203.0-red)

## 👋 Welcome

Welcome to the **Automated Multilingual Evaluation Pipeline (AMEP)** solution kit.

If you are a **Platform Engineer**, you know the struggle: your Ai Developers and Data Scientists want to use the "latest and greatest" open-source models, but they need to know if those models actually work for your specific business requirements—especially when supporting multiple languages.

This repository isn't just a lab; it is a **deployable solution framework**. We have broken down the complex process of model evaluation into four distinct, manual steps. You can run them sequentially to build a full evaluation pipeline, or pick and choose individual modules to integrate into your own existing workflows.

## 🎯 Who Is This For?

We built this specifically for the people building the tracks for the AI train:

* **Platform Engineers (Primary):** You need to provide a robust service to your data science teams. This guide shows you how to build the "plumbing" for model evaluation so they can focus on the data.
* **Service Consultants:** You are delivering OpenShift AI solutions to customers. Use this repo as a reference architecture or a base for your delivery engagements.
* **Red Hat Partners:** You are building integrations on top of OpenShift AI 3.0. This framework demonstrates best practices for Model Registry, ModelCar, and TrustyAI integration.

---

## 🧩 The Workflow (Modular & Manual)

This guide walks you through the process manually. This ensures you understand exactly how the components interact and allows you to debug or customize steps easily.

### Phase 1: Package & Register 📦
**"Treat Models Like Software"**
Stop downloading weights at runtime. We will show you how to package a Large Language Model (LLM) into an OCI container image (a "ModelCar") using standard tools like `podman`. You will then register this artifact in the **OpenShift AI Model Registry** for governance and versioning.

### Phase 2: Deploy (vLLM) 🚀
**"High-Performance Serving"**
You will manually trigger the deployment of your registered model using **vLLM**, the state-of-the-art inference engine. We will cover how to configure the `ServingRuntime` and ensure your GPU resources are allocated correctly.

### Phase 3: Evaluate (TrustyAI) ⚖️
**"The Test Drive"**
This is where the magic happens. You will deploy a **TrustyAI LMEvalJob**—a Kubernetes Custom Resource that automatically runs standardized fluency tests against your deployed model.
* **Languages Tested:** English 🇺🇸, Spanish 🇪🇸, Japanese 🇯🇵
* **Metrics:** Accuracy, Fluency, and Hallucination resistance.

### Phase 4: Visualize 📊
**"Make It Visible"**
Finally, you will gather the raw JSON data from object storage (S3) and use a Jupyter Notebook to generate a **Radar Chart**. This gives you a clean, visual artifact to show stakeholders exactly how different models compare.

---

## 🛠️ Tech Stack

This solution uses standard, cloud-native components available in OpenShift AI 3.0:

* **Registry:** Red Hat OpenShift AI Model Registry
* **Runtime:** vLLM (KServe)
* **Evaluation:** TrustyAI (LM-Evaluation-Harness)
* **Storage:** S3 Compatible Storage (ODF/MinIO)
* **Analysis:** Jupyter Lab (RHOAI Workbench)

---

## 🚀 Quick Start

### Prerequisites
1.  **OpenShift AI 3.0+** cluster access.
2.  **Cluster Admin** privileges (required for setting up initial ServingRuntimes).
3.  **S3 Storage** (bucket name and credentials).
4.  A **Container Registry** (Quay.io or internal) to push your ModelCar images.

### Installation

1.  **Clone this Repository**
    ```bash
    git clone [https://github.com/your-org/genai-amep.git](https://github.com/your-org/genai-amep.git)
    cd genai-amep
    ```

2.  **Access the Guide**
    This documentation is built with Antora. To view the step-by-step instructions:

    * **Option A (Local Build):**
        ```bash
        npm install && npm run build
        # Open build/site/index.html
        ```
    * **Option B (Direct Read):**
        Navigate to the `modules/ROOT/pages/` folder to read the guides as raw text files.

---

## 📚 Roadmap & Flexibility

Because these steps are manual, you can swap them out!
* *Don't need Spanish?* Modify the TrustyAI config in Phase 3.
* *Already have a model deployed?* Skip Phase 1 & 2 and jump straight to Phase 3 to evaluate it.
* *Want to use TGIS instead of vLLM?* Swap the ServingRuntime in Phase 2.

## 🤝 Contribution & Feedback

This is a living framework. If you find a better way to configure the Model Registry or a more efficient TrustyAI metric, please open a PR!

**Maintainers:** Red Hat Product Enablement Readiness Team
**Original Creators** Red Hat AI Customer Adoption and Innovation (CAI) Team