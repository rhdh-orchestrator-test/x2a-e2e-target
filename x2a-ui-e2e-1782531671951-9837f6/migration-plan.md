# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests that demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting the InSpec tests to Ansible-compatible testing frameworks while maintaining the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used for testing web server functionality

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - **Option 1**: Migrate to Ansible Molecule with Testinfra for testing
  - **Option 2**: Use the ansible.builtin.assert module for simple tests
  - **Option 3**: Implement Ansible Molecule with Goss for more complex testing

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Approach: Ensure the SSL protocol restrictions are preserved in the migrated Ansible roles
  
- **SSH Security**: The SSH root login restriction test must be maintained
  - Approach: Convert the InSpec control to an equivalent Ansible assertion or Molecule test

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated during deployment, no pre-existing secrets detected
  - Count of credentials per module:
    - chef-automate-deployment: 3 (username, password, email)
    - chef-server-deployment: 3 (username, password, email)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to equivalent Ansible testing frameworks
  - Mitigation: Use Molecule with Testinfra or Goss to achieve similar testing capabilities
  
- **Chef Automate Deployment**: Converting the Chef Automate deployment script to Ansible
  - Mitigation: Research Ansible modules for managing Chef installations or use the command/shell module with idempotency checks

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, just need to be restructured as roles
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Medium complexity, convert to Ansible Molecule tests
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity, convert to Ansible roles and playbooks

### Assumptions

1. The existing Ansible playbooks are functional and don't require significant modifications beyond restructuring
2. The InSpec tests are currently used for validation and compliance checking, and this functionality needs to be preserved
3. The deployment scripts are used for setting up Chef infrastructure, which may be replaced entirely with Ansible
4. No external data sources or complex integrations are present in the current implementation
5. The target environment will continue to be Ubuntu 20.04 or compatible systems
6. The migration does not need to maintain backward compatibility with Chef InSpec
7. The current implementation is for demonstration purposes and may not include all production-level features
8. No complex state management or database interactions are present in the current implementation