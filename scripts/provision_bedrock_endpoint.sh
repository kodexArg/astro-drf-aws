#!/usr/bin/env bash
# Provisions the Bedrock VPC interface endpoint for the project.
#
# Mirrors this repo's existing provisioning mechanism: raw AWS CLI calls run
# manually by an operator with the correct account/profile, then recorded in
# docs/INVENTORY.md in the same batch ([[adr-29-permanent-deployment]]). There is
# no Terraform/CDK in this repo — see docs/INVENTORY.md for every other
# resource created the same way.
#
# Prerequisites:
#   - AWS CLI configured with a profile that resolves to {{AWS_ACCOUNT_ID}}
#     (set AWS_ACCOUNT_ID after bootstrap). Verify first:
#       aws sts get-caller-identity --profile "${AWS_PROFILE:-kodex}"
#   - Region us-east-1 (adr-02-initial-stack).
#   - VPC_ID, TASK_SG_ID, and SUBNET_IDS filled after bootstrap — never invent IDs.
#
# This script is idempotent-unsafe by design (matches the rest of the repo's
# manual provisioning steps) — run it once, then hand-copy the returned IDs
# into docs/INVENTORY.md.

set -euo pipefail

PROFILE="${AWS_PROFILE:-kodex}"
REGION="${AWS_REGION:-us-east-1}"
PROJECT_SLUG="${PROJECT_SLUG:-astro-drf-aws}"
EXPECTED_ACCOUNT="${AWS_ACCOUNT_ID:-REPLACE_AFTER_BOOTSTRAP}"
VPC_ID="${VPC_ID:-REPLACE_AFTER_BOOTSTRAP}"
TASK_SG_ID="${TASK_SG_ID:-REPLACE_AFTER_BOOTSTRAP}"
# Space-separated subnet IDs, e.g. "subnet-REPLACE_AFTER_BOOTSTRAP subnet-REPLACE_AFTER_BOOTSTRAP"
read -r -a SUBNET_IDS <<< "${SUBNET_IDS:-REPLACE_AFTER_BOOTSTRAP}"

if [[ "$VPC_ID" == "REPLACE_AFTER_BOOTSTRAP" || "$TASK_SG_ID" == "REPLACE_AFTER_BOOTSTRAP" ]]; then
  echo "Set VPC_ID, TASK_SG_ID, and SUBNET_IDS from live discovery after bootstrap." >&2
  echo "Do not invent vpc-/sg-/subnet- IDs." >&2
  exit 1
fi

TAGS="Key=project,Value=${PROJECT_SLUG} Key=env,Value=prod Key=lifecycle,Value=ephemeral Key=Name,Value=alvs-prod-bedrock-vpce-sg"
EP_TAGS="Key=project,Value=${PROJECT_SLUG} Key=env,Value=prod Key=lifecycle,Value=ephemeral Key=Name,Value=alvs-prod-bedrock-runtime-vpce"

echo "Caller identity (must match AWS_ACCOUNT_ID=${EXPECTED_ACCOUNT}):"
CALLER=$(aws sts get-caller-identity --profile "$PROFILE" --query Account --output text)
if [[ "$EXPECTED_ACCOUNT" != "REPLACE_AFTER_BOOTSTRAP" && "$CALLER" != "$EXPECTED_ACCOUNT" ]]; then
  echo "Account mismatch: caller=$CALLER expected=$EXPECTED_ACCOUNT" >&2
  exit 1
fi

echo "Creating security group alvs-prod-bedrock-vpce-sg..."
SG_ID=$(aws ec2 create-security-group \
  --profile "$PROFILE" --region "$REGION" \
  --group-name alvs-prod-bedrock-vpce-sg \
  --description "Ingress 443 from alvs-prod-task-sg for the Bedrock runtime VPC endpoint" \
  --vpc-id "$VPC_ID" \
  --tag-specifications "ResourceType=security-group,Tags=[$TAGS]" \
  --query 'GroupId' --output text)
echo "Created SG: $SG_ID"

aws ec2 authorize-security-group-ingress \
  --profile "$PROFILE" --region "$REGION" \
  --group-id "$SG_ID" \
  --protocol tcp --port 443 \
  --source-group "$TASK_SG_ID"

echo "Creating Bedrock runtime interface endpoint..."
VPCE_ID=$(aws ec2 create-vpc-endpoint \
  --profile "$PROFILE" --region "$REGION" \
  --vpc-id "$VPC_ID" \
  --vpc-endpoint-type Interface \
  --service-name "com.amazonaws.${REGION}.bedrock-runtime" \
  --subnet-ids "${SUBNET_IDS[@]}" \
  --security-group-ids "$SG_ID" \
  --private-dns-enabled \
  --tag-specifications "ResourceType=vpc-endpoint,Tags=[$EP_TAGS]" \
  --query 'VpcEndpoint.VpcEndpointId' --output text)

echo "Created VPC endpoint: $VPCE_ID"
echo
echo "Next step (same batch): update docs/INVENTORY.md —"
echo "  flip both 'planned' rows to live with SG=$SG_ID, VPCE=$VPCE_ID."
