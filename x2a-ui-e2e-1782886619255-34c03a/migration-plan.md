# MIGRATION FROM CHEF/INSPEC TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec compliance tests and Ansible playbooks demonstrating how to use Chef InSpec alongside Ansible for compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible compliance solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but deployment scripts suggest on-premises or generic cloud VM usage

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Convert InSpec tests to Ansible assert modules and blocks
  - Option 2: Use ansible-lint for static analysis
  - Option 3: Integrate with Ansible Automation Platform's compliance capabilities
  - Option 4: Keep using InSpec but call it from Ansible using command/shell modules

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - ansible-test for collections testing

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains the only enabled protocol
  - Maintain proper certificate generation and management

- **SSH Hardening**: The SSH root login control must be preserved
  - Convert the InSpec control to equivalent Ansible assertions or include in ansible-lint checks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible assert module with careful condition mapping
  - Consider maintaining some InSpec tests and calling them from Ansible if direct conversion is too complex

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs an equivalent in Ansible
  - Mitigation: Integrate with Ansible Automation Platform's compliance capabilities or use a third-party solution

- **Chef Server Deployment**: Converting Chef server deployment to Ansible requires understanding of Chef's architecture
  - Mitigation: Create Ansible roles that install and configure equivalent functionality or alternative solutions

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, just need review and potential refactoring to follow best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible assertions or alternative testing framework
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible roles for infrastructure deployment

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being production infrastructure code
2. The existing Ansible playbooks are functional and follow reasonable practices
3. The target environment will continue to be Ubuntu 20.04 or compatible systems
4. There's no requirement to maintain Chef Automate/Infra Server specifically; the goal is to provide equivalent functionality in Ansible
5. The hardcoded credentials in deployment scripts are for demonstration purposes only
6. The Test Kitchen configuration is primarily for demonstration and testing, not for production deployment
7. The compliance requirements represented by the InSpec tests must be preserved in the Ansible migration