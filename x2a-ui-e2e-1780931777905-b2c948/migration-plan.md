# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used for testing the web server deployment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Molecule with Testinfra for Python-based testing
  - Option 2: Ansible Test for native Ansible testing capabilities
  - Option 3: Convert InSpec tests to Ansible assert tasks

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for automation platform
  - GitLab CI/CD or Jenkins for CI/CD pipelines
  - Compliance scanning tools like OpenSCAP or Ansible Compliance

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Approach: Maintain the same configuration parameters in the Ansible tasks

- **SSH Security**: The SSH root login compliance check needs to be converted to Ansible
  - Approach: Create an Ansible task that checks the sshd_config file for PermitRootLogin settings

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected:
    - website_https.yml: 0 hardcoded credentials
    - poodle_fix.yml: 0 hardcoded credentials
    - deploy-automate.sh: 3 credentials (username, useremail, userpassword)
    - deploy-chef-server.sh: 3 credentials (username, useremail, userpassword)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting Ruby-based InSpec tests to Ansible-compatible testing frameworks
  - Mitigation: Use Testinfra with Molecule which provides similar testing capabilities in Python

- **Chef Automate Functionality**: Replacing Chef Automate's compliance scanning and reporting
  - Mitigation: Implement OpenSCAP or Ansible Compliance automation with custom reporting

- **System Requirements**: Maintaining the same system requirements (vm.max_map_count, vm.dirty_expire_centisecs)
  - Mitigation: Include these as pre-tasks in the Ansible playbooks that replace the deployment scripts

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format
   - Only need to be reviewed and potentially refactored to follow best practices

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Medium complexity
   - Convert to Ansible-compatible testing framework
   - Ensure all compliance checks are preserved

3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity
   - Convert to Ansible playbooks
   - Replace Chef Automate/Server with alternative solutions

### Assumptions

1. The existing Ansible playbooks are functioning correctly and don't require significant changes beyond best practices refactoring.
2. The Chef InSpec tests are used primarily for compliance validation and can be replaced with equivalent functionality.
3. The deployment scripts are used for setting up a development/test environment rather than production.
4. There are no additional Chef cookbooks or recipes beyond what's visible in the repository.
5. The migration will replace Chef Automate/Server functionality with equivalent Ansible-based solutions.
6. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
7. No custom Chef resources or libraries are being used that would require special handling.
8. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be properly secured in the migrated solution.