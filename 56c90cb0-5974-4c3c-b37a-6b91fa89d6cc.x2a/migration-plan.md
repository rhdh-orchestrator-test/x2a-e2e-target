# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef-related setup scripts that need to be migrated to a unified Ansible approach. The repository primarily consists of:

1. Ansible playbooks for configuring web servers with HTTPS
2. Chef InSpec tests for validating configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is relatively low as most of the infrastructure code is already in Ansible format. The main focus will be on converting the Chef InSpec tests to Ansible-compatible testing frameworks and replacing the Chef Automate/Infra Server deployment scripts with Ansible playbooks.

Estimated timeline: 1-2 weeks for a complete migration, with the majority of time spent on creating equivalent testing capabilities in Ansible.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration
- `tests/ssh_profile.rb`: InSpec profile for SSH security compliance
- `index.html`: Sample HTML file for the web server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (latest)**: Replace with Ansible Molecule for testing
- **InSpec (latest)**: Replace with Ansible-compatible testing frameworks:
  - For infrastructure validation: Molecule with Testinfra or Goss
  - For compliance testing: OpenSCAP with ansible-lockdown or Ansible Compliance as Code
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible roles for configuration management platform setup

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL/TLS. Ensure the migration maintains or improves the security posture:
  - Enforce TLSv1.2+ protocol usage
  - Disable weak ciphers
  - Implement proper certificate management
  
- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions. Ensure equivalent checks are implemented in the Ansible-based testing framework.

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec tests to an Ansible-compatible testing framework will require careful mapping of test assertions:
  - Challenge: InSpec has domain-specific language for compliance testing
  - Mitigation: Use Ansible Compliance as Code or OpenSCAP with equivalent controls

- **Configuration Management Platform**: Replacing Chef Automate/Infra Server with an Ansible-based solution:
  - Challenge: Chef Automate provides compliance reporting that needs an equivalent in the Ansible ecosystem
  - Mitigation: Consider AWX/Tower with compliance add-ons or integrate with external compliance tools

### Migration Order

1. **website_https playbook** (low risk, already in Ansible format)
   - Review and optimize the existing Ansible playbook
   - Add idempotency improvements if needed
   - Update to use Ansible best practices and current modules

2. **poodle_fix playbook** (low risk, already in Ansible format)
   - Review and optimize the existing Ansible playbook
   - Consider merging with website_https as a role or included task

3. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Molecule with Testinfra or Goss
   - Convert ssh_profile.rb to Ansible-compatible compliance testing

4. **Chef Automate/Server Deployment Scripts** (high complexity)
   - Create Ansible roles to replace the deployment scripts
   - Implement secure credential management with Ansible Vault
   - Add idempotency to ensure repeatable deployments

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
2. Vagrant will continue to be used for development/testing environments
3. The migration aims to replace both the Chef InSpec testing and Chef Automate/Server components with Ansible-native solutions
4. No actual Chef cookbooks exist in the repository that need migration (only InSpec tests and setup scripts)
5. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functional and can be used as a reference for the migration style
6. The security requirements (SSL configuration, SSH hardening) must be maintained or enhanced in the migrated solution