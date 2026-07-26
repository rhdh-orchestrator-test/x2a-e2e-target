# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and demonstration purposes. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks

Given the limited scope and the fact that part of the repository already uses Ansible, this migration is estimated to be of low complexity and could be completed within 1-2 weeks by a single engineer familiar with both Chef and Ansible technologies.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **deploy-automate**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **deploy-chef-server**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be updated to use Ansible-native testing frameworks.
- `chef-and-ansible/index.html`: Simple HTML file used for testing web server functionality. Can be reused as-is.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the Ansible provisioner (already in use)

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for enterprise automation platform
  - Or use ansible-runner and ansible-navigator for lightweight alternatives

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ is enforced (already addressed in poodle_fix.yml)
  - Consider adding more modern cipher suites
  - Add HSTS headers

- **SSH Hardening**: The InSpec test verifies SSH root login is disabled. Migration should:
  - Incorporate this check into Ansible-based testing
  - Consider adding an Ansible role for SSH hardening

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts (username, password)
  - Migration should use Ansible Vault for credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests requires understanding the compliance requirements and implementing equivalent checks.
  - Mitigation: Use Ansible's assert module with appropriate conditions that match the InSpec requirements.

- **Chef Automate Deployment**: The Chef Automate deployment script includes specific system configurations and Chef-specific commands.
  - Mitigation: Create an Ansible role that performs equivalent system configurations and uses the appropriate API calls or commands to set up the replacement automation platform.

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format. Simply review and optimize.
2. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb): Convert to Ansible-compatible testing framework.
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Create equivalent Ansible roles for deployment of the chosen automation platform.

### Assumptions

1. The repository is primarily for demonstration purposes rather than production use, based on the README content.
2. The InSpec tests are intended to validate compliance with security standards and verify functionality.
3. The deployment scripts are intended for setting up Chef infrastructure in lab environments.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. There are no external dependencies or integrations beyond what's visible in the repository.
6. The migration will replace Chef InSpec with an Ansible-compatible testing framework while maintaining the same compliance checks.
7. The Chef Automate and Infra Server deployment will be replaced with an equivalent Ansible automation platform deployment.