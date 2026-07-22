# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be migrated to a unified Ansible approach. The repository primarily consists of:

1. Ansible playbooks for configuring web servers with HTTPS
2. Chef InSpec tests for validating configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **MEDIUM** with an estimated timeline of 2-3 weeks. The main challenge will be converting the Chef InSpec tests to Ansible-compatible testing frameworks while maintaining the same level of compliance validation.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Security hardening, SSL protocol configuration

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Shell Script
    - Key Features: Chef Automate installation, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Shell Script
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for validating HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for validating SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML file for web server testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-test with custom modules
  - Option 2: Integrate with Molecule for testing
  - Option 3: Use the ansible.builtin.assert module for validation checks

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality but is more Ansible-native
  - Will require converting the kitchen.yml configuration to molecule.yml

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks
  - Create roles for server configuration
  - Use ansible.builtin.user module for user management
  - Consider integrating with AWX/Ansible Tower for UI capabilities

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in poodle_fix.yml
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain proper certificate generation and management

- **SSH Hardening**: The SSH security profile must be maintained
  - Convert the InSpec SSH profile to Ansible assertions or checks
  - Ensure PermitRootLogin remains disabled

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely, possibly with ansible-vault

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks
  - InSpec provides rich compliance testing that must be replicated
  - Solution: Use a combination of ansible.builtin.assert, custom modules, and external tools like Molecule

- **Maintaining Compliance Validation**: Ensuring the same level of compliance checking
  - The current setup uses InSpec for compliance validation alongside Ansible
  - Solution: Implement compliance-as-code using Ansible roles with built-in validation

- **Chef Server Deployment**: Replacing Chef server deployment with equivalent functionality
  - Current scripts deploy Chef Automate and Chef Infra Server
  - Solution: Create Ansible roles for configuration management server setup (consider AWX/Tower)

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to a proper Ansible role structure

2. **poodle_fix.yml** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - Integrate with the website_https role

3. **InSpec Tests** (moderate complexity)
   - Convert InSpec tests to Ansible-compatible testing
   - Implement equivalent checks using ansible.builtin.assert or Molecule

4. **Chef Deployment Scripts** (high complexity)
   - Replace with Ansible playbooks for deploying configuration management
   - Consider AWX/Tower as a replacement for Chef Automate

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation.
2. The Chef components (Automate and Infra Server) are used for demonstration purposes and not critical to the actual infrastructure management.
3. The target environment is Ubuntu 20.04 running on Vagrant VMs.
4. The security compliance requirements (SSL configuration, SSH hardening) must be maintained in the migrated solution.
5. The current setup uses Test Kitchen for testing, which will need to be replaced with an Ansible-native testing solution.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure credential management.