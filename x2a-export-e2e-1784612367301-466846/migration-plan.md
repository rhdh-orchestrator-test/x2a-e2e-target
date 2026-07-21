# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment with both Chef and Ansible components. The primary content consists of Ansible playbooks for configuring web servers with HTTPS support, Chef InSpec tests for compliance verification, and shell scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, with most components already in Ansible format. The estimated timeline for complete migration is 1-2 weeks, with low complexity for the playbook components and moderate complexity for the Chef server deployment scripts.

## Module Migration Plan

This repository contains a mix of Ansible playbooks, Chef InSpec tests, and Chef server deployment scripts that need individual migration planning:

### MODULE INVENTORY

After thorough examination of the repository using file_search for patterns "**/manifests/init.pp", "**/recipes/default.rb", and "**/*.psd1", no Puppet modules, Chef cookbooks, or PowerShell modules were found. The repository contains the following components:

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses SSL POODLE vulnerability by disabling older SSL protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration
- `tests/ssh_profile.rb`: InSpec compliance profile for SSH security settings

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Keep InSpec tests but integrate with Ansible using ansible_local provisioner
  - Option 3: Convert InSpec tests to equivalent Ansible assert tasks

- **Test Kitchen (latest)**: Replace with:
  - Ansible Molecule for testing infrastructure
  - Or continue using Test Kitchen with the ansible_playbook provisioner

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for orchestration and control
  - Ansible Content Collections for role and module management
  - GitLab/GitHub for code repository and CI/CD

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL certificate generation and configuration
  - Migration approach: Preserve the existing OpenSSL tasks in the Ansible playbook
  - Consider using Ansible Vault for storing sensitive information

- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Convert InSpec tests to Ansible assert tasks or Ansible Molecule verify phase

- **Credentials in Scripts**: The Chef server deployment scripts contain hardcoded credentials
  - Migration approach: Replace with Ansible Vault for secure credential storage
  - Document the count and type of credentials detected per module:
    - deploy-automate.sh: 3 credentials (username, password, email)
    - deploy-chef-server.sh: 3 credentials (username, password, email)

### Technical Challenges

- **Chef InSpec Tests**: Converting InSpec tests to Ansible-native testing
  - Mitigation: Use Ansible assert modules or consider keeping InSpec as a testing tool even with Ansible

- **Chef Server Deployment**: Replacing Chef Server functionality with Ansible equivalents
  - Mitigation: Map Chef Server features to AWX/Ansible Tower and document the differences

- **Self-signed Certificates**: Ensuring proper certificate management in Ansible
  - Mitigation: Use the existing Ansible OpenSSL modules as already implemented

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (low risk, already in Ansible format)
   - Review and optimize existing Ansible code
   - Add documentation and comments

2. **InSpec Tests** (moderate complexity)
   - Convert to Ansible assert tasks or Molecule tests
   - Ensure compliance checks are maintained

3. **Chef Server Deployment Scripts** (high complexity)
   - Convert to Ansible roles for AWX/Tower deployment
   - Implement secure credential management

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, based on the README indicating these are examples for a white paper.

2. The Chef InSpec tests are used for compliance verification of infrastructure that may be managed by either Chef or Ansible.

3. The deployment scripts are intended for setting up a Chef environment, which would be replaced entirely by an Ansible-based solution.

4. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration.

5. The current implementation uses self-signed certificates for SSL, which would be maintained in the Ansible migration.

6. There is no complex data structure or external data sources that would require special handling during migration.

7. The repository does not contain actual Chef cookbooks or recipes that would need direct conversion to Ansible roles.