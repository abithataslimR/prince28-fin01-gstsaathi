
# GSTSaathi

[![CI](https://github.com/abithataslimR/prince28-fin01-gstsaathi/actions/workflows/ci.yml/badge.svg)](https://github.com/abithataslimR/prince28-fin01-gstsaathi/actions/workflows/ci.yml)

[![Live](https://img.shields.io/website?url=https%3A%2F%2Fgstsaathi.onrender.com%2Fhealth&label=live)](https://gstsaathi.onrender.com/docs)

[![Uptime (30 days)](https://img.shields.io/uptimerobot/ratio/m804749270-3670f7c8f791ec0b9f724ed5)](https://gstsaathi.onrender.com/health)

**Live:** Week 1 complete · Live at https://gstsaathi.onrender.com

## What is GSTSaathi?

GSTSaathi helps small manufacturers answer GST-related questions, find GST rates by HSN code and date, understand Input Tax Credit (ITC), reconcile invoices, and manage compliance.

## Who it's for

An accountant working at a 40-employee pump-set manufacturing company in Coimbatore who needs reliable GST information for everyday business operations.

## The problem

Finding the correct historical GST rate for a product based on its HSN code and the applicable date can be difficult. Incorrect rates can lead to billing mistakes and compliance issues.

## Data sources

- [CBIC](https://cbic-gst.gov.in/)
- [GST Council](https://gstcouncil.gov.in/)
- [GST Portal](https://www.gst.gov.in/)

## Hardest problem

GST rates can change over time. The application must identify the correct rate based on the HSN code and the date of the transaction.

## Signature feature

**HSN Rate Timeline:** Shows GST rate changes over time so users can identify the applicable rate for a particular date.

## Target metric

Achieve 95% or higher accuracy on a test set of 50 HSN-code and date combinations.

## Run locally

Clone the repository:

```bash
git clone https://github.com/abithataslimR/prince28-fin01-gstsaathi.git
cd prince28-fin01-gstsaathi
```

Install dependencies and run the application according to the project setup instructions.

## Checks

The project uses automated CI checks through GitHub Actions to validate code changes.

## Docker Compose

Docker Compose is used to run the application and its supporting services locally.

## API documentation

- Swagger UI: https://gstsaathi.onrender.com/docs
- Health check: https://gstsaathi.onrender.com/health

## Development and testing

| Area | Purpose |
|---|---|
| CI | Automatically checks code changes |
| CD | Deploys the application |
| Docker | Provides a consistent application environment |
| Health check | Verifies application availability |
| Uptime monitoring | Monitors the live application |
