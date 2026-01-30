# AWS Health Checker 🔍

A Python command-line tool for monitoring AWS infrastructure health. Checks EC2 instance status and CloudWatch alarms, providing quick visibility into your AWS environment's operational state.

## Features

- ✅ **EC2 Monitoring** - Check status of all EC2 instances
- ✅ **CloudWatch Alarms** - View alarm states (OK, ALARM, INSUFFICIENT_DATA)
- ✅ **Summary Report** - Quick overview of infrastructure health
- ✅ **JSON Export** - Save reports for documentation or further processing
- ✅ **Multi-Region** - Check any AWS region

## Prerequisites

- Python 3.8 or higher
- AWS credentials configured (`aws configure`)
- IAM permissions for EC2 and CloudWatch read access

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/aws-health-checker.git
cd aws-health-checker

# Install dependencies
pip install -r requirements.txt
