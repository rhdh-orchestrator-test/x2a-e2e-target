# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef Automate/Infra Server deployment scripts. The migration scope is relatively small, focusing on:

1. Consolidating existing Ansible playbooks into a standardized Ansible structure
2. Converting Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks
3. Preserving the InSpec compliance testing functionality within the Ansible framework

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the limited scope of the repository.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS website configuration
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `index.html`: Simple HTML page for the website example

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles
- **InSpec**: Maintain InSpec tests but integrate with Ansible using ansible_inspec_callback or convert to Ansible assert modules
- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management solution

### Security Considerations

- **SSL Configuration**: The poodle_fix.yml playbook enforces TLSv1.2 and disables older protocols. This security hardening should be preserved in the migrated Ansible roles.
- **SSH Hardening**: The ssh_profile.rb InSpec test verifies SSH root login is disabled. This security check should be maintained.
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates. Consider enhancing with Let's Encrypt integration for production environments.
- **Vault/secrets management**: 
  - Hardcoded credentials in setup-automate scripts (username, password)
  - These should be moved to Ansible Vault or another secrets management solution

### Technical Challenges

- **InSpec Integration**: Ensuring InSpec tests continue to work with the new Ansible structure. Mitigation: Use ansible_inspec_callback or convert tests to Ansible assertions.
- **Chef Automate Replacement**: Determining the appropriate Ansible-based replacement for Chef Automate functionality. Mitigation: Evaluate AWX/Tower or other Ansible management platforms.
- **Testing Framework**: Replacing Test Kitchen with Molecule while maintaining test coverage. Mitigation: Create equivalent Molecule scenarios for existing Test Kitchen tests.

### Migration Order

1. **website_https playbook** (low risk, already Ansible)
   - Refactor into proper Ansible role structure
   - Update handlers and variable management

2. **poodle_fix playbook** (low risk, already Ansible)
   - Refactor into proper Ansible role structure
   - Combine with website_https role as an optional security enhancement

3. **InSpec tests** (moderate complexity)
   - Set up integration with Ansible using ansible_inspec_callback
   - Alternatively, convert to Ansible assert modules

4. **Chef deployment scripts** (high complexity)
   - Convert to Ansible roles for deploying alternative configuration management solution
   - Implement secure credential management using Ansible Vault

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment, based on the README content.
2. The Chef Automate and Chef Infra Server deployment scripts are intended to be replaced rather than integrated with Ansible.
3. InSpec testing is a critical component that must be preserved in some form.
4. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration.
5. The hardcoded credentials in the deployment scripts are examples and not actual production credentials.
6. The Apache configuration in the Ansible playbooks represents the actual desired state for web servers.