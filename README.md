# Automate an AWS Security Baseline

**Author:** Cherif Rahman

> **Practice scenario modeled on Nationwide, not affiliated with or performed for Nationwide.** This is a personal portfolio lab. All accounts, buckets, and data are synthetic.

## Defining a Safe, Automated Security Baseline

### Baseline detection, remediation, and SCP safety

In this project, I am building an AWS Security Baseline, so basically it is a scenario that some companies have experienced, so all it is about when an employee accidentally removes a part of the organization that keeps it safe. An intruder gets in and does everything they can to cause damage, and I'll focus on what they did.

## Building a CI-Gated Infrastructure Repository

### Establishing repeatable infrastructure security checks

I'm creating a Git repository, so if the security has a malfunction or loses trust, this will reject the problems before it gets ready to deploy. I will create the supplied infrastructure files that would pass a local security check and confirm that GitHub Actions works as it should.

![Building a CI-Gated Infrastructure Repository](docs/images/01-ci-gated-repository.png)

## Deploying Detective Security Controls

### Provisioning audit, compliance, and alerting services

What I'm creating is a security baseline, basically a set of guardrails I customized to watch what happens in the account, and it alerts me if it shows malicious activity in the account so for right now I'm trying to deploy it. I did indeed have some errors because the region I was using had already been used, so I had to use a different region, and it kept saying the stack couldn't be updated or created.

![Deploying Detective Security Controls](docs/images/02-detective-controls-stack.png)

## Demonstrating the S3 Guardrail Gap

### Testing an out-of-band S3 security change

For this step, I'm using AWS CloudTrail and AWS Config to monitor my AWS account for suspicious changes, and I'm using EventBridge and Lambda to detect them and enable the necessary settings, like enabling block public access. Currently, I'm trying to capture a protected bucket from the stack output and demonstrate the configuration gap without adding data or a public bucket policy.

### What infrastructure drift revealed

I observed when I removed the protected bucket's Block Public Access setting and tried to see if it had worked, and how this is scary, as it creates a gap so if someone is not careful, this can be a highly crucial security risk

![Demonstrating the S3 Guardrail Gap](docs/images/03-s3-guardrail-gap.png)

## Automating S3 Block Public Access Recovery

### EventBridge-triggered Lambda remediation

What I'm going to do is build a lambda deployment package with the supplied handler, then package the remediation template and deploy the CloudFormation stack, and going to test to see if the responder restores it automatically by deleting the bucket-level setting.

## Validating CloudTrail Protection and Tamper Detection

### Validating policy as code and alerting

I'm validating the unattached CloudTrail protection SCP against its required actions, then triggering a brief CloudTrail stop-start event. Once that's done, I'll check to see if I receive the tamper-alert email after confirming the trail status.

![Validating CloudTrail Protection and Tamper Detection](docs/images/04-cloudtrail-tamper-check.png)

### Safely keeping the SCP unattached

I kept it unattached because it avoids accidental lockouts, and standalone accounts don't support it, and I verified safety by running our script to check the rules automatically.

## Extending Automated Remediation to World-Open SSH

![Extending Automated Remediation to World-Open SSH](docs/images/05-world-open-ssh.png)

### Precisely revoking only unsafe SSH access

In this project extension, the responder checks. If the security group has the specified tag, it makes sure it connects to the lab, and it checks whether the port is 22 and whether IP ranges are allowed; if they are not configured, it will blindly delete the important stuff, which will cause errors and give headaches to the people who configured it in the first place.

> **Note:** this repository doesn't include the SSH responder code. The deployed baseline detects world-open SSH with the AWS Config rule `policyholder-restricted-ssh` (`INCOMING_SSH_DISABLED`) on the lab security group.

## Reflecting on Security Automation Skills

### Tools and security concepts applied

The key tools I used include Lambda, CloudFormation, CloudTrail, CloudShell, Amazon EventBridge, Amazon SNS, and GitHub with Git. The concepts I learnt include figuring out why uploading a .yaml file was not connecting with the AWS config I used with Git, and having patience overall; it took me a while to know why the stack was not connecting and to understand how the configuration gap started, and what to do to prevent that.

### Project timeline and challenges

This project took me approximately 2 days. The most challenging part was connecting my GitHub to my CloudFormation; it generally took a significant amount of my time, but I'm glad I was able to try another way, since it was a new account because there was a problem with my current one for some reason.

### Next steps in cloud security

I did this project today to learn how to connect my GitHub to CloudFormation and use AWS Lambda to repair the gap, and with EventBridge, I get a notification if something happens in my account. Next, I want to go deeper into Infrastructure as Code.

## Deploy (us-east-2)

1. **Baseline stack:** create the stack `policyholder-security-baseline` in `us-east-2` with CloudFormation **Sync from Git**, pointing at this repo, branch `main`, and the deployment file `cfn-publish.json` (set `AlertEmail` to your address first). Or deploy it from the CLI:
   ```bash
   aws cloudformation deploy --region us-east-2 --stack-name policyholder-security-baseline \
     --template-file templates/baseline.yaml --parameter-overrides AlertEmail=you@example.com \
     --capabilities CAPABILITY_IAM
   ```
   Confirm the SNS subscription email.
2. **Remediation stack:** package the Lambda and deploy `templates/remediation.yaml` with the baseline stack's `ProtectedBucketName` and `AlertTopicArn` outputs (`ARTIFACT_BUCKET` is any S3 bucket you own in `us-east-2`):
   ```bash
   mkdir -p build/lambda && cp lambda/handler.py build/lambda/
   aws cloudformation package --region us-east-2 --template-file templates/remediation.yaml \
     --s3-bucket "$ARTIFACT_BUCKET" --output-template-file packaged-remediation.yaml
   aws cloudformation deploy --region us-east-2 --stack-name policyholder-remediation \
     --template-file packaged-remediation.yaml \
     --parameter-overrides ProtectedBucketName=<bucket> AlertTopicArn=<topic-arn> \
     --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND
   ```
3. **SCP:** `policies/cloudtrail-protection-scp.json` is validated in CI by `scripts/validate_scp.py` and stays unattached. Attaching it requires AWS Organizations.

Every push and pull request runs the GitHub Actions gate in `.github/workflows/iac-security.yml` (cfn-lint, checkov, a Lambda compile check, and the SCP check).

## Clean up

1. Delete the remediation stack: `aws cloudformation delete-stack --region us-east-2 --stack-name policyholder-remediation`
2. Turn off Git sync for the baseline stack so a later push doesn't redeploy it.
3. Empty the protected bucket (`aws s3 rm s3://<ProtectedBucketName> --recursive`), then delete the baseline stack: `aws cloudformation delete-stack --region us-east-2 --stack-name policyholder-security-baseline`
4. The audit bucket uses `DeletionPolicy: Retain`, so delete it by hand when you no longer need the logs: `aws s3 rb s3://<AuditBucketName> --force`
