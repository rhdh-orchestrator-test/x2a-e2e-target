# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing profiles and Ansible playbooks that are used together to demonstrate compliance automation. The repository also includes setup scripts for Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing primarily on:

1. Migrating Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating the existing Ansible playbooks
3. Replacing Chef Automate and Chef Infra Server setup scripts with Ansible equivalents

Given the limited scope and the fact that part of the infrastructure is already using Ansible, this migration is estimated to be of **low complexity** with an estimated timeline of **1-2 weeks**.

## Module Migration Plan

This repository contains a combination of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to address POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

- **chef-automate-setup**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-setup**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. This file coordinates the testing of Ansible playbooks with InSpec tests.
- `index.html`: Simple HTML file used in the website deployment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider maintaining InSpec as a separate testing tool that can be called from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role and playbook testing
  - Or continue using Test Kitchen with the Ansible provisioner if preferred

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI, job scheduling, and inventory management
  - Git repositories for playbook and role storage
  - Consider using Ansible Collections for organizing related content

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure the migration maintains:
  - Proper TLS protocol settings (disabling SSL3, enabling TLS1.2)
  - Self-signed certificate generation
  - Secure virtual host configuration

- **SSH Security**: The InSpec tests verify SSH security configurations. Ensure:
  - SSH root login remains disabled
  - Compliance with security standards is maintained (STIG requirements)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks may require:
  - Learning new testing syntax and approaches
  - Ensuring equivalent coverage of security checks
  - Maintaining compliance reporting capabilities

- **Chef Automate Functionality**: If using Chef Automate for compliance reporting and visualization:
  - Identify alternative solutions in the Ansible ecosystem (AWX/Tower)
  - Consider how to replicate compliance dashboards and reporting

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, may only need refinement and organization into roles
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-compatible testing frameworks
3. **Setup Scripts** (deploy-automate.sh, deploy-chef-server.sh): Create equivalent Ansible playbooks for infrastructure setup

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment.
2. The existing Ansible playbooks are functional and follow best practices.
3. There are no external dependencies or integrations not visible in the repository.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The migration will maintain the same level of security compliance checking.
6. The hardcoded credentials in the setup scripts are for demonstration purposes only and will be properly secured in the migrated solution.
7. The Test Kitchen configuration is used for development and testing, not for production deployments.