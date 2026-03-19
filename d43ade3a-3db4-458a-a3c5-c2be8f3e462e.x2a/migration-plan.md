# MIGRATION FROM CHEF/INSPEC TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing rather than containing Chef cookbooks that need migration. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible playbooks are already in place. The primary migration task will be to replace the Chef InSpec tests with equivalent Ansible-native testing solutions. The estimated timeline for this migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH server configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security requirements (STIG)

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef server installation, user and organization creation

- **automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML content for the web server

### Target Details

Based on the source repository:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but scripts are designed to work on cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions like:
  - **ansible-lint**: For static analysis of playbooks
  - **Molecule**: For testing Ansible roles
  - **testinfra**: Python-based testing framework that can be used with Ansible

- **Test Kitchen**: Replace with Molecule for testing Ansible roles and playbooks

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
- **SSH Security**: The SSH security checks in ssh_profile.rb need to be implemented in Ansible
- **Self-signed Certificates**: The certificate generation process should be maintained or improved
- **User Credentials**: The hardcoded credentials in the deployment scripts should be replaced with Ansible Vault or another secure solution

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible-native testing frameworks will require careful mapping of test assertions
- **Chef Server Deployment**: The Chef server deployment scripts need to be replaced with equivalent Ansible playbooks if Chef infrastructure is still needed

### Migration Order

1. Convert InSpec tests to testinfra or other Ansible-compatible testing framework (low risk)
2. Replace Test Kitchen with Molecule for testing (moderate complexity)
3. Convert Chef server deployment scripts to Ansible playbooks (higher complexity)

### Assumptions

1. The primary goal is to move away from Chef InSpec for testing while maintaining the existing Ansible playbooks
2. The Chef server deployment scripts may still be needed if Chef is used elsewhere in the organization
3. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
4. The security requirements specified in the InSpec tests (especially the STIG requirements) must be maintained
5. The repository is primarily a demonstration of how Chef InSpec can work with Ansible rather than a production infrastructure repository