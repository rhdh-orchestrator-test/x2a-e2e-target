# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for demonstration purposes, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on standardizing all automation to Ansible. The complexity is low to moderate, with the main challenge being the conversion of Chef InSpec tests to Ansible-compatible testing frameworks. The estimated timeline for migration is 1-2 weeks, depending on testing requirements.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling older SSL protocols and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH root login security compliance
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality
- `chef-and-ansible/index.html`: Sample HTML file for testing web server deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml as the driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions like Molecule with Testinfra or ansible-test
- **Test Kitchen (latest)**: Replace with Molecule for Ansible role/playbook testing
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source alternatives like AWX

### Security Considerations

- **SSL/TLS Configuration**: The poodle_fix.yml playbook enforces TLSv1.2 only. This security hardening should be preserved in the migrated solution.
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates. Consider implementing a more robust certificate management solution in the migrated Ansible playbooks.
- **SSH Security**: The ssh_profile.rb InSpec test verifies that root login via SSH is disabled. This security check should be implemented in the Ansible testing framework.
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - No other credential patterns detected in the repository

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to an Ansible-compatible testing framework will require careful mapping of InSpec resources to equivalent testing constructs.
  - Mitigation: Use Molecule with Testinfra or ansible-test for infrastructure testing, ensuring all compliance checks are preserved.

- **Chef Automate Replacement**: Determining the appropriate replacement for Chef Automate functionality.
  - Mitigation: Evaluate Ansible Automation Platform or AWX as potential replacements, focusing on compliance reporting capabilities.

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
   - No conversion needed, just review and optimize
   - Update testing framework

2. **poodle_fix.yml** (low risk, already in Ansible format)
   - No conversion needed, just review and optimize
   - Update testing framework

3. **InSpec Tests** (moderate complexity)
   - Convert to Molecule with Testinfra or ansible-test
   - Ensure all compliance checks are preserved

4. **Chef Deployment Scripts** (high complexity)
   - Convert to Ansible roles for infrastructure deployment
   - Implement Ansible Vault for credential management

### Assumptions

1. The repository is primarily for demonstration purposes as indicated by the README.md files, not for production use.
2. The InSpec tests are intended to verify compliance of systems managed by Ansible.
3. The Chef Automate and Chef Infra Server deployment scripts are intended for setting up a Chef environment, which would be replaced by an Ansible management environment.
4. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file.
5. The current implementation uses Vagrant for local testing, which can be maintained or replaced with other virtualization technologies.
6. No external dependencies or complex integrations are present beyond what's visible in the repository.
7. The migration goal is to standardize on Ansible rather than maintain a hybrid Chef/Ansible environment.