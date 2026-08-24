# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration. The repository appears to be a demonstration or example repository rather than a production infrastructure codebase. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Migrating Chef Automate and Chef Server deployment scripts to Ansible playbooks

Given the limited scope and example nature of the repository, this migration is estimated to be low complexity and could be completed within 1-2 weeks by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests, Ansible playbooks, and Chef server deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance testing

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **deploy-automate**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **deploy-chef-server**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. This will need to be updated to use Ansible-native testing frameworks.
- `chef-and-ansible/index.html`: Simple HTML file used for testing the web server configuration.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks such as:
  - Molecule for Ansible role testing
  - ansible-lint for static code analysis
  - testinfra for infrastructure testing (Python-based alternative to InSpec)
  - ansible-test for Ansible collections testing

- **Test Kitchen**: Replace with Molecule for testing Ansible roles and playbooks

- **Chef Automate/Server**: Replace with Ansible Automation Platform or open-source alternatives like:
  - AWX (open-source version of Ansible Tower)
  - Semaphore (lightweight alternative)
  - GitLab CI/CD with Ansible

### Security Considerations

- **SSL Configuration**: The migration must maintain the same level of security for SSL/TLS configurations:
  - Ensure the POODLE vulnerability fix (disabling SSLv3) is maintained
  - Preserve the TLSv1.2 requirement
  - Migrate the self-signed certificate generation process

- **SSH Security**: Maintain the SSH root login restriction as verified by the InSpec test

- **Credentials Management**: 
  - The Chef server deployment scripts contain hardcoded credentials that should be moved to Ansible Vault
  - Identified credentials: 1 user password in each deployment script

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec tests to an Ansible-compatible testing framework will require understanding the test assertions and recreating them in the new framework
  - Mitigation: Use testinfra which has a similar syntax to InSpec and supports Python-based testing

- **Certificate Management**: The current solution uses Ansible's openssl modules for certificate generation
  - Mitigation: These can be directly reused in the consolidated Ansible solution

### Migration Order

1. **website_https.yml** (Priority 1): Already an Ansible playbook, just needs review and potential refactoring
2. **poodle_fix.yml** (Priority 1): Already an Ansible playbook, just needs review and potential refactoring
3. **Chef Server Deployment Scripts** (Priority 2): Convert bash scripts to Ansible playbooks with proper variable management
4. **InSpec Tests** (Priority 3): Convert to testinfra or another Ansible-compatible testing framework

### Assumptions

1. The repository is primarily for demonstration purposes and not a production environment
2. The InSpec tests are used for validation only and not for continuous compliance monitoring
3. There is no complex integration with other Chef components beyond what's visible in the repository
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. The self-signed certificates are acceptable for the use case and don't need to be replaced with CA-signed certificates
6. The hardcoded credentials in the deployment scripts are example values and not actual production credentials