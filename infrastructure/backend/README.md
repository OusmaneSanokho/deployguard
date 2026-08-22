# Terraform state backend (bootstrap)

Creates the S3 bucket the rest of DeployGuard uses as a remote Terraform
backend.

## Resources

- `aws_s3_bucket.terraform_state` — stores every other project's `.tfstate`

## State locking

Originally used a DynamoDB table (`LockID` partition key) for locking, per
the standard pattern for Terraform S3 backends. Terraform 1.11+ introduced
native S3 locking (`use_lockfile = true` in a project's backend block),
which uses the bucket itself and needs no separate table. Migrated to
that approach and destroyed the DynamoDB table, since it no longer served
a purpose — see commit history for the change.

## Why this project is separate from the rest of DeployGuard

Bootstrap problem: the S3 backend can't be configured to point at a bucket
that doesn't exist yet, and this project's only job is to create that
bucket. So this folder uses plain local state (Terraform's default when no
`backend` block is set) to create it once.

## State

Deliberately kept local, not migrated to the backend it creates. This
project runs once, by one person, with no concurrent access — the actual
problem remote state solves. If this machine is ever lost, the bucket can
be reattached via `terraform import` using the same code.

## Usage

Run once. After the bucket exists, other DeployGuard Terraform projects
reference it as their backend using `use_lockfile = true`, not DynamoDB.