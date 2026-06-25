# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

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
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing the web server. Can be directly used in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Use Ansible Molecule with Goss for infrastructure testing
  - Option 3: Maintain InSpec as a separate testing tool but invoke from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Server**: Replace with Ansible Automation Platform or other Ansible-compatible CI/CD and compliance solutions

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL configuration is maintained in the migrated Ansible playbooks.
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented

- **SSH Security**: The InSpec tests verify SSH security configurations. Ensure these checks are maintained in the migrated testing framework.
  - Migration approach: Convert InSpec tests to Ansible assert tasks or Molecule tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Self-signed certificates generated in the playbook
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks may require learning new testing approaches.
  - Mitigation: Use Molecule with Testinfra which has a similar syntax to InSpec

- **Compliance Reporting**: If compliance reporting is a key feature, ensure the replacement solution provides adequate reporting capabilities.
  - Mitigation: Consider using Ansible Automation Platform with built-in compliance reporting

### Migration Order

1. Ansible Playbooks (website_https.yml, poodle_fix.yml) - Low risk as they are already in Ansible format
2. Testing Framework (Convert InSpec tests to Molecule/Testinfra) - Moderate complexity
3. Deployment Scripts (Convert bash scripts to Ansible roles) - Moderate complexity

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments, based on the README content.
2. The InSpec tests are used for compliance verification of infrastructure provisioned by Ansible.
3. The bash scripts for Chef Automate/Server deployment are separate from the main Ansible+InSpec workflow.
4. There are no external dependencies or modules not visible in the repository structure.
5. The target environment is Ubuntu 20.04 running on Vagrant VMs.
6. No complex state management or data persistence requirements exist beyond what's visible in the playbooks.
7. No external inventory or variable files are being used for the Ansible playbooks.
8. The hardcoded credentials in the deployment scripts are for demonstration purposes only.