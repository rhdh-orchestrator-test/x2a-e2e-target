# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting the existing Ansible playbooks to a more structured Ansible format and migrating the Chef InSpec tests to Ansible-compatible testing frameworks. The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3, enables TLSv1.2 only

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration will require converting to Ansible-native testing frameworks.
- `index.html`: Simple HTML file used as a test page for the web server.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks like Molecule with Testinfra or Ansible's built-in assert module
- **Test Kitchen**: Replace with Molecule for Ansible role testing
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source alternatives like AWX

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL/TLS. Ensure proper TLS configuration is maintained during migration.
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented in the existing playbooks.

- **SSH Security**: The InSpec tests verify SSH security configurations.
  - Migration approach: Convert InSpec tests to Ansible assert tasks or Molecule with Testinfra.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation: Use Molecule with Testinfra which provides similar functionality to InSpec.

- **Chef Automate/Infra Server Deployment**: Converting Chef server deployment scripts to Ansible.
  - Mitigation: Create Ansible roles for deploying alternative infrastructure management tools.

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - Refactor into proper Ansible role structure
   - Add documentation

2. **poodle_fix.yml** (low risk, already Ansible)
   - Refactor into proper Ansible role structure
   - Combine with website_https role as an optional feature

3. **InSpec Tests** (moderate complexity)
   - Convert to Molecule with Testinfra or Ansible assert tasks
   - Ensure all compliance checks are maintained

4. **Chef Deployment Scripts** (high complexity)
   - Convert to Ansible roles for deploying alternative infrastructure management tools
   - Implement secure credential handling with Ansible Vault

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
2. The migration will replace Chef InSpec with Ansible-compatible testing frameworks.
3. The Chef Automate and Chef Infra Server deployment will be replaced with Ansible Automation Platform or open-source alternatives.
4. The existing Ansible playbooks will be refactored into proper Ansible roles following best practices.
5. The security requirements implemented in the InSpec tests will need to be maintained in the new testing framework.
6. The self-signed SSL certificates approach will be maintained rather than implementing Let's Encrypt or other certificate authorities.
7. The hardcoded credentials in the deployment scripts will be replaced with secure credential management.