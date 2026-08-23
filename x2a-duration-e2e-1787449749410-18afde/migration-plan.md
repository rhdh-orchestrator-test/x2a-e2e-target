# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec profiles that are used for compliance testing and automation. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. Additionally, there are setup scripts for Chef Automate and Chef Infra Server deployment.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec profiles to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible playbooks (which are already in Ansible format) and moderate complexity for converting the InSpec profiles to Ansible-compatible testing frameworks.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec profiles that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **website_https_verify**:
    - Description: Chef InSpec profile for verifying HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile for verifying SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

- **automate_deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef_server_deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used in the website deployment. Migration consideration: Can be directly used in Ansible.

## Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Use Molecule for more comprehensive testing
  - Option 3: Integrate with other testing frameworks like Serverspec or TestInfra

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with Ansible automation platform (AAP) or other Ansible management solutions:
  - AWX (open source)
  - Ansible Automation Platform (commercial)

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL configuration is maintained during migration.
  - Migration approach: Preserve the SSL configuration logic in the Ansible playbooks.

- **SSH Security**: The InSpec profile checks for SSH root login configuration. Ensure this security check is maintained.
  - Migration approach: Convert the InSpec check to an Ansible assert or use Ansible-lint.

- **Self-signed Certificates**: The playbook generates self-signed certificates. Consider implementing proper certificate management.
  - Migration approach: Use Ansible's `openssl_*` modules (already in use) or integrate with a certificate management system.

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation strategy: Map InSpec resources to equivalent Ansible modules or TestInfra checks.

- **Chef Server Deployment**: Replacing Chef Server deployment with Ansible management.
  - Mitigation strategy: Document the transition from Chef Server to Ansible management, including inventory management and node communication.

### Migration Order

1. Ansible Playbooks (website_https.yml, poodle_fix.yml) - Low risk as they're already in Ansible format
2. InSpec Tests (website_https_verify.rb, ssh_profile.rb) - Convert to Ansible-compatible testing
3. Chef Deployment Scripts (deploy-automate.sh, deploy-chef-server.sh) - Replace with Ansible roles for management platform setup

### Assumptions

1. The primary goal is to consolidate on Ansible as the sole automation tool, eliminating Chef components.
2. The InSpec tests need to be converted to equivalent functionality in an Ansible-compatible testing framework.
3. The deployment scripts for Chef Automate and Chef Infra Server will be replaced with equivalent Ansible roles or playbooks for setting up an Ansible management environment.
4. The current Test Kitchen setup is used for development and testing, and will need an equivalent in the Ansible ecosystem.
5. The hardcoded credentials in the deployment scripts will be replaced with a more secure approach using Ansible Vault.
6. The repository is primarily for demonstration purposes, as indicated by the README, and may not represent a production environment.
7. The target environment will continue to be Ubuntu 20.04 or compatible systems.
8. The SSL and security configurations are important aspects that must be preserved in the migration.