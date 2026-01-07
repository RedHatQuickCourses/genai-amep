# ModelCar Pipeline S3 Migration Guide

## Overview

The ModelCar pipeline has been updated to use S3 storage instead of OCI image packaging with Quay. This simplifies the workflow and aligns with modern cloud-native storage practices.

## What Changed

### Previous Workflow (OCI-based)
1. Download model from HuggingFace
2. Optionally compress model
3. Build ModelCar OCI image using OLOT
4. Push OCI image to Quay registry
5. Register OCI image URI in Model Registry

### New Workflow (S3-based)
1. Download model from HuggingFace
2. Optionally compress model
3. **Upload model to S3 storage** (under `model-data/{model-name}/{version}/`)
4. **Register S3 URI in Model Registry**

## Key Benefits

- **Simplified Architecture**: No need for OCI image building tools (OLOT, skopeo)
- **No Quay Dependency**: Eliminates the need for container registry infrastructure
- **Direct Storage Access**: Models stored in S3 can be accessed directly by serving runtimes
- **Better Scalability**: S3 storage is more suitable for large model files
- **Cost Effective**: Reduced infrastructure overhead

## New Files Created

### 1. S3 Upload Script
**Location**: `deploy/tasks/s3-integration/upload_model.py`

Python script that uploads model files to S3 with metadata tracking. Uses boto3 for S3 operations.

### 2. S3 Upload Container Image
**Location**: `deploy/tasks/s3-integration/Containerfile`

Container image definition for the S3 uploader task.

### 3. S3 Model Registration Script
**Location**: `deploy/tasks/register-with-registry/register_s3_model.py`

Updated registration script that registers S3 URIs instead of OCI image URIs in the Model Registry.

## Modified Files

### 1. Pipeline Definition
**File**: `deploy/openshift/modelcar-pipeline.yaml`

**Changes**:
- Removed `OCI_IMAGE` parameter
- Added `S3_BUCKET` and `S3_ENDPOINT_URL` parameters
- Replaced `quay-auth-workspace` with `s3-credentials` workspace
- Replaced `build-and-push-modelcar` task with `upload-model-to-s3` task
- Updated `register-with-registry` task to use S3 registration script

### 2. Documentation
**File**: `modules/chapter1/pages/modelcar-pipeline.adoc`

**Changes**:
- Updated overview and prerequisites
- Changed deployment instructions to use S3 credentials
- Updated pipeline run examples with S3 parameters
- Revised container image build section
- Updated troubleshooting for S3-based issues

## Migration Steps

### 1. Create S3 Credentials Secret

```bash
oc create secret generic s3-credentials \
  --from-literal=AWS_ACCESS_KEY_ID=<YOUR_ACCESS_KEY> \
  --from-literal=AWS_SECRET_ACCESS_KEY=<YOUR_SECRET_KEY> \
  -n modelcar-pipelines
```

### 2. Create Registration ConfigMap

```bash
oc create configmap register-s3-script \
  --from-file=register_s3_model.py=deploy/tasks/register-with-registry/register_s3_model.py \
  -n modelcar-pipelines
```

### 3. Build and Push S3 Uploader Image

```bash
cd deploy/tasks/s3-integration
podman build --platform linux/amd64 \
  -t quay.io/<YOUR_ORG>/s3-uploader:latest \
  -f Containerfile .
podman push quay.io/<YOUR_ORG>/s3-uploader:latest
```

### 4. Update Pipeline

```bash
oc apply -f deploy/openshift/modelcar-pipeline.yaml -n modelcar-pipelines
```

### 5. Run Pipeline with S3 Parameters

```bash
oc create -f - <<EOF
apiVersion: tekton.dev/v1beta1
kind: PipelineRun
metadata:
  generateName: modelcar-run-
  namespace: modelcar-pipelines
spec:
  pipelineRef:
    name: modelcar-pipeline
  params:
    - name: HUGGINGFACE_MODEL
      value: "ibm-granite/granite-3.3-2b-instruct"
    - name: MODEL_NAME
      value: "granite-3.3-2b-instruct"
    - name: MODEL_VERSION
      value: "1.0.0"
    - name: MODEL_REGISTRY_URL
      value: "http://mysql.rhoai-model-registries.svc.cluster.local:3306"
    - name: S3_BUCKET
      value: "models"
    - name: S3_ENDPOINT_URL
      value: "http://minio.minio.svc.cluster.local:9000"
  workspaces:
    - name: shared-workspace
      persistentVolumeClaim:
        claimName: modelcar-storage
    - name: s3-credentials
      secret:
        secretName: s3-credentials
EOF
```

## S3 Storage Structure

Models are stored in S3 with the following structure:

```
s3://{bucket}/
  └── model-data/
      └── {model-name}/
          └── {version}/
              ├── config.json
              ├── tokenizer.json
              ├── model-00001-of-00002.safetensors
              ├── model-00002-of-00002.safetensors
              └── ...
```

Example:
```
s3://models/model-data/granite-3.3-2b-instruct/1.0.0/
```

## Model Registry Integration

Models are registered in the OpenShift AI Model Registry with:
- **URI**: `s3://{bucket}/model-data/{model-name}/{version}`
- **Storage Type**: `s3`
- **Metadata**: Source (HuggingFace), framework, compression status

## Future Enhancements (Suggested)

Based on your request for model card automation, consider:

1. **Automated Model Card Generation**: Extract metadata from HuggingFace and create model cards in OpenShift AI Model Catalog
2. **Model Serving Integration**: Automatically create InferenceService configurations that point to S3-backed models
3. **Version Management**: Track model versions and provide rollback capabilities
4. **Model Metrics**: Integrate with TrustyAI for automated model evaluation upon registration

## Troubleshooting

### S3 Upload Fails
- Verify S3 credentials are correct
- Check S3 endpoint URL is accessible from the cluster
- Ensure bucket exists and has proper permissions

### Registration Fails
- Verify Model Registry URL is correct
- Check that the model files were successfully uploaded to S3
- Review the `model_s3_uri` file in the workspace

### Missing Model Files
- Check the `HUGGINGFACE_ALLOW_PATTERNS` parameter
- Verify the HuggingFace model repository contains expected files
- Review download task logs for errors

## References

- [S3 Integration Documentation](deploy/tasks/s3-integration/README.md)
- [Model Registry API](https://github.com/kubeflow/model-registry)
- [OpenShift AI Documentation](https://access.redhat.com/documentation/en-us/red_hat_openshift_ai)
