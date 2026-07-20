# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment of Chef and Ansible components that need to be migrated to a pure Ansible solution. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks with Chef InSpec testing components
3. Example configurations for web server deployment with SSL/TLS security

The migration complexity is relatively low as most of the Ansible components are already in place and the Chef components are primarily deployment scripts rather than complex cookbooks. The estimated timeline for migration is 1-2 weeks, with the main effort focused on replacing the Chef InSpec testing with Ansible-native testing solutions and converting the Chef server deployment scripts to Ansible playbooks.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration example of Ansible playbooks with Chef InSpec for compliance testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS website deployment, SSL/TLS configuration, compliance testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef server setup, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should replace this with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure web server. Can be retained with minor modifications.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be retained with minor modifications.
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test for HTTPS website. Should be migrated to Ansible-native testing (Molecule with Testinfra or Ansible assertions).
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec test for SSH security compliance. Should be migrated to Ansible-native testing.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Should be converted to an Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Should be converted to an Ansible playbook.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package references)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Use Ansible assertions and built-in modules for compliance checks
  - Option 3: Consider Ansible Lint for static analysis of playbooks

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration and management
  - Ansible Collections for configuration management
  - GitLab CI/GitHub Actions for CI/CD pipelines

### Security Considerations

- **SSL/TLS Configuration**: The current implementation configures Apache with TLS 1.2 and disables older protocols. Migration should maintain or enhance this security posture.
  - Migration approach: Preserve the SSL/TLS hardening in the Ansible playbooks, consider updating to include TLS 1.3 support.

- **SSH Hardening**: The InSpec profile checks for secure SSH configuration (disabled root login).
  - Migration approach: Implement equivalent checks using Ansible's assert module or Molecule with Testinfra.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificate generation should use Ansible Vault for storing private keys
  - Count of credentials detected: 3 (username, password, SSL private key)

### Technical Challenges

- **Testing Framework Migration**: Moving from Chef InSpec to Ansible-native testing solutions.
  - Mitigation: Create equivalent tests using Ansible's built-in modules or Molecule with Testinfra. Map InSpec resources to equivalent Ansible modules.

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible playbooks.
  - Mitigation: Create Ansible roles for server setup, user management, and organization creation. Use Ansible's package management modules to install required packages.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Retain `website_https.yml` and `poodle_fix.yml` with minor modifications
   - Update handlers to use fully qualified module names

2. **Testing Framework** (Moderate complexity)
   - Create Molecule testing structure to replace Test Kitchen
   - Convert InSpec tests to Ansible assertions or Testinfra

3. **Chef Server Deployment Scripts** (High complexity)
   - Create Ansible playbooks to replace the bash scripts for Chef server deployment
   - Implement Ansible Vault for credential management

### Assumptions

1. The primary purpose of this repository is for demonstration and examples, not production deployment.
2. The Chef InSpec tests are used for compliance verification of infrastructure deployed by Ansible.
3. The Chef server deployment scripts are used for setting up a Chef environment, which will be replaced by Ansible Tower/AWX.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. There are no external dependencies or integrations beyond what is visible in the repository.
6. The migration will maintain the same level of security compliance and testing coverage.
7. The hardcoded credentials in the scripts are for demonstration purposes and will be properly secured in the migrated solution.