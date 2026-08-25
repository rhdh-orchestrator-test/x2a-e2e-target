# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration would be 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

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

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/index.html`: Simple HTML file used for testing. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - For `website_https_verify.rb`: Use Ansible assert module or molecule verify
  - For `ssh_profile.rb`: Use Ansible-lint or ansible.posix collection for SSH hardening

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or improve security settings:
  - Ensure TLS 1.2+ is enforced (as in poodle_fix.yml)
  - Consider using Let's Encrypt instead of self-signed certificates
  - Implement proper certificate management

- **SSH Hardening**: The InSpec profile checks for SSH root login. Migration should:
  - Implement SSH hardening using ansible.posix collection
  - Maintain compliance with security standards referenced in the InSpec profile (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require:
  - Understanding the compliance requirements in the InSpec tests
  - Implementing equivalent checks using Ansible modules or Molecule
  - Ensuring the same level of compliance reporting

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible will require:
  - Understanding the Chef Automate architecture
  - Creating Ansible roles for Chef Automate installation
  - Implementing idempotent user and organization creation

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, just need to be organized into roles and potentially updated for best practices.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible-native testing.
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity due to the need to understand Chef Automate architecture.

### Assumptions

1. The primary goal is to migrate all components to pure Ansible without dependencies on Chef tools.
2. The InSpec tests are used for compliance validation and need to be replaced with equivalent Ansible functionality.
3. The deployment scripts are used for setting up Chef infrastructure, which may not be needed if moving entirely to Ansible.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The security requirements specified in the InSpec profiles must be maintained in the Ansible implementation.
6. The repository is primarily for demonstration purposes rather than production use, based on the README content.