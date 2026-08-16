# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef Automate/Infra Server setup scripts. The primary migration focus will be on standardizing all infrastructure automation to Ansible. The repository appears to be a demonstration of using Chef InSpec for compliance testing with Ansible playbooks, along with scripts for setting up Chef infrastructure.

The migration scope is relatively small, with only a few Ansible playbooks and bash scripts to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as most of the content is already in Ansible format.

## Module Migration Plan

This repository contains Ansible playbooks and Chef setup scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS configuration, including self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-setup**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-setup**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `tests/website_https_verify.rb`: Chef InSpec test file for verifying HTTPS configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions like Molecule or maintain InSpec as a standalone testing tool
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing
- **Chef Automate/Infra Server**: Evaluate if these components are needed or can be replaced with Ansible Tower/AWX

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache, which needs careful migration to maintain security posture
- **Self-signed certificates**: The current implementation generates self-signed certificates, consider integrating with Let's Encrypt in the Ansible migration
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - SSL certificate and key management
  - Consider migrating to Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Testing**: The repository uses Chef InSpec for compliance testing with Ansible. Decide whether to:
  1. Keep InSpec as a standalone testing tool (simplest approach)
  2. Migrate to Ansible-native testing with Molecule and TestInfra (more consistent with Ansible ecosystem)

- **Chef Server Setup**: The bash scripts for Chef server setup need to be converted to Ansible roles if the functionality is still required

### Migration Order

1. **website_https.yml** (Priority 1): Already in Ansible format, just needs review and potential refactoring to follow best practices
2. **poodle_fix.yml** (Priority 1): Already in Ansible format, just needs review and potential refactoring
3. **InSpec Tests** (Priority 2): Decide on testing strategy and implement
4. **Chef Setup Scripts** (Priority 3): Convert to Ansible roles if the functionality is still required

### Assumptions

1. The primary goal is to standardize on Ansible and remove Chef dependencies where possible
2. The InSpec testing functionality is valuable and should be preserved in some form
3. The Chef Automate/Infra Server setup scripts may no longer be needed if fully migrating to Ansible
4. The repository is primarily for demonstration purposes rather than production use
5. No external dependencies or modules are referenced that would need to be included in the migration
6. The hardcoded credentials in the setup scripts are for demonstration purposes and would be replaced with secure alternatives in the migration
7. The Apache configuration and SSL setup in the Ansible playbooks are the core functionality that needs to be preserved