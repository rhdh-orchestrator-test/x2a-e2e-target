# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a unified Ansible approach. The repository appears to be a demonstration/example repository showing Chef InSpec for compliance testing alongside Ansible playbooks, as well as Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few components to migrate, making this a low-complexity migration that could be completed in 1-2 weeks.

## Module Migration Plan

This repository contains Chef InSpec profiles, Ansible playbooks, and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration compliance testing, STIG compliance checks

- **website_https_verify**:
    - Description: Chef InSpec profile that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **deploy-automate**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **deploy-chef-server**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Likely a Test Kitchen configuration file for testing the Chef InSpec profiles with Ansible playbooks
- `chef-and-ansible/index.html`: Static HTML file, possibly used as a template or example

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu (evidenced by apt package manager in Ansible playbooks with specific package versions like apache2=2.4.41-4ubuntu3.10)
- **Virtual Machine Technology**: Not specified, but scripts are designed to work on both on-premises VMs and cloud instances
- **Cloud Platform**: Not specified, appears to be cloud-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Migrate InSpec profiles to Ansible's `ansible-lint` for static analysis
  - Use Ansible's built-in `assert` module for runtime validation
  - Consider integrating with Ansible's `molecule` for testing
  - Alternatively, maintain InSpec as a compliance tool but invoke it from Ansible

- **Chef Automate/Infra Server**: Replace with Ansible automation platform:
  - Migrate Chef Automate functionality to Ansible Automation Platform
  - Replace Chef Server with Ansible Tower/AWX for centralized management
  - Create Ansible playbooks to handle the deployment tasks currently done by the bash scripts

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening present in the POODLE fix playbook
  - Ensure TLSv1.2 remains enabled and older protocols disabled
  - Maintain proper certificate generation and management

- **SSH Hardening**: Maintain the SSH security controls verified by the InSpec profile
  - Ensure root login remains disabled in the migrated solution
  - Implement equivalent compliance checks in Ansible

- **Vault/secrets management**: 
  - Hardcoded credentials in the deployment scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets detected (username/password in both deployment scripts)

### Technical Challenges

- **Compliance Testing**: The biggest challenge will be replacing Chef InSpec's compliance testing capabilities
  - InSpec provides specialized security testing that may require multiple Ansible modules to replicate
  - Solution: Use a combination of Ansible's `assert`, `command`, and `shell` modules to perform equivalent checks

- **Certificate Management**: The self-signed certificate generation needs to be properly migrated
  - Solution: Use Ansible's `openssl_*` modules (already in use in the existing playbooks)

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they're already in Ansible format, just need review and potential refactoring
2. **InSpec Profiles** (ssh_profile.rb, website_https_verify.rb) - Medium complexity, requires converting Ruby-based tests to Ansible assertions
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - Higher complexity, requires replacing Chef-specific tooling with Ansible equivalents

### Assumptions

1. The repository is primarily for demonstration/educational purposes and may not represent a production environment
2. The InSpec profiles are used for compliance validation of infrastructure provisioned by Ansible
3. The deployment scripts are used to set up a Chef environment, which would be replaced entirely by Ansible
4. No actual Chef cookbooks or recipes are present in the repository that need migration
5. The target environment is Ubuntu-based (based on apt usage in playbooks)
6. The migration will maintain the same level of security compliance checking currently provided by InSpec
7. The hardcoded credentials in deployment scripts are for demonstration purposes only