# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a pure Ansible solution. The repository primarily consists of:

1. Chef InSpec test profiles for compliance validation
2. Ansible playbooks for configuration management
3. Shell scripts for Chef Automate and Chef Infra Server deployment

The migration complexity is relatively low as most configuration management is already implemented in Ansible. The primary focus will be on converting Chef InSpec tests to Ansible-compatible testing frameworks and replacing Chef server deployment scripts with Ansible playbooks.

Estimated timeline: 2-3 weeks for a complete migration, with the majority of time spent on converting InSpec tests to an Ansible-compatible testing framework.

## Module Migration Plan

This repository contains a mix of Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook for deploying a secure HTTPS website with Apache
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache configuration, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook for fixing SSL vulnerabilities in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deploy**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Shell Script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Shell Script
    - Key Features: Chef Server installation, user and organization creation

- **ssh_profile**:
    - Description: Chef InSpec test profile for SSH security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login validation, compliance with security standards

- **website_https_verify**:
    - Description: Chef InSpec test profile for HTTPS website validation
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS content validation, SSL protocol verification

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `index.html`: Sample HTML file for website testing
- `README.md`: Documentation files explaining the repository purpose

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen (latest)**: Replace with:
  - Molecule for Ansible role and playbook testing
  - GitHub Actions or other CI/CD pipeline for automated testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for centralized management
  - GitOps workflow with CI/CD pipelines for configuration management

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation uses self-signed certificates generated with OpenSSL
  - Migration approach: Continue using Ansible's `openssl_*` modules for certificate management

- **SSH Security Hardening**:
  - Current implementation tests for disabled root login
  - Migration approach: Create Ansible role for SSH hardening that applies the same security controls

- **Hardcoded Credentials**:
  - Detected in setup-automate scripts (username, password)
  - Migration approach: Use Ansible Vault for secure credential storage

- **TLS Protocol Security**:
  - Current implementation enforces TLS 1.2 and disables older protocols
  - Migration approach: Create Ansible role for TLS hardening that applies the same security controls

### Technical Challenges

- **InSpec Test Conversion**: 
  - Challenge: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's `assert` module with custom scripts or consider maintaining InSpec for testing while using Ansible for configuration

- **Compliance Reporting**:
  - Challenge: Replacing Chef Automate's compliance reporting capabilities
  - Mitigation: Integrate with compliance tools like OpenSCAP or use AWX/Tower for reporting

- **User Management**:
  - Challenge: Replacing Chef Server's user and organization management
  - Mitigation: Implement RBAC through Ansible AWX/Tower or integrate with existing identity providers

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, just need review and potential refactoring
2. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb): Medium complexity, requires conversion to Ansible-compatible testing framework
3. **Chef Server Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires complete replacement with Ansible playbooks for AWX/Tower deployment

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, based on the README description.
2. The InSpec tests are used for validating configurations managed by Ansible, not Chef-managed resources.
3. There are no actual Chef cookbooks in this repository that need migration, only InSpec test profiles.
4. The deployment scripts for Chef Automate/Server are intended to be replaced with an Ansible AWX/Tower deployment.
5. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.
6. No external data sources or complex state management is required beyond what's visible in the repository.
7. The security requirements (TLS 1.2, disabled SSH root login) should be maintained in the migrated solution.