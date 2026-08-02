# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks
3. Adapting Chef InSpec tests to work with Ansible or replacing them with Ansible-native testing solutions

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository primarily contains deployment scripts and simple Ansible playbooks with InSpec tests

## Module Migration Plan

This repository contains a mix of Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to address POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `chef-and-ansible/index.html`: Sample HTML content for the website

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Keep InSpec but call it from Ansible using the `command` module

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role/playbook testing
  - Option 2: Simple Vagrant-based testing scripts

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: AWX/Ansible Tower for enterprise features
  - Option 2: Simple Ansible control node with Git repositories

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL/TLS protocols are maintained in the migrated solution.
  - Migration approach: Preserve the existing SSL configuration in the Ansible playbooks

- **SSH Hardening**: The InSpec tests check for SSH root login disablement.
  - Migration approach: Create an Ansible task to ensure SSH root login is disabled and add appropriate testing

- **Credentials in Scripts**: The Chef deployment scripts contain hardcoded credentials.
  - Migration approach: Use Ansible Vault to secure credentials in the migrated playbooks

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password, email)
  - Count: 2 scripts with 5 credential-related variables each

### Technical Challenges

- **Challenge 1: InSpec Test Conversion**
  - Description: Converting InSpec tests to Ansible-native testing
  - Mitigation strategy: Use Ansible's assert module for basic tests, or consider keeping InSpec and calling it from Ansible

- **Challenge 2: Chef Automate/Infra Server Replacement**
  - Description: Determining the appropriate Ansible-based replacement for Chef Automate/Infra Server
  - Mitigation strategy: Evaluate AWX/Ansible Tower or simpler Git-based workflow depending on requirements

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/*.yml) - Low risk as they're already in Ansible format
   - Preserve existing playbooks
   - Update any deprecated syntax or modules
   - Ensure idempotence

2. **Chef Deployment Scripts** (setup-automate/*.sh) - Medium complexity
   - Convert bash scripts to Ansible playbooks
   - Secure credentials using Ansible Vault
   - Test deployment on target platforms

3. **Testing Framework** (chef-and-ansible/tests/*.rb) - Medium complexity
   - Convert InSpec tests to Ansible-native testing or
   - Create wrapper playbooks to call InSpec tests

### Assumptions

1. The existing Ansible playbooks are functional and follow best practices
2. The Chef deployment scripts are used for initial setup only and not for ongoing configuration management
3. There are no external dependencies or integrations not visible in the repository
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The hardcoded credentials in the deployment scripts are examples and not production credentials
6. The InSpec tests are essential and their functionality needs to be preserved
7. There is no requirement to maintain backward compatibility with Chef Automate/Infra Server