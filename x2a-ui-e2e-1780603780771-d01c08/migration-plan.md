# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate to a pure Ansible solution. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3, enables TLSv1.2 only

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing the web server. Can be directly used in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible alternatives:
  - For compliance testing: Use Ansible's built-in assert module or migrate to ansible-lint
  - For infrastructure testing: Use Molecule with testinfra or ansible-test
  - For security compliance: Consider OpenSCAP with ansible-collection-hardening

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure code

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or AWX (open-source version of Ansible Tower)

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL/TLS configuration is maintained during migration.
  - Migration approach: Use ansible.builtin.openssl_* modules as already implemented

- **SSH Security**: The InSpec tests verify SSH root login is disabled.
  - Migration approach: Use ansible-lint security rules or create equivalent assert tasks

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible assertions or testinfra tests.
  - Mitigation: Use Ansible's assert module for simple tests and testinfra for more complex infrastructure validation.

- **Chef Automate Deployment**: Replacing Chef Automate with Ansible Automation Platform or AWX.
  - Mitigation: Create Ansible playbooks to deploy and configure AWX/Ansible Automation Platform.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, just need review and potential refactoring.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible testing framework.
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires replacing with Ansible Automation Platform or AWX deployment.

### Assumptions

1. The primary goal is to move away from Chef InSpec for testing while maintaining or enhancing compliance capabilities.
2. The existing Ansible playbooks are functional and follow best practices.
3. The deployment scripts for Chef Automate and Chef Infra Server need to be replaced with equivalent Ansible Automation Platform or AWX deployment.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The security requirements (SSL configuration, SSH hardening) need to be maintained in the migrated solution.
6. No specific performance requirements are mentioned, so standard Ansible performance is assumed to be acceptable.
7. The migration will include updating documentation to reflect the new Ansible-only approach.
8. The hardcoded credentials in the deployment scripts will be replaced with secure credential management.