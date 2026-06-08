# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. There are also Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

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
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing. Migration consideration: Keep as-is or incorporate into Ansible templates.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Convert InSpec tests to Ansible assert tasks
  - Option 3: Maintain InSpec as a separate tool but call it from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or other Ansible-compatible compliance and automation tools

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL configuration is maintained in migrated Ansible roles.
  - Migration approach: Create dedicated Ansible role for Apache SSL configuration with proper defaults

- **SSH Security**: The InSpec tests verify SSH security configurations. Ensure these checks are maintained.
  - Migration approach: Convert InSpec SSH tests to Ansible assert tasks or Molecule tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Self-signed certificates generated in playbooks
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks may require learning new testing approaches.
  - Mitigation: Use Molecule with Testinfra which has similar syntax to InSpec, or maintain InSpec as a separate tool

- **Compliance Reporting**: If compliance reporting is a requirement, ensure the Ansible solution includes compliance reporting capabilities.
  - Mitigation: Consider using Ansible Automation Platform with built-in compliance capabilities or integrate with third-party compliance tools

### Migration Order

1. Ansible Playbooks (website_https.yml, poodle_fix.yml) - Already in Ansible format, just need to be converted to roles
2. Chef InSpec Tests (website_https_verify.rb, ssh_profile.rb) - Convert to Ansible testing framework
3. Chef Deployment Scripts (deploy-automate.sh, deploy-chef-server.sh) - Convert to Ansible playbooks

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used with Ansible for compliance testing.
2. The target environment is Ubuntu 20.04 running on Vagrant VMs.
3. There are no external dependencies beyond what's explicitly installed in the playbooks.
4. The deployment scripts are examples and not used in production environments.
5. No complex state management or data persistence is required.
6. The InSpec tests are used for compliance validation only and not for broader infrastructure testing.
7. There are no custom InSpec resources that would require special handling during migration.
8. The hardcoded credentials in the deployment scripts are for demonstration purposes only.