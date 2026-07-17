# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be consolidated into a unified Ansible approach. The repository primarily consists of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec tests for validating security compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is relatively low as most of the infrastructure code is already in Ansible format. The main focus will be on converting the Chef InSpec tests to Ansible-compatible testing frameworks and replacing the Chef Automate/Infra Server deployment scripts with Ansible playbooks.

Estimated timeline: 2-3 weeks for a complete migration, with the majority of time spent on testing and validation.

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Apache web server configuration with SSL/TLS setup
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-vulnerability-fix**:
    - Description: Security fix for POODLE vulnerability in Apache SSL configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **compliance-testing**:
    - Description: InSpec tests for validating HTTPS configuration and SSH security
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: Port validation, HTTPS content verification, SSL protocol verification, SSH root login check

- **chef-infrastructure-deployment**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts using Chef tooling
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `chef-and-ansible/index.html`: Sample HTML file for website testing
- `chef-and-ansible/README.md`: Documentation for Chef InSpec with Ansible integration

### Target Details

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible Test for playbook validation
  - Option 3: Integration with other testing frameworks like Serverspec or Testinfra

- **Test Kitchen**: Replace with Molecule for Ansible role testing and development

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or GitHub Actions for pipeline automation
  - Ansible Vault for secrets management

### Security Considerations

- **SSL/TLS Configuration**: The current playbooks enforce TLSv1.2 and disable vulnerable protocols. Migration should maintain or enhance this security posture.
  - Migration approach: Preserve the same SSL/TLS hardening in the consolidated Ansible playbooks

- **SSH Security**: InSpec tests verify SSH root login is disabled.
  - Migration approach: Implement equivalent checks using Ansible's assert module or Molecule

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated dynamically but should be managed securely
  - Document the count and type of credentials detected per module:
    - chef-infrastructure-deployment: 1 user password in plain text

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification methods
  - Mitigation: Use Ansible's uri module for HTTP checks, assert module for validation, and command module with OpenSSL for SSL protocol verification

- **Chef Server Deployment**: Replacing Chef server deployment with equivalent Ansible management
  - Mitigation: Implement AWX/Tower deployment playbooks and document migration path for existing Chef-managed nodes

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - No conversion needed, just code review and potential optimization

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - No conversion needed, just code review and potential optimization
   - Consider merging with website-https-configuration for a unified approach

3. **compliance-testing** (moderate complexity)
   - Convert InSpec tests to Ansible-compatible testing framework
   - Implement equivalent checks using Ansible modules

4. **chef-infrastructure-deployment** (high complexity)
   - Create Ansible playbooks for AWX/Tower deployment
   - Implement user and organization management in Ansible

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, as indicated by the README.md mentioning "working examples" and "companion to a white paper".

2. The Chef InSpec tests are used for compliance validation of infrastructure deployed by Ansible, suggesting a hybrid approach that will be consolidated to pure Ansible.

3. The setup-automate scripts are used for deploying Chef infrastructure, which will be replaced by Ansible management tools.

4. The target environment is Ubuntu 20.04 running on Vagrant VMs for testing purposes.

5. There are no complex Chef cookbooks or recipes that need migration, as the repository focuses on InSpec tests and simple Ansible playbooks.

6. The security requirements include TLS 1.2 enforcement and SSH hardening, which must be maintained in the migrated solution.