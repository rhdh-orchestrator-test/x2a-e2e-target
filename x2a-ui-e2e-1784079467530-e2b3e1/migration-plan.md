# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also contains Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

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
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static code analysis
  - Option 3: Use Molecule for testing Ansible roles
  - Option 4: Continue using InSpec but call it from Ansible using the command module

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible's built-in testing capabilities

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain proper certificate generation and management

- **SSH Security**: Maintain the SSH root login restrictions as verified by the InSpec test
  - Implement equivalent checks using Ansible's assert module or other testing framework

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts need to be moved to Ansible Vault
  - Count: 2 credential sets (username/password) in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing mechanisms
  - Mitigation: Use Ansible's assert module or integrate with a testing framework like Molecule

- **Chef Automate Deployment**: Replacing Chef Automate deployment with equivalent functionality
  - Mitigation: Determine if Chef Automate is still needed or if it can be replaced with Ansible Tower/AWX

### Migration Order

1. **website_https.yml** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to Ansible role structure for better organization

2. **poodle_fix.yml** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Consider merging with website_https role as a security task

3. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assertions or Molecule tests
   - Convert ssh_profile.rb to Ansible assertions or Molecule tests

4. **Chef Deployment Scripts** (high complexity)
   - Convert deploy-automate.sh to Ansible playbook
   - Convert deploy-chef-server.sh to Ansible playbook
   - Implement proper secret management using Ansible Vault

### Assumptions

1. The primary goal is to migrate all components to pure Ansible without relying on Chef InSpec
2. The Chef Automate and Chef Infra Server deployments are still needed in the target environment
3. The security compliance requirements will remain the same after migration
4. The target environment will continue to be Ubuntu 20.04 running on Vagrant
5. No additional functionality beyond what's in the current repository is required
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be replaced with secure alternatives
7. The self-signed certificates are acceptable for the target environment (not requiring trusted CA certificates)