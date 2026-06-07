# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests, needs to be replaced with Ansible-native testing framework
- `index.html`: Sample HTML file used for testing the web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Keep InSpec but run it from Ansible using the `command` or `shell` module

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible-specific CI/CD pipelines

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab/GitHub for code repository
  - Compliance scanning tools like OpenSCAP or DISA STIG tools

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Migration approach: Keep the existing Ansible task that enforces TLSv1.2
  
- **SSH Hardening**: The SSH root login check needs to be converted to an Ansible-compatible test
  - Migration approach: Convert the InSpec control to an Ansible assert task or Molecule test

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated on the fly, no pre-existing secrets detected
  - Count of credentials per module:
    - chef-automate-deployment: 3 (username, password, email)
    - chef-server-deployment: 3 (username, password, email)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's domain-specific language to Ansible's more general-purpose testing capabilities
  - Mitigation: Use Ansible's assert module with appropriate conditionals or consider using Molecule which provides more testing capabilities

- **Test Kitchen Workflow**: Replacing the Test Kitchen workflow with an Ansible-native testing approach
  - Mitigation: Implement Molecule testing framework which is designed specifically for Ansible roles and playbooks

- **Chef Server Deployment**: Converting the Chef Server deployment scripts to Ansible
  - Mitigation: Create Ansible roles for deploying alternative infrastructure like AWX/Tower or other configuration management solutions

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
   - Review and optimize according to best practices
   - Update any deprecated syntax

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Moderate complexity
   - Convert to Ansible assert tasks or Molecule tests
   - Ensure all compliance checks are preserved

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - High complexity
   - Create Ansible playbooks to replace Chef infrastructure with Ansible AWX/Tower or other alternatives
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't need functional changes
2. The InSpec tests are currently being used for compliance validation and these compliance requirements must be maintained
3. The organization is moving completely from Chef to Ansible, including replacing Chef Automate/Infra Server with Ansible-based solutions
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The self-signed certificates approach is acceptable for the migrated solution
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure alternatives
7. The migration will maintain the same level of security compliance as the original implementation