#!/usr/bin/env python3
"""
Model Registry Registration for S3-backed Models
Developed by the Red Hat AI Customer Adoption and Innovation team (CAI)

This script registers models stored in S3 to the OpenShift AI Model Registry
"""

import os
import sys
from pathlib import Path

print("Developed by the Red Hat AI Customer Adoption and Innovation team (CAI)")

if os.environ.get('SKIP_TASK') in os.environ.get('SKIP_TASKS', '').split(','):
    print("Skipping register-with-registry task")
    sys.exit(0)

from model_registry import ModelRegistry
from model_registry.types import ModelArtifact, ModelVersion, RegisteredModel
from model_registry.exceptions import StoreError

# Get namespace from service account
namespace_file_path = '/var/run/secrets/kubernetes.io/serviceaccount/namespace'
with open(namespace_file_path, 'r') as namespace_file:
    namespace = namespace_file.read().strip()

# Get cluster domain from environment
cluster_domain = os.environ.get('CLUSTER_DOMAIN', 'cluster.local')

# Get server address from environment
server_address = os.environ.get('MODEL_REGISTRY_URL')
if not server_address:
    print("Error: MODEL_REGISTRY_URL environment variable not set")
    sys.exit(1)
print(f"Server address: {server_address}")

# Set token path in environment
os.environ["KF_PIPELINES_SA_TOKEN_PATH"] = "/var/run/secrets/kubernetes.io/serviceaccount/token"
print("Token path set in environment")

# Initialize model registry client
registry = ModelRegistry(
    server_address=server_address,
    port=443,
    author="modelcar-pipeline",
    is_secure=False
)

# Get model information from environment
model_name = os.environ.get('MODEL_NAME').lower()
model_version = os.environ.get('MODEL_VERSION')
huggingface_model = os.environ.get('HUGGINGFACE_MODEL', 'unknown')

# Read S3 URI from workspace (set by upload task)
s3_uri_file = Path('/workspace/shared-workspace/model_s3_uri')
if s3_uri_file.exists():
    s3_uri = s3_uri_file.read_text().strip()
    print(f"Using S3 URI from upload task: {s3_uri}")
else:
    # Fallback: construct from environment variables
    s3_bucket = os.environ.get('S3_BUCKET')
    if s3_bucket:
        s3_uri = f"s3://{s3_bucket}/model-data/{model_name}/{model_version}"
        print(f"Constructed S3 URI: {s3_uri}")
    else:
        print("Error: Cannot determine S3 URI. S3_BUCKET not set and model_s3_uri file not found.")
        sys.exit(1)

try:
    # Register model with S3 metadata
    registered_model = registry.register_model(
        model_name,
        s3_uri,
        version=model_version,
        description=f"Model {huggingface_model} downloaded from Hugging Face and stored in S3",
        model_format_name="safetensors",
        model_format_version="1",
        storage_key="s3-storage",
        storage_path=s3_uri,
        metadata={
            "source": "huggingface",
            "huggingface_model": huggingface_model,
            "framework": "pytorch",
            "storage_type": "s3",
            "s3_uri": s3_uri
        }
    )

    print(f"Successfully registered model: {model_name} version {model_version}")
    print(f"Model URI: {s3_uri}")
    print(f"Model details available at: https://rhods-dashboard-redhat-ods-applications.{cluster_domain}/modelRegistry/modelcar-pipeline-registry/registeredModels/1/versions/{registry.get_model_version(model_name, model_version).id}/details")

    # Save model version ID for future tasks
    model_version_id = registry.get_model_version(model_name, model_version).id
    with open('/workspace/shared-workspace/model_version_id', 'w') as f:
        f.write(str(model_version_id))

    print(f"✅ Model registration complete!")
    print(f"   Model: {model_name} v{model_version}")
    print(f"   Registry ID: {model_version_id}")
    print(f"   S3 Location: {s3_uri}")

except StoreError as e:
    print(f"Model version already exists: {model_name} version {model_version}")
    try:
        # Get existing model version details
        model_details = registry.get_model_version(model_name, model_version)
        print(f"Existing model details:")
        print(f"Model ID: {model_details.id}")
        print(f"Model Name: {model_details.name}")

        # Save model version ID for future tasks
        with open('/workspace/shared-workspace/model_version_id', 'w') as f:
            f.write(str(model_details.id))

        print("✅ Task completed successfully - using existing model version")
        sys.exit(0)
    except Exception as e:
        print(f"Error getting existing model details: {str(e)}")
        sys.exit(1)
except Exception as e:
    print(f"Error registering model: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
