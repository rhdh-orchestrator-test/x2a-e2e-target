# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the existing Chef InSpec tests to Ansible-native testing solutions while maintaining the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Sample HTML file used in the website deployment. Can be maintained as-is or incorporated into Ansible as a template.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible AWX or Ansible Tower for enterprise management

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Approach: Convert the existing Ansible playbook to use the `ansible.builtin.lineinfile` module instead of `replace`

- **SSH Hardening**: The SSH compliance checks need to be converted to Ansible
  - Approach: Create an Ansible role that implements the same SSH hardening and use assert to verify compliance

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module with appropriate conditionals to achieve similar functionality

- **Compliance Metadata**: InSpec tests include rich compliance metadata (STIG IDs, CCI references) that needs to be preserved
  - Mitigation: Use Ansible playbook comments or custom variables to maintain compliance metadata

- **Test Kitchen to Molecule**: Converting the test workflow from Test Kitchen to Molecule
  - Mitigation: Create equivalent Molecule scenarios that match the existing Test Kitchen configuration

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may need minor updates for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible assertions or Molecule tests
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible roles for infrastructure deployment
4. **Testing Framework** (kitchen.yml): Replace with Molecule configuration

### Assumptions

1. The existing Ansible playbooks are functional and don't require significant refactoring
2. The team is familiar with Ansible and willing to adopt Ansible-native testing approaches
3. There is no requirement to maintain backward compatibility with Chef InSpec
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be properly secured in the migrated solution
5. The target environment will continue to be Ubuntu 20.04 or compatible
6. The migration doesn't need to include a Chef Automate/Infra Server replacement, only the deployment scripts need to be converted to Ansible