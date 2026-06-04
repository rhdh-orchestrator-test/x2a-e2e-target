# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.
**Complexity**: Low to Medium - The repository contains a limited number of files with clear purposes.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test profile that validates HTTPS configuration and website availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that validates SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, STIG compliance check

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script using Chef Automate CLI
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script using Chef Automate CLI
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework configuration
- `index.html`: Sample HTML file used in the web server deployment - can be preserved as-is

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use the `ansible.builtin.assert` module for simple validation
  - Option 2: Use Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source alternatives:
  - AWX (open-source upstream of Ansible Tower)
  - Ansible Semaphore
  - Ansible Automation Platform (commercial)

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure the SSLProtocol settings are maintained in the Apache configuration
  - Verify that only TLSv1.2 is enabled and SSLv3 is disabled

- **SSH Hardening**: The SSH security checks in ssh_profile.rb need to be preserved
  - Convert the InSpec control to Ansible assert or Molecule verification
  - Maintain compliance with the referenced STIG requirements (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts need to be moved to Ansible Vault
  - Count: 2 credential sets (username/password) in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions
  - Challenge: InSpec has specific resources for SSL/TLS testing that may not have direct equivalents in Ansible
  - Mitigation: May need to use custom Ansible modules or shell commands with assert for some validations

- **Chef Automate Functionality**: Replacing Chef Automate with Ansible alternatives
  - Challenge: Chef Automate provides specific compliance reporting features
  - Mitigation: Evaluate if AWX/Tower can provide similar compliance reporting or if additional tools are needed

### Migration Order

1. **InSpec Tests** (Priority 1, moderate complexity)
   - Convert website_https_verify.rb to Ansible tests
   - Convert ssh_profile.rb to Ansible tests

2. **Deployment Scripts** (Priority 2, moderate complexity)
   - Convert deploy-chef-server.sh to Ansible playbook
   - Convert deploy-automate.sh to Ansible playbook

3. **Testing Framework** (Priority 3, low complexity)
   - Replace Test Kitchen with Molecule

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) can be preserved as-is
2. The target environment will continue to be Ubuntu 20.04
3. The team is familiar with Ansible but may need training on Ansible testing frameworks
4. There is no requirement to maintain backward compatibility with Chef InSpec
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be replaced with secure alternatives
6. The deployment scripts are intended for on-premises or cloud VM deployment, not container deployment