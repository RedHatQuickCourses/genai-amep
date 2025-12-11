#!/usr/bin/env python3
"""
S3 Integration for LLM Evaluation Results
Developed by the Red Hat AI Customer Adoption and Innovation team (CAI)

This script uploads evaluation results to S3-compatible storage
and provides utilities for downloading and comparing results.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import logging

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


class S3EvaluationStorage:
    """Manages evaluation results storage in S3"""

    def __init__(
        self,
        bucket_name: str,
        endpoint_url: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None
    ):
        """
        Initialize S3 client

        Args:
            bucket_name: S3 bucket name
            endpoint_url: S3 endpoint URL (for MinIO or compatible services)
            access_key: AWS access key ID
            secret_key: AWS secret access key
        """
        self.bucket_name = bucket_name

        # Configure S3 client
        s3_config = {
            'service_name': 's3'
        }

        if endpoint_url:
            s3_config['endpoint_url'] = endpoint_url

        if access_key and secret_key:
            s3_config['aws_access_key_id'] = access_key
            s3_config['aws_secret_access_key'] = secret_key

        self.s3 = boto3.client(**s3_config)

        # Verify bucket exists
        try:
            self.s3.head_bucket(Bucket=bucket_name)
            logger.info(f"✅ Connected to S3 bucket: {bucket_name}")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.error(f"❌ Bucket '{bucket_name}' does not exist")
            else:
                logger.error(f"❌ Error accessing bucket: {e}")
            raise

    def upload_evaluation_results(
        self,
        results_dir: Path,
        model_name: str,
        model_version: str,
        evaluation_id: Optional[str] = None
    ) -> str:
        """
        Upload evaluation results to S3

        Args:
            results_dir: Path to local results directory
            model_name: Name of the evaluated model
            model_version: Version of the evaluated model
            evaluation_id: Optional custom evaluation ID

        Returns:
            S3 prefix where files were uploaded
        """
        if not results_dir.exists():
            raise ValueError(f"Results directory not found: {results_dir}")

        # Generate evaluation ID if not provided
        if not evaluation_id:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            evaluation_id = f"{model_name}_{model_version}_{timestamp}"

        s3_prefix = f"evaluations/{model_name}/{model_version}/{evaluation_id}"

        logger.info(f"📤 Uploading results to S3...")
        logger.info(f"   Local path: {results_dir}")
        logger.info(f"   S3 prefix: s3://{self.bucket_name}/{s3_prefix}")

        uploaded_count = 0
        total_size = 0

        # Upload all files recursively
        for file_path in results_dir.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(results_dir)
                s3_key = f"{s3_prefix}/{relative_path}"

                try:
                    # Upload with metadata
                    extra_args = {
                        'Metadata': {
                            'model-name': model_name,
                            'model-version': model_version,
                            'evaluation-id': evaluation_id,
                            'upload-timestamp': datetime.now().isoformat()
                        }
                    }

                    self.s3.upload_file(
                        str(file_path),
                        self.bucket_name,
                        s3_key,
                        ExtraArgs=extra_args
                    )

                    file_size = file_path.stat().st_size
                    total_size += file_size
                    uploaded_count += 1

                    logger.debug(f"   ✓ {relative_path} ({file_size} bytes)")

                except ClientError as e:
                    logger.error(f"   ✗ Failed to upload {relative_path}: {e}")

        logger.info(f"✅ Uploaded {uploaded_count} files ({total_size:,} bytes)")
        logger.info(f"   S3 Location: s3://{self.bucket_name}/{s3_prefix}/")

        return s3_prefix

    def download_evaluation_results(
        self,
        s3_prefix: str,
        local_dir: Path
    ) -> None:
        """
        Download evaluation results from S3

        Args:
            s3_prefix: S3 prefix to download from
            local_dir: Local directory to save files
        """
        local_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"📥 Downloading results from S3...")
        logger.info(f"   S3 prefix: s3://{self.bucket_name}/{s3_prefix}")
        logger.info(f"   Local path: {local_dir}")

        # List all objects with the prefix
        paginator = self.s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=self.bucket_name, Prefix=s3_prefix)

        downloaded_count = 0

        for page in pages:
            if 'Contents' not in page:
                continue

            for obj in page['Contents']:
                s3_key = obj['Key']

                # Calculate local file path
                relative_path = s3_key[len(s3_prefix):].lstrip('/')
                local_file = local_dir / relative_path

                # Create parent directories
                local_file.parent.mkdir(parents=True, exist_ok=True)

                try:
                    self.s3.download_file(
                        self.bucket_name,
                        s3_key,
                        str(local_file)
                    )
                    downloaded_count += 1
                    logger.debug(f"   ✓ {relative_path}")

                except ClientError as e:
                    logger.error(f"   ✗ Failed to download {s3_key}: {e}")

        logger.info(f"✅ Downloaded {downloaded_count} files")

    def list_evaluations(
        self,
        model_name: Optional[str] = None,
        model_version: Optional[str] = None
    ) -> List[Dict]:
        """
        List available evaluations in S3

        Args:
            model_name: Optional filter by model name
            model_version: Optional filter by model version

        Returns:
            List of evaluation metadata dictionaries
        """
        prefix = "evaluations/"
        if model_name:
            prefix += f"{model_name}/"
            if model_version:
                prefix += f"{model_version}/"

        logger.info(f"🔍 Listing evaluations: s3://{self.bucket_name}/{prefix}")

        evaluations = []
        paginator = self.s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(
            Bucket=self.bucket_name,
            Prefix=prefix,
            Delimiter='/'
        )

        for page in pages:
            # List "directories" (common prefixes)
            for common_prefix in page.get('CommonPrefixes', []):
                eval_prefix = common_prefix['Prefix']

                # Try to fetch metadata from summary file
                summary_key = f"{eval_prefix}cross_language_summary.json"
                try:
                    response = self.s3.get_object(
                        Bucket=self.bucket_name,
                        Key=summary_key
                    )
                    metadata = json.loads(response['Body'].read())
                    metadata['s3_prefix'] = eval_prefix
                    evaluations.append(metadata)
                except ClientError:
                    # Summary file not found, create basic metadata
                    evaluations.append({
                        's3_prefix': eval_prefix,
                        'model_name': 'unknown',
                        'model_version': 'unknown'
                    })

        return evaluations


def main():
    parser = argparse.ArgumentParser(
        description="Upload/download LLM evaluation results to/from S3"
    )
    parser.add_argument(
        'action',
        choices=['upload', 'download', 'list'],
        help="Action to perform"
    )
    parser.add_argument(
        '--results-dir',
        type=Path,
        help="Local results directory (for upload/download)"
    )
    parser.add_argument(
        '--model-name',
        required='upload' in sys.argv,
        help="Model name"
    )
    parser.add_argument(
        '--model-version',
        required='upload' in sys.argv,
        help="Model version"
    )
    parser.add_argument(
        '--evaluation-id',
        help="Custom evaluation ID (optional)"
    )
    parser.add_argument(
        '--s3-prefix',
        help="S3 prefix (for download)"
    )
    parser.add_argument(
        '--bucket',
        default=os.environ.get('S3_BUCKET', 'llm-evaluation-results'),
        help="S3 bucket name (default: from S3_BUCKET env var)"
    )
    parser.add_argument(
        '--endpoint-url',
        default=os.environ.get('S3_ENDPOINT_URL'),
        help="S3 endpoint URL (default: from S3_ENDPOINT_URL env var)"
    )
    parser.add_argument(
        '--access-key',
        default=os.environ.get('AWS_ACCESS_KEY_ID'),
        help="AWS access key (default: from AWS_ACCESS_KEY_ID env var)"
    )
    parser.add_argument(
        '--secret-key',
        default=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        help="AWS secret key (default: from AWS_SECRET_ACCESS_KEY env var)"
    )

    args = parser.parse_args()

    # Initialize S3 client
    try:
        storage = S3EvaluationStorage(
            bucket_name=args.bucket,
            endpoint_url=args.endpoint_url,
            access_key=args.access_key,
            secret_key=args.secret_key
        )
    except Exception as e:
        logger.error(f"Failed to initialize S3 client: {e}")
        sys.exit(1)

    # Perform action
    if args.action == 'upload':
        if not args.results_dir:
            logger.error("--results-dir required for upload")
            sys.exit(1)

        try:
            s3_prefix = storage.upload_evaluation_results(
                results_dir=args.results_dir,
                model_name=args.model_name,
                model_version=args.model_version,
                evaluation_id=args.evaluation_id
            )
            print(f"\n✅ Upload complete!")
            print(f"   S3 Location: s3://{args.bucket}/{s3_prefix}/")

        except Exception as e:
            logger.error(f"Upload failed: {e}")
            sys.exit(1)

    elif args.action == 'download':
        if not args.s3_prefix or not args.results_dir:
            logger.error("--s3-prefix and --results-dir required for download")
            sys.exit(1)

        try:
            storage.download_evaluation_results(
                s3_prefix=args.s3_prefix,
                local_dir=args.results_dir
            )
            print(f"\n✅ Download complete!")
            print(f"   Local path: {args.results_dir}")

        except Exception as e:
            logger.error(f"Download failed: {e}")
            sys.exit(1)

    elif args.action == 'list':
        try:
            evaluations = storage.list_evaluations(
                model_name=args.model_name,
                model_version=args.model_version
            )

            if not evaluations:
                print("No evaluations found")
            else:
                print(f"\n📊 Found {len(evaluations)} evaluation(s):\n")
                for eval_data in evaluations:
                    print(f"  Model: {eval_data.get('model_name', 'unknown')} "
                          f"v{eval_data.get('model_version', 'unknown')}")
                    print(f"  Time: {eval_data.get('timestamp', 'unknown')}")
                    print(f"  S3 Path: {eval_data['s3_prefix']}")
                    print()

        except Exception as e:
            logger.error(f"List failed: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
