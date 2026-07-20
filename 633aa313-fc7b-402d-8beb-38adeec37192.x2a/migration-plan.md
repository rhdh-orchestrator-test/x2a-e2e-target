# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests that demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting the existing InSpec tests to Ansible-compatible testing frameworks while maintaining the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.
**Complexity**: Low to Medium - The repository primarily contains Ansible playbooks already with InSpec tests for validation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Directory containing Ansible playbooks for Apache HTTPS setup and SSL security fixes, along with InSpec tests
    - Path: chef-and-ansible
    - Technology: Ansible + Chef InSpec
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup, security compliance testing

- **setup-automate**:
    - Description: Directory containing bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-compatible testing framework configuration.
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment. Can be reused as-is in the Ansible playbook.
- `chef-and-ansible/website_https.yml`: Ansible playbook for setting up HTTPS website.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL configuration.
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec test for SSH security configuration.
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test for HTTPS functionality and security.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server without Automate.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or maintain Test Kitchen with the `kitchen-ansible` plugin

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure the migration maintains:
  - Proper SSL protocol settings (TLSv1.2 enforcement)
  - Self-signed certificate generation
  - Secure virtual host configuration

- **SSH Security**: The InSpec tests verify SSH root login is disabled. Ensure:
  - SSH hardening is maintained in the migrated solution
  - Compliance with security standards (SRG-OS-000112, V-38607, etc.)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks will require:
  - Understanding the assertions being made in the InSpec tests
  - Implementing equivalent checks in Ansible or Molecule
  - Ensuring the same level of compliance validation

- **Chef Automate/Server Deployment**: Converting the bash scripts to Ansible playbooks will require:
  - Understanding the Chef Automate/Server installation process
  - Creating idempotent Ansible tasks for each step
  - Handling user and organization creation
  - Managing SSL certificates and system requirements

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format. Review and update as needed.
2. **Testing Framework**: Implement Molecule or another Ansible-compatible testing solution to replace InSpec.
3. **Test Conversion**: Convert the InSpec tests to the new testing framework.
4. **Chef Deployment Scripts**: Convert the bash scripts to Ansible playbooks.

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the existing Ansible playbooks.
2. The target environment will continue to be Ubuntu 20.04 or compatible systems.
3. The security requirements and compliance standards referenced in the InSpec tests must be maintained.
4. The repository is primarily for demonstration purposes rather than production use.
5. No external Chef cookbooks or complex Chef-specific features are in use.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be properly secured in the migrated solution.