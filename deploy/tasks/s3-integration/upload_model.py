#!/usr/bin/env python3
"""
S3 Model Upload Task for ModelCar Pipeline
Developed by the Red Hat AI Customer Adoption and Innovation team (CAI)

This script uploads downloaded HuggingFace models to S3 storage
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    print("❌ boto3 not installed. Install with: pip install boto3")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("Developed by the Red Hat AI Customer Adoption and Innovation team (CAI)")

# Check if task should be skipped
if os.environ.get('SKIP_TASK') in os.environ.get('SKIP_TASKS', '').split(','):
    print("Skipping upload-model-to-s3 task")
    sys.exit(0)

# Get environment variables
bucket_name = os.environ.get('S3_BUCKET')
endpoint_url = os.environ.get('S3_ENDPOINT_URL')
access_key = os.environ.get('AWS_ACCESS_KEY_ID')
secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
model_name = os.environ.get('MODEL_NAME')
model_version = os.environ.get('MODEL_VERSION', '1.0.0')
workspace_path = os.environ.get('WORKSPACE_PATH', '/workspace/shared-workspace/model')

if not all([bucket_name, access_key, secret_key, model_name]):
    logger.error("Missing required environment variables")
    logger.error("Required: S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, MODEL_NAME")
    sys.exit(1)

# Initialize S3 client
s3_config = {
    'service_name': 's3',
    'aws_access_key_id': access_key,
    'aws_secret_access_key': secret_key
}

if endpoint_url:
    s3_config['endpoint_url'] = endpoint_url

try:
    s3_client = boto3.client(**s3_config)
    # Verify bucket exists
    s3_client.head_bucket(Bucket=bucket_name)
    logger.info(f"✅ Connected to S3 bucket: {bucket_name}")
except ClientError as e:
    error_code = e.response['Error']['Code']
    if error_code == '404':
        logger.error(f"❌ Bucket '{bucket_name}' does not exist")
    else:
        logger.error(f"❌ Error accessing bucket: {e}")
    sys.exit(1)

# Upload model files to S3
model_dir = Path(workspace_path)
if not model_dir.exists():
    logger.error(f"❌ Model directory not found: {model_dir}")
    sys.exit(1)

# Create S3 prefix: model-data/{model_name}/{model_version}/
s3_prefix = f"model-data/{model_name}/{model_version}"
logger.info(f"📤 Uploading model to S3...")
logger.info(f"   Local path: {model_dir}")
logger.info(f"   S3 prefix: s3://{bucket_name}/{s3_prefix}")

uploaded_count = 0
total_size = 0

# Upload all files recursively
for file_path in model_dir.rglob('*'):
    if file_path.is_file():
        relative_path = file_path.relative_to(model_dir)
        s3_key = f"{s3_prefix}/{relative_path}"

        try:
            # Upload with metadata
            extra_args = {
                'Metadata': {
                    'model-name': model_name,
                    'model-version': model_version,
                    'upload-timestamp': datetime.now().isoformat(),
                    'source': 'huggingface',
                    'pipeline': 'modelcar-pipeline'
                }
            }

            s3_client.upload_file(
                str(file_path),
                bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )

            file_size = file_path.stat().st_size
            total_size += file_size
            uploaded_count += 1

            logger.info(f"   ✓ {relative_path} ({file_size:,} bytes)")

        except ClientError as e:
            logger.error(f"   ✗ Failed to upload {relative_path}: {e}")
            sys.exit(1)

logger.info(f"✅ Uploaded {uploaded_count} files ({total_size:,} bytes)")
logger.info(f"   S3 Location: s3://{bucket_name}/{s3_prefix}/")

# Save S3 URI for registration task
s3_uri = f"s3://{bucket_name}/{s3_prefix}"
uri_file = Path('/workspace/shared-workspace/model_s3_uri')
uri_file.write_text(s3_uri)
logger.info(f"   Saved S3 URI to: {uri_file}")

print(f"\n✅ Model upload complete!")
print(f"   Model: {model_name} v{model_version}")
print(f"   S3 URI: {s3_uri}")
print(f"   Files: {uploaded_count} ({total_size:,} bytes)")
