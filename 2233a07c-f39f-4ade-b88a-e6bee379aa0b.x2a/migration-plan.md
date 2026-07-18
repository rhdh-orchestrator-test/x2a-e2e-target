# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec with Ansible for compliance automation. The migration scope is relatively small, with the primary components being:

1. Ansible playbooks for configuring HTTPS websites
2. Chef InSpec tests for compliance verification
3. Shell scripts for Chef Automate and Chef Infra Server deployment

The migration complexity is **LOW** as most components are already Ansible-based or are simple shell scripts. The estimated timeline for migration is **1-2 weeks**, primarily focused on standardizing the existing Ansible playbooks and converting the InSpec tests to Ansible-native testing frameworks.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **ansible-playbooks**:
    - Description: Ansible playbooks for configuring Apache with HTTPS and fixing SSL vulnerabilities
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration, SSL hardening

- **inspec-tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH hardening
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH root login testing

- **chef-deployment**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment example
- `chef-and-ansible/README.md`: Documentation files explaining the purpose of the examples
- `chef-and-ansible/website_https.yml`: Ansible playbook for HTTPS website configuration
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for SSL vulnerability remediation

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use ansible-test framework
  - Option 3: Maintain InSpec tests but integrate with Ansible using the ansible_inspec module

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing infrastructure
  - Or maintain Test Kitchen but use the kitchen-ansible plugin exclusively

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure SSL/TLS settings that need to be maintained:
  - Self-signed certificate generation
  - Disabling vulnerable protocols (SSLv3)
  - Enforcing TLSv1.2

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled
  - Migration should include equivalent Ansible tasks to enforce this security control
  - Consider using ansible-hardening role for comprehensive SSH hardening

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Recommend migrating to Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks
  - Mitigation: Use ansible.builtin.assert or ansible.builtin.fail modules to implement equivalent tests
  - Consider using community.general.assert module for more complex assertions

- **Chef Server Deployment**: The Chef server deployment scripts need to be replaced
  - Mitigation: Create Ansible roles for infrastructure management instead of Chef server

### Migration Order

1. **Ansible playbooks** (low risk, already Ansible)
   - Standardize according to Ansible best practices
   - Add proper documentation
   - Implement idempotency improvements
   - Merge website_https.yml and poodle_fix.yml into a comprehensive web server role

2. **InSpec tests** (moderate complexity)
   - Convert to Ansible-native testing with Molecule
   - Implement equivalent assertions

3. **Chef deployment scripts** (high complexity)
   - Replace with Ansible roles for infrastructure management
   - Implement secure credential handling with Ansible Vault

### Assumptions

1. The primary purpose of this repository is demonstration, not production deployment
2. The InSpec tests are essential and need equivalent functionality in the migrated solution
3. The Chef server deployment scripts are not the main focus and could be replaced with alternative infrastructure management approaches
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. Vagrant will continue to be used for local development and testing
6. The security requirements (SSL/TLS configuration, SSH hardening) must be maintained in the migrated solution