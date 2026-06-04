# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests. The estimated timeline for migration would be 1-2 weeks, with low complexity since most of the content is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
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
    - Description: Chef InSpec test that verifies SSH root login is disabled (security compliance check)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance with specific tags (STIG, CCI)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider migrating to ansible-test

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL configuration is maintained in the migrated Ansible playbooks.
  - Migration approach: Preserve the SSL configuration parameters in the Ansible tasks

- **SSH Security**: The InSpec tests verify SSH root login is disabled.
  - Migration approach: Create equivalent Ansible assert tasks to verify SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or other testing frameworks.
  - Mitigation: Use Ansible's assert module for basic tests and consider integrating with tools like Molecule for more complex testing scenarios.

- **Chef Automate Deployment**: The bash scripts for Chef Automate and Chef Infra Server deployment need to be converted to Ansible playbooks.
  - Mitigation: Create Ansible roles for Chef server deployment if still needed, or replace with Ansible AWX/Tower for similar functionality.

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (low risk, already in Ansible format)
2. **InSpec tests** (moderate complexity, requires conversion to Ansible testing framework)
3. **Chef deployment scripts** (high complexity, requires complete rewrite as Ansible playbooks or potential replacement with Ansible AWX/Tower)

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance testing.
2. The Chef deployment scripts may not be needed if the organization is fully migrating to Ansible (including replacing Chef Automate with Ansible AWX/Tower).
3. The target environment is Ubuntu 20.04 running on Vagrant VMs.
4. There are no external dependencies or complex integrations beyond what is visible in the repository.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in production.
6. The organization wants to maintain the same level of compliance testing currently provided by InSpec.