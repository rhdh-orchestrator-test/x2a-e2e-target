# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and infrastructure configuration. The migration scope is relatively small, focusing on:

1. Migrating Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks

Given the limited scope and the fact that part of the infrastructure is already using Ansible, this migration is estimated to be low complexity and could be completed within 1-2 weeks by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **deploy-automate**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **deploy-chef-server**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be updated to use Ansible-native testing frameworks.
- `chef-and-ansible/index.html`: Sample HTML file used for testing web server configuration. Can be reused in Ansible playbooks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-compatible testing frameworks such as:
  - Molecule for Ansible role testing
  - ansible-lint for static code analysis
  - testinfra for infrastructure testing (Python-based alternative to InSpec)

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration and job scheduling
  - Ansible Collections for role and module management
  - Git repositories for version control of playbooks

### Security Considerations

- **SSL Configuration**: The existing playbooks configure Apache with SSL. Migration should maintain or improve the security posture:
  - Ensure TLSv1.2 or higher is enforced (currently done in poodle_fix.yml)
  - Use modern cipher suites
  - Consider integrating with Let's Encrypt for certificate management instead of self-signed certificates

- **SSH Hardening**: The InSpec tests verify SSH security configurations. Migration should:
  - Implement equivalent SSH hardening in Ansible
  - Maintain compliance with security standards referenced in the InSpec tests (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts (username, password)
  - Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks may require learning new testing methodologies and syntax.
  - Mitigation: Use testinfra which has similar functionality to InSpec but integrates better with Ansible

- **Chef Server Deployment**: Replacing Chef Server deployment scripts with Ansible requires understanding of Chef Server architecture.
  - Mitigation: Create Ansible roles that replicate the functionality of the deployment scripts, focusing on idempotence

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format. Refactor to follow best practices and improve security.
2. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb): Convert to testinfra or other Ansible-compatible testing framework.
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Create Ansible playbooks to replace these bash scripts.

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production, as indicated by the README.md mentioning "examples" and "companion to a white paper".
2. The Chef InSpec tests are used for compliance validation of infrastructure that could be managed by either Chef or Ansible.
3. The deployment scripts are used for setting up Chef infrastructure, which will be replaced by Ansible Tower/AWX.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and not used in production environments.
5. The kitchen.yml configuration suggests that Test Kitchen is used to validate the Ansible playbooks using InSpec tests, indicating a hybrid approach to infrastructure testing.