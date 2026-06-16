# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef server deployment scripts that need to be converted to Ansible playbooks. The estimated timeline for this migration is 1-2 weeks given the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing web server functionality. No migration needed as it's a static asset.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Consider maintaining InSpec as a separate tool called from Ansible

- **Test Kitchen (latest)**: Replace with Molecule for Ansible role testing

- **Chef Automate/Chef Server**: Replace deployment scripts with Ansible roles for equivalent functionality or migrate to alternative compliance platforms like:
  - AWX/Ansible Tower
  - Ansible Automation Platform

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Approach: Maintain the same configuration parameters in the Ansible tasks

- **SSH Security**: The SSH root login compliance check needs to be converted to an Ansible-compatible test
  - Approach: Create an equivalent check using Ansible assert or Molecule verify

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup scripts (username, password)
  - Migration approach: Use Ansible Vault to secure these credentials

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks
  - Mitigation: Use Ansible's assert module for simple tests, or integrate with Molecule for more complex testing scenarios
  - Consider using ansible-lint for static analysis of playbooks

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible
  - Mitigation: Create Ansible roles that perform equivalent setup steps, or consider if Chef server is still needed after migration

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they're already in Ansible format, may need minor updates for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Convert to Ansible-compatible testing framework
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - Convert to Ansible roles or evaluate if they're still needed

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as indicated in the README.md.
2. The existing Ansible playbooks are functioning correctly and follow best practices.
3. The Chef InSpec tests are currently being used to validate the Ansible playbook outcomes.
4. The deployment scripts for Chef Automate and Chef Server may not be needed if the migration is fully to Ansible.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only and would be replaced with secure alternatives in production.
6. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.
7. There are no external dependencies beyond what's explicitly mentioned in the repository.