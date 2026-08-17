# MIGRATION FROM CHEF AND BASH SCRIPTS TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests, Ansible playbooks, and Bash scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, with most components already using Ansible. The primary migration tasks involve converting the Chef Automate and Chef Infra Server deployment scripts from Bash to Ansible playbooks, and ensuring the InSpec tests can be integrated into an Ansible-based workflow.

**Estimated Timeline**: 1-2 weeks for a complete migration, with minimal complexity due to the small codebase and existing Ansible components.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Automated deployment of Chef Automate and Chef Infra Server, user and organization creation

- **website-https**:
    - Description: Ansible playbook for deploying a secure web server with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook for fixing SSL vulnerabilities in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **compliance-tests**:
    - Description: Chef InSpec tests for verifying SSH security and HTTPS configuration
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, HTTPS port verification, SSL protocol verification

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `chef-and-ansible/index.html`: Sample HTML file for website testing
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for both on-premises and cloud environments (based on comments in the deployment scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Integrate with ansible-test for more comprehensive testing
  - Option 3: Keep InSpec as a verification tool but invoke it from Ansible

- **Chef Automate/Infra Server**: Replace with Ansible automation platform:
  - Ansible AWX/Tower for web UI and job scheduling
  - Ansible Galaxy for role and collection management
  - Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL Configuration**: The existing playbooks configure Apache with secure SSL settings (TLSv1.2 only). This should be maintained in the migrated solution.
  - Migration approach: Use the `apache2_module` and `apache2_conf` Ansible modules instead of the `replace` module for more idempotent configuration.

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled.
  - Migration approach: Create an Ansible role for SSH hardening that applies the same security controls, with verification using ansible-lint or another compliance tool.

- **Self-signed Certificates**: The current solution generates self-signed certificates.
  - Migration approach: Maintain this approach for development/testing but add support for proper CA-signed certificates in production environments.

- **Vault/secrets management**: 
  - Hardcoded credentials in Bash scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in the deployment scripts

### Technical Challenges

- **InSpec Test Integration**: The current setup uses InSpec for compliance testing.
  - Mitigation: Either maintain InSpec as a separate tool called from Ansible, or migrate tests to an Ansible-native solution like ansible-lint or molecule.

- **Chef Server Deployment**: The current solution deploys Chef Server, which won't be needed in an Ansible-only environment.
  - Mitigation: Replace with Ansible AWX/Tower deployment playbooks.

### Migration Order

1. **chef-automate-deployment** (moderate complexity): Convert Bash scripts to Ansible playbooks, replacing Chef Automate/Infra Server with Ansible AWX/Tower.
2. **compliance-tests** (moderate complexity): Convert InSpec tests to Ansible-native testing or integrate InSpec with Ansible workflow.
3. **website-https** and **poodle-fix** (low complexity): These are already Ansible playbooks and only need minor refactoring for best practices.

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments, based on the README indicating it's for "examples related to content created by the Technical Product Marketing and Developer Relations teams."
2. The Chef InSpec tests are intended to verify the configurations applied by the Ansible playbooks, suggesting a hybrid approach where Ansible is used for configuration and InSpec for verification.
3. The deployment scripts are designed to work in both cloud and on-premises environments, but specific cloud providers are not targeted.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure values in a production environment.
5. The Test Kitchen configuration suggests this is primarily a development/testing environment rather than production.