# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The repository also includes shell scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Replacing Chef Automate/Infra Server deployment scripts with Ansible equivalents

Given the limited scope and the fact that part of the infrastructure is already using Ansible, this migration is estimated to be of **low complexity** with an estimated timeline of **1-2 weeks**.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables only TLSv1.2

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Compliance testing for SSH configuration

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS is properly configured
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Tests port 443 listening, HTTPS response, and SSL/TLS protocol configuration

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Will need to be updated to use Ansible-native testing.
- `chef-and-ansible/index.html`: Simple HTML file used as a test page for the web server.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Use Molecule for more comprehensive testing
  - Option 3: Continue using InSpec but integrate it with Ansible using the `inspec` Ansible module

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible-specific CI/CD pipeline

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: AWX/Ansible Tower for enterprise automation
  - Option 2: Ansible Automation Platform

### Security Considerations

- **SSL/TLS Configuration**: The current implementation enforces TLSv1.2 and disables vulnerable protocols. This security practice should be maintained in the Ansible migration.
  - Migration approach: Use the same configuration parameters in the Ansible Apache modules

- **SSH Security**: The InSpec test verifies that SSH root login is disabled.
  - Migration approach: Create an equivalent Ansible playbook that both configures and verifies this setting

- **Self-signed Certificates**: The current implementation generates self-signed certificates.
  - Migration approach: Use Ansible's `openssl_*` modules to generate certificates or consider integrating with Let's Encrypt for production environments

- **Vault/secrets management**:
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` (username, password)
  - Migration approach: Use Ansible Vault to securely store credentials

### Technical Challenges

- **Testing Framework Transition**: Moving from InSpec to an Ansible-native testing solution.
  - Mitigation: Create equivalent tests using Ansible's assert module or Molecule

- **Maintaining Compliance Validation**: The current setup uses InSpec for compliance validation.
  - Mitigation: Ensure the new Ansible solution provides equivalent compliance validation capabilities

- **Chef Automate Functionality**: Replacing Chef Automate's compliance and reporting features.
  - Mitigation: Evaluate if AWX/Ansible Tower provides sufficient compliance reporting or if additional tools are needed

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format; just need review and potential optimization
2. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb): Convert to Ansible-native testing
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Create equivalent Ansible playbooks for infrastructure deployment
4. **Test Kitchen Configuration**: Replace with Molecule or other Ansible-native testing framework

### Assumptions

1. The primary purpose of this repository is to demonstrate compliance automation using Chef InSpec alongside Ansible, as indicated in the README.
2. The target environment is Ubuntu 20.04 running on Vagrant VMs.
3. The security configurations (SSL/TLS, SSH) are critical and must be maintained in the migration.
4. There are no external dependencies or integrations beyond what's visible in the repository.
5. The Chef Automate and Chef Infra Server deployment scripts are used for setting up test environments and not production systems.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only.
7. The migration will maintain the same level of compliance validation currently provided by InSpec.