# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for demonstrating compliance automation. The primary focus appears to be on showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are shell scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Disables SSLv3, enables TLSv1.2 only

- **inspec_tests**:
    - Description: Chef InSpec tests that verify HTTPS functionality, security, and SSH configuration
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification, SSH security compliance

- **chef-automate-setup**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing web server functionality. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - For `website_https_verify.rb`: Use Ansible URI module for HTTP checks and community.crypto modules for SSL verification
  - For `ssh_profile.rb`: Use Ansible assert module with command/shell modules or ansible-lint for compliance checks

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. Ensure this security hardening is maintained in the migrated Ansible playbooks.
  - Migration approach: Use the same configuration parameters in the Ansible apache2_module and template modules.

- **SSH Security**: The InSpec tests verify SSH root login is disabled. Ensure this check is maintained.
  - Migration approach: Create an equivalent Ansible task that checks the SSH configuration.

- **Self-signed Certificates**: The playbook generates self-signed certificates. Consider using Let's Encrypt for production.
  - Migration approach: Maintain the self-signed certificate generation using Ansible's openssl_* modules as already implemented.

- **Vault/secrets management**:
  - Hardcoded credentials in shell scripts: The deploy-automate.sh and deploy-chef-server.sh scripts contain hardcoded usernames and passwords.
  - Migration approach: Replace with Ansible Vault for secure credential storage.

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification tasks.
  - Mitigation strategy: Use Ansible assert module combined with command/shell modules to perform the same checks, or consider using ansible-lint for compliance checking.

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible.
  - Mitigation strategy: Create Ansible roles for Chef Automate and Chef Infra Server deployment, using the official installation documentation as a reference.

### Migration Order

1. **Ansible playbooks** (low risk, already in Ansible format)
2. **InSpec tests** (moderate complexity, requires conversion to Ansible testing framework)
3. **Chef deployment scripts** (higher complexity, requires understanding of Chef Automate architecture)

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments.
2. The InSpec tests are used for compliance verification of systems managed by Ansible.
3. The deployment scripts are used for setting up Chef infrastructure, which may be replaced entirely by Ansible.
4. No external Chef cookbooks or recipes are being used, as no Berksfile, metadata.rb, or cookbook directories were found.
5. The target environment is Ubuntu 20.04 running on Vagrant VMs.
6. The security requirements (TLS 1.2, SSH hardening) need to be maintained in the migrated solution.
7. The migration will involve converting InSpec tests to equivalent Ansible verification tasks.
8. The Chef Automate and Chef Infra Server deployment may be replaced with Ansible AWX/Tower or other Ansible-based solutions.