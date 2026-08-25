# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more standardized Ansible structure and migrating Chef InSpec tests to Ansible-compatible testing frameworks. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

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
    - Key Features: Apache SSL configuration hardening, service restart

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration and website availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Static HTML file for the website. No migration needed, can be used as-is in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Migrate InSpec tests to Ansible Molecule with testinfra or Goss
  - For compliance testing, consider using ansible-lint with custom rules or OpenSCAP integration

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure:
  - Convert kitchen.yml configuration to molecule/default/molecule.yml
  - Set up appropriate verifiers in Molecule to replace InSpec functionality

- **Chef Automate/Infra Server**: Replace with Ansible automation platform:
  - Convert Chef Automate deployment scripts to Ansible roles for infrastructure management
  - Consider using AWX/Tower for web UI and API functionality similar to Chef Automate

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL certificate generation and configuration:
  - Maintain the same security hardening in migrated playbooks
  - Consider enhancing with more robust certificate management (Let's Encrypt integration)

- **SSH Hardening**: The SSH profile checks for secure SSH configuration:
  - Implement equivalent checks in Ansible using ansible-lint or custom modules
  - Create an Ansible role for SSH hardening that implements the same security controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be migrated to Ansible Vault
  - No other credential patterns detected in the repository

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible testing frameworks:
  - Challenge: InSpec has specific syntax for compliance testing that doesn't directly map to other testing frameworks
  - Mitigation: Use Molecule with testinfra or Goss, which provide similar functionality, or consider maintaining InSpec as a testing tool even with Ansible

- **Chef Server Functionality**: Replacing Chef Server functionality with Ansible equivalents:
  - Challenge: Chef Server provides centralized configuration management that needs equivalent functionality in Ansible
  - Mitigation: Implement AWX/Tower for centralized control and consider GitOps workflows for configuration management

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need restructuring to follow best practices
2. **Testing Framework**: Moderate complexity, convert InSpec tests to Molecule/testinfra or maintain InSpec as a testing tool
3. **Chef Automate/Server Deployment**: Higher complexity, replace with Ansible AWX/Tower deployment playbooks

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production, as indicated by the README mentioning "working examples" related to content created by Technical Product Marketing.
2. The Chef InSpec tests are used for validation and compliance checking of infrastructure set up by Ansible playbooks.
3. The setup-automate scripts are used for setting up a Chef environment, which may be used for comparison or demonstration alongside Ansible.
4. The migration goal is to standardize on Ansible rather than maintain a hybrid Chef/Ansible environment.
5. The hardcoded credentials in the setup scripts are for demonstration purposes and not used in production environments.
6. The Test Kitchen configuration is used for testing the Ansible playbooks with InSpec verification.