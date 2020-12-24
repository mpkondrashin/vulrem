#!/bin/bash
# VulRem - Vulnerability Remediation
# run_main.sh - script for test run

export SMARTCHECK_URL="https://<DSSC Address>:<DSSC Port>"
export SMARTCHECK_SKIP_TLS_VERIFY="True"
export SMARTCHECK_USERNAME="<username>"
export SMARTCHECK_PASSWORD="<password"

export DEEPSECURITY_URL="https://<DSM address>:4119/api"
export DEEPSECURITY_SKIP_TLS_VERIFY="True"
export DEEP_SECURITY_API_KEY="<API key>"
export DEEPSECURITY_POLICY_ID="<Policy ID>"

python main.py

