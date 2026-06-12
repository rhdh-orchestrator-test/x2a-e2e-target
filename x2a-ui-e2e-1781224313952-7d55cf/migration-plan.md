# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks. The estimated timeline for this migration is 1-2 weeks given the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks with STIG references

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing web server functionality. No migration needed as it's a static asset.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be environment-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Consider Ansible Lint for static analysis

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/Jenkins for pipeline integration
  - Ansible Vault for secrets management

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the Apache configuration
  - Approach: Convert the existing Ansible tasks in poodle_fix.yml to roles with proper documentation

- **SSH Hardening**: The SSH security checks need to be maintained
  - Approach: Convert InSpec tests to Ansible assert tasks or Molecule verify tests

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup scripts (username, password)
  - Approach: Move credentials to Ansible Vault

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Create custom Ansible modules or use assert with carefully crafted conditions

- **Compliance Reporting**: InSpec provides built-in compliance reporting that needs to be replicated
  - Mitigation: Integrate with tools like Ansible AWX/Tower for reporting or use custom reporting scripts

- **Chef Server Functionality**: Replacing Chef Server's node management and policy features
  - Mitigation: Implement Ansible inventory management and AWX/Tower for similar functionality

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, just need refactoring to follow best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible-compatible testing
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires complete rewrite as Ansible playbooks

### Assumptions

1. The current setup uses Test Kitchen to provision a Vagrant VM, run Ansible playbooks, and verify with InSpec tests
2. The InSpec tests are used for compliance validation rather than functional testing
3. There are no additional Chef cookbooks or recipes beyond what's visible in the repository
4. The deployment scripts are used for setting up Chef infrastructure, which will be replaced by Ansible infrastructure
5. No external dependencies or integrations beyond what's explicitly mentioned in the files
6. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
7. The self-signed certificates are acceptable for the target environment (not requiring integration with external CA)
8. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be properly secured in the migration