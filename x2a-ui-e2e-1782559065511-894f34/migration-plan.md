# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **inspec-website-tests**:
    - Description: Chef InSpec tests that verify HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS content verification, SSL protocol security verification

- **inspec-ssh-profile**:
    - Description: Chef InSpec profile that verifies SSH security configurations
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec
- `index.html`: Sample HTML file used for testing the web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use pytest-ansible for Python-based testing
  - Option 3: Integrate with ansible-lint for static analysis

- **Test Kitchen**: Replace with Ansible Molecule for infrastructure testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/Jenkins for pipeline integration
  - Compliance scanning can be handled by OpenSCAP integration with Ansible

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Approach: Maintain the same configuration parameters in the Ansible playbooks

- **SSH Hardening**: The SSH security profile needs to be converted to Ansible-compatible tests
  - Approach: Convert InSpec tests to Ansible assert tasks or Molecule verify tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's Ruby-based testing syntax to Ansible's YAML-based assertions
  - Mitigation: Use Ansible's assert module or consider integrating with a Python testing framework

- **Compliance Metadata**: Preserving STIG and CCI compliance metadata from InSpec tests
  - Mitigation: Document compliance requirements separately or use Ansible tags and custom variables to maintain metadata

- **Chef Server Functionality**: Replacing Chef Server user and organization management
  - Mitigation: Use Ansible AWX/Tower for team management and inventory organization

### Migration Order

1. **website-https playbook** (already in Ansible, no migration needed)
2. **poodle-fix playbook** (already in Ansible, no migration needed)
3. **inspec-website-tests** (convert to Ansible Molecule tests)
4. **inspec-ssh-profile** (convert to Ansible security role with appropriate tests)
5. **chef-automate-deployment** (convert to Ansible playbook for AWX/Tower deployment)
6. **chef-server-deployment** (convert to Ansible playbook for AWX/Tower deployment)

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't need modification
2. The repository is primarily used for demonstration purposes rather than production deployment
3. The compliance requirements in the InSpec tests need to be preserved in the Ansible migration
4. The Chef Automate and Chef Infra Server deployment scripts are used for actual infrastructure setup
5. No external Chef cookbooks or dependencies are being used beyond what's visible in the repository
6. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
7. The migration will need to maintain the same level of security compliance testing
8. No custom Chef resources or complex Chef-specific functionality is being used