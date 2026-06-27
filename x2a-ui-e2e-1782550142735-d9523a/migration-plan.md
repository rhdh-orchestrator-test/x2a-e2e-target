# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks designed to demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be migrated to Ansible playbooks.

The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity due to the limited scope of Chef InSpec tests and deployment scripts.

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
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing the web server. Can be preserved as-is or included as a template in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - For compliance testing: Use ansible-lint for static analysis
  - For runtime verification: Use Ansible assert module or Molecule for testing
  - For complex compliance needs: Consider integrating with OpenSCAP or using ansible.posix.mount module

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain proper certificate generation and management

- **SSH Security**: The SSH root login check must be preserved
  - Convert the InSpec control to an Ansible task that checks and enforces this setting
  - Consider using ansible.posix.sshd_config module for managing SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts need to be moved to Ansible Vault
  - Count: 2 credential sets (username/password) in deployment scripts

### Technical Challenges

- **InSpec to Ansible Conversion**: Converting InSpec tests to Ansible assertions requires careful mapping of test logic
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules
  - Use Ansible's assert module combined with command/shell modules to replicate InSpec functionality

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible requires understanding of Chef Automate's installation requirements
  - Mitigation: Create an Ansible role that implements the same system configuration and installation steps
  - Use Ansible's uri module to download Chef Automate CLI instead of curl

### Migration Order

1. **website_https.yml and poodle_fix.yml**: Already in Ansible format, no migration needed
2. **Chef InSpec tests**: Convert to Ansible assertions or Molecule tests
   - website_https_verify.rb: Convert to Ansible tasks using uri and assert modules
   - ssh_profile.rb: Convert to Ansible tasks using ansible.posix.sshd_config and assert modules
3. **Deployment scripts**: Convert to Ansible playbooks
   - deploy-automate.sh: Create Ansible role for Chef Automate deployment
   - deploy-chef-server.sh: Create Ansible role for Chef Infra Server deployment
4. **Testing framework**: Replace Test Kitchen with Molecule

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't need modification beyond potential security improvements.
2. The Chef InSpec tests are currently used for validation after Ansible playbook execution, and this validation is still required.
3. The deployment scripts are used for setting up Chef infrastructure, which may not be needed if fully migrating to Ansible.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. There are no external dependencies or integrations not visible in the provided repository.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure alternatives in the Ansible implementation.