# Terraform state backend (bootstrap)

Creates the S3 bucket and DynamoDB table that the rest of DeployGuard uses
as a remote Terraform backend.

## Resources

- `aws_s3_bucket.terraform_state` — stores the main project's `.tfstate`
- `aws_dynamodb_table.terraform_locks` — state locking, prevents two
  concurrent `apply` runs from corrupting state (partition key: `LockID`,
  a fixed name required by Terraform's S3 backend integration)

## Why this project is separate from the rest of DeployGuard

Bootstrap problem: the S3 backend can't be configured to point at a bucket
that doesn't exist yet, and this project's only job is to create that
bucket. So this folder uses plain local state (Terraform's default when no
`backend` block is set) to create the bucket and table once.

## State

Deliberately kept local, not migrated to the backend it creates. This
project runs once, by one person, with no concurrent access — the actual
problem remote state solves. Setting up a remote backend here would need
its own correct security configuration to be worth doing, for a benefit
(protection if this laptop is lost) that's low-stakes for this specific,
non-sensitive folder. If this machine is ever lost, both resources can be
reattached via `terraform import` using the same code.

## Usage

Run once. After both resources exist, the main DeployGuard Terraform
project (`infrastructure/environments/dev/`, not yet created) references
them as its backend. This folder should not need to be touched again
after that.