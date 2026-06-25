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
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance tagging (STIG, CCI)

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Use Ansible Molecule with Goss for simpler test cases
  - Option 3: Convert InSpec tests to Ansible assert tasks for direct integration

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Server**: Replace deployment scripts with Ansible roles that can:
  - Configure system requirements (hostname, sysctl parameters)
  - Install alternative compliance and infrastructure management tools:
    - AWX/Ansible Tower for infrastructure management
    - Compliance solutions like OpenSCAP or Ansible Automation Platform

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Approach: Maintain the same SSL protocol restrictions in the Ansible playbooks

- **SSH Security**: The SSH root login compliance check needs to be preserved
  - Approach: Convert the InSpec control to an Ansible task that checks the same configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected:
    - chef-automate-deployment: 3 (username, password, email)
    - chef-server-deployment: 3 (username, password, email)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks
  - Mitigation: Use Ansible's assert module or Molecule with Testinfra to replicate InSpec functionality
  - Challenge level: Medium

- **Compliance Tagging**: InSpec tests contain compliance metadata (STIG, CCI) that needs preservation
  - Mitigation: Document compliance mappings in Ansible task comments or separate documentation
  - Challenge level: Low

- **Chef Server Replacement**: Determining the appropriate replacement for Chef Server functionality
  - Mitigation: Evaluate if Ansible Tower/AWX meets the requirements or if additional tools are needed
  - Challenge level: Medium

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, just need review and potential refactoring to follow best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Medium complexity, requires conversion to Ansible-compatible testing framework
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires complete rewrite as Ansible playbooks and determination of replacement technologies

### Assumptions

1. The primary goal is to consolidate on Ansible as the single automation tool, eliminating Chef components
2. The existing Ansible playbooks are functional and follow best practices
3. The InSpec tests are providing value that should be preserved in the Ansible ecosystem
4. The deployment scripts for Chef Automate/Server need to be replaced with equivalent functionality in Ansible
5. No specific compliance framework requirements beyond what's documented in the InSpec tests
6. The target environment will continue to be Ubuntu 20.04 or compatible systems
7. The self-signed certificates are acceptable for the environment (not production)
8. The hardcoded credentials in the deployment scripts are for demonstration purposes only