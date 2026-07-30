# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests that are used together to deploy and validate secure web server configurations. The repository also includes scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing on:

1. Converting existing Ansible playbooks to follow modern Ansible best practices
2. Converting Chef InSpec tests to Ansible-native testing solutions
3. Replacing Chef Automate/Infra Server deployment scripts with Ansible automation

**Estimated Timeline**: 1-2 weeks for a single engineer, with the majority of time spent on converting InSpec tests to Ansible-native testing frameworks.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that validates SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, STIG compliance checks

- **automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Template for the Hello World website deployed by the Ansible playbook

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic validation
  - Option 2: Use Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - GitHub Actions or other CI/CD pipeline for automated testing

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for web UI and job scheduling
  - Git repositories for version control
  - CI/CD pipelines for automated testing and deployment

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the current playbooks:
  - Disable SSLv3 (POODLE vulnerability mitigation)
  - Enable only TLSv1.2 or higher
  - Generate proper self-signed certificates

- **SSH Hardening**: Maintain the SSH security controls:
  - Disable root login
  - Maintain STIG compliance requirements

- **Vault/secrets management**:
  - Current implementation has hardcoded credentials in the Chef Server deployment scripts
  - Migration should use Ansible Vault to secure:
    - User passwords in the Chef Server deployment scripts (currently hardcoded as 'password')
    - Any other sensitive information

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of InSpec resources to Ansible modules:
  - InSpec port checks → Ansible wait_for module
  - InSpec HTTP checks → Ansible uri module
  - InSpec SSL checks → Custom Ansible modules or external commands

- **Test Kitchen to Molecule**: Converting the testing framework will require:
  - Creating Molecule scenarios that match current Test Kitchen functionality
  - Ensuring idempotence testing is properly configured
  - Setting up proper test sequence (create, prepare, converge, verify, destroy)

- **Chef Server Deployment**: Converting the Chef Server deployment scripts to Ansible will require:
  - Understanding Chef Automate/Infra Server installation requirements
  - Creating idempotent Ansible tasks for installation and configuration
  - Properly handling user and organization creation

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml):
   - Low risk, already in Ansible format
   - Update to follow modern Ansible best practices
   - Convert to roles for better organization

2. **Testing Framework**:
   - Set up Molecule testing infrastructure
   - Create basic test scenarios

3. **InSpec Tests**:
   - Convert website_https_verify.rb to Ansible assertions or Molecule verifiers
   - Convert ssh_profile.rb to Ansible assertions or Molecule verifiers

4. **Chef Server Deployment**:
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The current Ansible playbooks are functional and correctly implement the desired state.
2. The InSpec tests accurately validate the security requirements.
3. The deployment scripts for Chef Automate/Infra Server are used for setting up testing or development environments, not production environments.
4. The migration will maintain the same level of security validation currently provided by InSpec.
5. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
6. The hardcoded credentials in the deployment scripts are not used in production environments.
7. There are no external dependencies or integrations not visible in the provided repository.