# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

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
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Sample HTML file used for testing the web server setup. Can be preserved as-is or incorporated into Ansible as a template.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Maintain InSpec but invoke it from Ansible using the `command` or `shell` module

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or Ansible's own testing frameworks

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - Git repositories for configuration management
  - Optional CI/CD integration (Jenkins, GitLab CI, etc.)

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Ensure these security settings are preserved in the migrated solution.
  - Migration approach: Maintain the same SSL protocol restrictions (TLSv1.2) in the Ansible playbooks.

- **SSH Security**: The InSpec tests verify SSH root login is disabled. Ensure this security check is maintained.
  - Migration approach: Convert the InSpec test to Ansible assert or Molecule verify tests.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts: The deploy scripts contain hardcoded username/password. These should be moved to Ansible Vault.
  - Self-signed certificates: The playbook generates self-signed certificates. Consider using Ansible Vault for storing production certificates.
  - Count of credentials detected: 2 (username/password in deployment scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks may require learning new testing approaches.
  - Mitigation: Start with simple assertions and gradually build more complex tests. Consider using Molecule which provides a structured testing framework.

- **Chef Automate/Server Deployment**: Replacing Chef Automate and Chef Infra Server with Ansible AWX/Tower requires understanding the equivalent functionality.
  - Mitigation: Create a mapping of Chef Automate features to Ansible AWX/Tower features to ensure all required functionality is covered.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format and can be preserved with minimal changes.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible testing frameworks.
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity as they involve replacing Chef Automate/Server with Ansible AWX/Tower.

### Assumptions

1. The existing Ansible playbooks are working correctly and don't require functional changes.
2. The team is familiar with Ansible but may need training on Ansible testing frameworks to replace InSpec.
3. The security requirements enforced by the InSpec tests must be maintained in the Ansible solution.
4. The deployment scripts are used for setting up development/test environments and not production environments (given the hardcoded credentials).
5. The repository is primarily for demonstration purposes as indicated by the README, so some simplifications may be acceptable.
6. The migration will include setting up equivalent functionality to Chef Automate using Ansible AWX/Tower.
7. No external dependencies or integrations beyond what's visible in the repository need to be considered.