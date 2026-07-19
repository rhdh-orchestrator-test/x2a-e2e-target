# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with Chef InSpec tests that need to be consolidated into a pure Ansible solution

The complexity is moderate, with the main challenge being replacing Chef InSpec testing with equivalent Ansible testing solutions. The estimated timeline for migration is 1-2 weeks, depending on testing requirements and validation processes.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure Apache web server with SSL, along with Chef InSpec tests for validation
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL certificate generation, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should replace with Ansible-native testing framework like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS. Can be retained but should be updated to follow current Ansible best practices.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Can be retained but should be updated to follow current Ansible best practices.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Needs to be converted to Ansible-native testing.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH hardening compliance. Needs to be converted to Ansible-native testing.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Needs to be converted to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs to be converted to Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider integrating with OpenSCAP for compliance testing

- **Test Kitchen**: Replace with Molecule for Ansible role/playbook testing

- **Chef Automate/Infra Server**: Determine if equivalent functionality is needed:
  - If Chef is being used for configuration management: Replace with pure Ansible
  - If Chef is being used for compliance: Consider Ansible AWX/Tower with compliance plugins
  - If Chef is being used for reporting: Consider Ansible AWX/Tower with reporting features

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure the migration maintains:
  - TLS 1.2 enforcement (as seen in poodle_fix.yml)
  - Self-signed certificate generation (or integrate with Let's Encrypt)
  - Proper certificate permissions

- **SSH Hardening**: The InSpec tests check for SSH root login disablement. Ensure the migration:
  - Maintains SSH hardening checks
  - Implements equivalent controls in Ansible

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets identified in setup scripts (username/password in deploy-automate.sh and deploy-chef-server.sh)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing mechanisms will require careful mapping of test assertions.
  - Mitigation: Create a mapping document for InSpec resources to Ansible assertions
  - Consider using Ansible's `assert` module with custom facts gathering

- **Chef Server Deployment**: If Chef Server functionality is still needed, determine how to manage it with Ansible.
  - Mitigation: Evaluate if Chef Server can be replaced entirely with Ansible AWX/Tower
  - If Chef Server must be retained, create Ansible playbooks to deploy and manage it

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/website_https.yml, chef-and-ansible/poodle_fix.yml): Low risk, already in Ansible format
   - Update to current Ansible best practices
   - Replace Test Kitchen with Molecule

2. **InSpec Tests** (chef-and-ansible/tests/website_https_verify.rb, chef-and-ansible/tests/ssh_profile.rb): Moderate complexity
   - Convert to Ansible assertions or Molecule verifiers
   - Validate equivalent test coverage

3. **Chef Deployment Scripts** (setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh): High complexity
   - Convert to Ansible playbooks
   - Implement secret management with Ansible Vault
   - Test deployment thoroughly

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production, based on the README.md content.
2. The Chef Automate and Chef Infra Server deployment is intended for on-premises or generic cloud VMs, not a specific cloud provider.
3. The hardcoded credentials in the setup scripts are for demonstration purposes and would be replaced with secure credentials in production.
4. The InSpec tests are used for compliance validation of the deployed infrastructure.
5. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration.
6. The migration goal is to eliminate Chef dependencies entirely, not to maintain a hybrid Chef/Ansible environment.
7. The Apache configuration is for demonstration purposes and may need to be updated for current security best practices.
8. The SSL certificate generation is for testing/demonstration and would be replaced with proper certificates in production.