# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more structured Ansible format and replacing Chef InSpec tests with Ansible-native testing solutions. The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef components that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (kitchen.yml)**: Replace with Ansible Molecule for testing
- **InSpec Tests**: Convert to Ansible-native testing with:
  - ansible-lint for static analysis
  - testinfra for infrastructure testing
  - ansible-test for module testing
- **Chef Automate/Server Deployment**: Convert bash scripts to Ansible roles for deploying monitoring/management solutions

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should maintain or enhance security settings:
  - Self-signed certificate generation should be preserved
  - TLS protocol restrictions (disabling SSLv3) should be maintained
  - Consider enhancing with modern cipher suites

- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Ensure root login remains disabled
  - Maintain SSH security controls in the migrated solution

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks will require mapping InSpec resources to appropriate Ansible modules or testinfra functions
  - Mitigation: Create a mapping document for InSpec resources to Ansible equivalents

- **Chef Server Deployment**: The Chef server deployment scripts need to be replaced with equivalent infrastructure
  - Mitigation: Evaluate if Chef Server is still needed or if Ansible can fully replace its functionality

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, direct conversion to Ansible roles
2. **Testing Framework**: Convert InSpec tests to Ansible-native testing solutions
3. **Chef Deployment Scripts**: Replace with Ansible roles for deploying management infrastructure

### Assumptions

1. The repository is primarily used for demonstration purposes as indicated by the main README.md
2. The Chef InSpec tests are used alongside Ansible for compliance verification
3. The deployment scripts are used for setting up Chef infrastructure, which may be replaced by Ansible AWX/Tower
4. No complex Chef cookbooks or recipes are present that would require significant conversion effort
5. The target environment will continue to be Ubuntu 20.04 or compatible systems
6. The self-signed certificates are acceptable for the use case and don't need to be replaced with CA-signed certificates
7. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be properly secured in the migrated solution