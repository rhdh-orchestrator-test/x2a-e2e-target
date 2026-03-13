# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the existing InSpec tests to Ansible-native testing solutions while maintaining the existing Ansible playbooks. Additionally, there are Chef server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium
**Primary Focus**: Converting InSpec tests to Ansible-native testing solutions

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Security hardening, SSL protocol configuration

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

- **chef-server-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef server CLI
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for the web server

### Target Details

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - **Option 1**: Use Ansible's `assert` module for basic validation
  - **Option 2**: Integrate with Molecule for more comprehensive testing
  - **Option 3**: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible-native testing framework

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
- **SSH Hardening**: The SSH security checks in ssh_profile.rb need to be implemented in Ansible
- **Secrets Management**: The Chef server deployment scripts contain hardcoded credentials that should be moved to Ansible Vault

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing style to Ansible's procedural approach may require additional logic
- **Compliance Reporting**: InSpec provides built-in compliance reporting that will need to be replicated in Ansible
- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible will require understanding of Chef server architecture

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may need minor updates for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-native testing solutions
3. **Chef Server Deployment Scripts**: Create equivalent Ansible playbooks for Chef server deployment
4. **Test Kitchen Configuration**: Replace with Molecule for testing

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance testing
2. The existing Ansible playbooks are functional and follow best practices
3. The target environment will remain Ubuntu 20.04 on Vagrant
4. The Chef server deployment scripts are used for setting up test environments and not production systems
5. No additional Chef cookbooks or resources are used beyond what's visible in the repository
6. The migration does not require changes to the application functionality, only to the infrastructure code
7. The team has expertise in both Chef InSpec and Ansible to facilitate the migration