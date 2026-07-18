# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on two main components:

1. Ansible playbooks for deploying and securing Apache web servers
2. Chef InSpec tests for validating security compliance

Additionally, there are Chef Automate and Chef Infra Server deployment scripts that will need to be replaced with Ansible-based deployment solutions.

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a single engineer to complete. The primary focus will be on replacing Chef InSpec tests with Ansible-native testing solutions while preserving the existing Ansible playbooks with minor improvements.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Directory containing Ansible playbooks for Apache HTTPS deployment and Chef InSpec tests for compliance validation
    - Path: chef-and-ansible
    - Technology: Ansible + Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL security hardening, compliance testing

- **chef-and-ansible/tests**:
    - Description: Directory containing Chef InSpec test files for compliance validation
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS configuration validation, SSH security compliance testing

- **setup-automate**:
    - Description: Directory containing Chef Automate and Chef Infra Server deployment scripts
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef infrastructure deployment automation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache web server with HTTPS configuration
  - Migration consideration: Convert to Ansible role with proper variable management
  
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability in Apache
  - Migration consideration: Integrate into a comprehensive security hardening role
  
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec tests for validating HTTPS configuration
  - Migration consideration: Convert to Ansible assert statements or Molecule tests
  
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec profile for SSH security compliance
  - Migration consideration: Convert to Ansible security role with compliance checks
  
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
  - Migration consideration: Replace with Ansible Molecule for testing
  
- `chef-and-ansible/index.html`: Sample HTML file for web server deployment
  - Migration consideration: Can be used as-is or templated in Ansible
  
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
  - Migration consideration: Replace with Ansible playbook for AWX/Tower deployment
  
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server
  - Migration consideration: Replace with Ansible playbook for management infrastructure

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but scripts are designed to work on cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Use Ansible Molecule for more comprehensive testing
  - Option 3: Integrate with OpenSCAP or other compliance tools via Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for orchestration and management
  - GitLab CI/CD or Jenkins for pipeline automation
  - Compliance scanning tools like OpenSCAP or Ansible's built-in security roles

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the POODLE fix playbook
  - Migration approach: Convert to an Ansible role with appropriate defaults for secure TLS configuration

- **SSH Hardening**: The SSH compliance tests check for root login restrictions
  - Migration approach: Create an Ansible role for SSH hardening that applies the same controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Compliance Testing**: Replacing Chef InSpec with equivalent Ansible testing capabilities
  - Mitigation: Use a combination of Ansible assert module and external tools like OpenSCAP
  
- **Deployment Automation**: Replacing Chef Automate/Infra Server deployment with equivalent Ansible solution
  - Mitigation: Create Ansible playbooks for AWX/Tower deployment or use containerized deployment with Docker/Kubernetes

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible directory) - Low risk, already in Ansible format
   - Refactor into proper Ansible roles with variables
   - Improve idempotency and error handling
   - Add documentation

2. **Compliance Tests** (chef-and-ansible/tests directory) - Medium complexity
   - Convert InSpec tests to Ansible assert statements or Molecule tests
   - Ensure all compliance checks are preserved
   - Document mapping between InSpec and Ansible tests

3. **Deployment Scripts** (setup-automate directory) - High complexity
   - Create Ansible playbooks for deploying management infrastructure
   - Replace Chef Automate/Infra Server with Ansible AWX/Tower or other solutions
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation
2. The target environment is Ubuntu 20.04 running on Vagrant VMs
3. The security compliance requirements include HTTPS configuration and SSH hardening
4. The Chef Automate and Chef Infra Server deployment scripts are used for setting up a management infrastructure
5. No complex Chef cookbooks or recipes are present that would require significant refactoring
6. The migration will preserve all existing functionality while moving to Ansible-native solutions
7. The existing Ansible playbooks can be largely preserved with minor improvements
8. The compliance testing requirements will remain the same after migration