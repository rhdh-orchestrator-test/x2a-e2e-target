# MIGRATION FROM CHEF AND BASH TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests, Ansible playbooks, and Bash scripts for Chef Automate/Chef Infra Server deployment. The migration scope is relatively small, focusing on:

1. Existing Ansible playbooks that need to be reviewed and potentially refactored
2. Chef InSpec tests that need to be migrated to Ansible-compatible testing frameworks
3. Bash scripts for Chef server deployment that need to be converted to Ansible playbooks

The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity. The primary challenge will be maintaining the compliance testing functionality currently provided by Chef InSpec while moving to an Ansible-native solution.

## Module Migration Plan

This repository contains Chef InSpec tests, Ansible playbooks, and Bash scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook for deploying a secure Apache web server with HTTPS support
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook for remediating SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test for verifying HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control for validating SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Sample HTML file used for testing web server deployment. Can be incorporated into Ansible as a template.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-test for infrastructure validation

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing and validation

- **Chef Automate/Infra Server**: Determine if these components need to be replaced with Ansible equivalents:
  - Option 1: Replace with AWX/Ansible Tower for enterprise management
  - Option 2: Use Ansible Automation Platform for compliance and governance

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening present in the POODLE fix playbook
  - Approach: Create an Ansible role for Apache security hardening that includes the SSL protocol restrictions

- **SSH Security**: The SSH compliance checks need to be maintained
  - Approach: Convert the InSpec SSH profile to Ansible assertions or Molecule tests

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys should be managed securely, potentially using ansible-vault for sensitive data

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible validation
  - Mitigation: Use a combination of Ansible's assert module and custom modules to replicate InSpec functionality
  - Consider using Ansible's built-in modules like uri, stat, and command to perform equivalent checks

- **Maintaining Compliance Validation**: Ensuring the same level of compliance checking
  - Mitigation: Document each compliance check and create equivalent Ansible tasks or roles

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible
  - Mitigation: Create an Ansible role for Chef server deployment if still needed, or determine if this functionality should be replaced entirely with Ansible Tower/AWX

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
   - Review and refactor according to best practices
   - Convert to roles for better organization

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Moderate complexity
   - Convert to Ansible assertions or Molecule tests
   - Ensure all compliance checks are maintained

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - High complexity
   - Determine if Chef server is still needed in the Ansible environment
   - If needed, create Ansible roles for deployment
   - If not needed, document the replacement approach with Ansible tools

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible, as indicated in the README.md
2. The Chef InSpec tests are essential for compliance validation and must be preserved in functionality
3. The Chef server deployment scripts may be optional if moving entirely to Ansible
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. No complex Chef cookbooks or recipes are present that would require significant conversion effort
6. The repository appears to be example/demonstration code rather than production infrastructure
7. The hardcoded credentials in the deployment scripts are for demonstration purposes only
8. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are already functional and may only need refactoring