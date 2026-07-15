# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible playbooks (which are already in Ansible format) and moderate complexity for converting the InSpec tests to Ansible-compatible testing frameworks.

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
    - Key Features: Disables SSLv3 and enables TLSv1.2 only

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (SRG-OS-000112)

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef server installation, user and organization creation

- **automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing web server functionality. Can be directly used in Ansible without modification.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in assert module for basic testing
  - Option 2: Use Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen with Vagrant**: Replace with Molecule for testing Ansible roles and playbooks

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower for enterprise automation platform

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL/TLS settings are maintained during migration.
  - Migration approach: Maintain the same SSL configuration parameters but use Ansible's native modules

- **SSH Security**: The InSpec tests verify SSH security configurations.
  - Migration approach: Convert InSpec tests to Ansible assert statements or Molecule tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation: Use Ansible's assert module for simple tests, and consider Molecule for more complex testing scenarios.

- **Chef Server Deployment**: Replacing Chef server deployment scripts with Ansible AWX/Tower deployment.
  - Mitigation: Create Ansible playbooks to deploy AWX/Tower with similar user/organization structure.

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (low risk, already in Ansible format)
2. **InSpec tests** (moderate complexity, requires conversion to Ansible testing framework)
3. **Chef deployment scripts** (high complexity, requires replacement with AWX/Tower deployment)

### Assumptions

1. The primary goal is to move all functionality to pure Ansible without any Chef components.
2. The InSpec tests need to be converted to equivalent functionality in an Ansible-compatible testing framework.
3. The deployment scripts for Chef Automate and Chef Infra Server will be replaced with equivalent Ansible AWX/Tower deployment.
4. The current setup uses Vagrant for local development/testing, which may continue to be used with Ansible.
5. No external dependencies or integrations beyond what's visible in the repository.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be properly secured in the migrated solution.
7. The Apache web server configuration requirements will remain the same in the migrated solution.