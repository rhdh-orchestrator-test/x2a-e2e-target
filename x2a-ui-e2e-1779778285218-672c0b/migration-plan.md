# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The repository also contains Chef server and Automate deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https_verify**:
    - Description: InSpec tests for verifying HTTPS website configuration, port status, and SSL/TLS protocols
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: HTTPS validation, port checking, SSL protocol verification

- **ssh_profile**:
    - Description: InSpec compliance profile for SSH security configuration validation
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check, CCI compliance mapping, STIG validation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef Server CLI
    - Key Features: User creation, organization setup, server configuration

- **automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef Automate CLI
    - Key Features: Combined Automate and Infra Server deployment, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `website_https.yml`: Ansible playbook for configuring HTTPS website with Apache. No migration needed as it's already in Ansible format.
- `poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability in Apache. No migration needed as it's already in Ansible format.
- `index.html`: Sample HTML file used by the website playbook. No migration needed.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for both on-premises and cloud deployment (based on comments in deployment scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible's `assert` module for basic testing
  - Option 2: Molecule for comprehensive test-driven development
  - Option 3: Maintain InSpec as a standalone tool called from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSH Security Controls**: The SSH compliance profile checks for root login restrictions. Ensure these security checks are maintained in the Ansible migration.
- **SSL/TLS Protocol Security**: The InSpec tests verify that insecure protocols (SSL3) are disabled and secure protocols (TLS 1.2) are enabled. Maintain these security validations in the Ansible migration.
- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated dynamically in the playbooks, which is a good practice to maintain

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach may require additional logic and careful validation to ensure equivalent test coverage.
  - Mitigation: Consider using Ansible's `assert` module combined with `command`/`shell` modules to replicate InSpec's functionality, or maintain InSpec as a separate tool called from Ansible.

- **Chef Server Deployment**: The Chef server deployment scripts contain specific Chef CLI commands that need Ansible equivalents.
  - Mitigation: Create Ansible roles that use the `command` module to execute the necessary Chef CLI commands, or preferably, replace with native Ansible modules for similar functionality.

### Migration Order

1. **Ansible Playbook Testing Framework** (High value, low risk): Replace Test Kitchen with Molecule while maintaining existing Ansible playbooks
2. **InSpec Test Conversion** (Moderate complexity): Convert InSpec tests to Ansible-compatible testing
3. **Deployment Script Conversion** (High complexity): Convert Chef server and Automate deployment scripts to Ansible playbooks

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, based on the README description.
2. The InSpec tests are meant to validate the configurations applied by the Ansible playbooks, not to replace them.
3. The deployment scripts are intended for initial setup of Chef infrastructure, which would be replaced entirely by Ansible in the migration.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in production.
5. The existing Ansible playbooks (`website_https.yml` and `poodle_fix.yml`) are already in the target format and don't require migration.