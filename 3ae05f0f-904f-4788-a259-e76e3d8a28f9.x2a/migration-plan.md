# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance testing. The repository also includes scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the content is already in Ansible format. The main migration tasks will involve:
1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Updating the deployment scripts to use Ansible instead of Bash
3. Ensuring the existing Ansible playbooks follow best practices

Estimated timeline: 1-2 weeks for a small team, with low complexity.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML file for the web server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions like:
  - Molecule for infrastructure testing
  - ansible-lint for playbook linting
  - testinfra for infrastructure validation

- **Test Kitchen with Vagrant**: Replace with:
  - Molecule for Ansible role testing
  - Or keep Test Kitchen but use the ansible_playbook provisioner (which is already in use)

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 only, disabling older protocols. This security practice should be maintained in the migrated solution.
  - Migration approach: Use the same configuration in Ansible, ensuring TLS 1.2 is enforced

- **SSH Security**: The InSpec tests verify that root login via SSH is disabled.
  - Migration approach: Create an Ansible task to verify and enforce this configuration, possibly using ansible.posix.sshd_config module

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to an Ansible-compatible testing framework.
  - Mitigation strategy: Use testinfra which has a similar syntax and can be integrated with Ansible playbooks

- **Chef Automate Deployment**: The current deployment uses bash scripts with specific Chef commands.
  - Mitigation strategy: Create Ansible roles that perform the same functions, possibly using the uri module to interact with Chef APIs

### Migration Order

1. Convert existing Ansible playbooks to follow best practices (low risk, high value)
   - Organize into roles and collections
   - Implement variable files instead of inline variables
   - Use Ansible Vault for sensitive data

2. Create Ansible playbooks to replace the Chef deployment bash scripts (moderate complexity)
   - Create roles for Chef Server and Chef Automate deployment
   - Use Ansible Vault for credentials

3. Convert InSpec tests to Ansible-compatible testing framework (high complexity)
   - Implement testinfra or Molecule tests
   - Ensure all compliance checks are maintained

### Assumptions

1. The primary goal is to standardize on Ansible as the configuration management tool
2. Chef InSpec is currently being used only for testing, not for actual configuration management
3. The deployment scripts are used for setting up test environments, not production systems
4. The existing Ansible playbooks are functional but may not follow best practices
5. No external dependencies or third-party modules are being used beyond what's visible in the repository
6. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
7. The security requirements (TLS 1.2, SSH hardening) will remain the same
8. Test Kitchen may still be used as a testing framework, just with Ansible as the provisioner