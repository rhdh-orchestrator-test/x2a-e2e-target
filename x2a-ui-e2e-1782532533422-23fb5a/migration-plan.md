# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks designed to demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single engineer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL/TLS protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used for testing web server functionality. Can be preserved as-is.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for testing Ansible roles and playbooks
  - Option 2: Ansible Assert module for basic validation within playbooks
  - Option 3: Integration with other testing frameworks like Serverspec or Testinfra

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that accomplish the same server setup

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook that disables SSLv3 and enables only TLSv1.2.
- **SSH Security**: The SSH root login compliance check must be preserved in the Ansible testing framework.
- **Self-signed Certificates**: The generation and configuration of self-signed certificates should be maintained in the migrated solution.
- **Vault/secrets management**:
  - Hardcoded credentials in the Chef Automate/Infra Server deployment scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets (username/password) in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions will require careful mapping of InSpec resources to Ansible modules or external testing frameworks.
  - Mitigation: Use Ansible's assert module for basic tests and consider Molecule for more complex testing scenarios.

- **Test Kitchen to Molecule**: Transitioning from Test Kitchen to Molecule will require reconfiguring test environments and execution workflows.
  - Mitigation: Molecule provides similar functionality to Test Kitchen and can be configured to use Vagrant as a driver.

- **Chef Automate/Infra Server Deployment**: Converting the deployment scripts to Ansible playbooks will require understanding the Chef Automate/Infra Server installation process.
  - Mitigation: Break down the script into discrete tasks and map each to appropriate Ansible modules.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These can remain largely unchanged as they are already in Ansible format.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert these to Ansible-native testing solutions.
3. **Test Kitchen Configuration** (kitchen.yml): Replace with Molecule configuration.
4. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible playbooks.

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and do not need significant modifications.
2. The target environment will continue to be Ubuntu 20.04 as specified in the kitchen.yml file.
3. Vagrant will continue to be used for local development and testing.
4. The repository is primarily for demonstration purposes as indicated by the README.md, which mentions these are examples companion to a white paper.
5. No external dependencies or complex infrastructure beyond what is explicitly defined in the repository.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure alternatives in the migrated solution.
7. The Chef InSpec tests are currently being used for compliance validation and their functionality needs to be preserved in the migrated solution.