# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible's native testing capabilities while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.
**Complexity**: Low to Medium - The InSpec tests are straightforward, but ensuring equivalent test coverage in Ansible will require careful implementation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS website deployment and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, STIG compliance check

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used for testing web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's native testing capabilities:
  - For basic tests: Use Ansible's `assert` module and `command`/`shell` modules with `register` and conditional checks
  - For more complex tests: Implement Ansible Molecule with testinfra or pytest
  - Alternative: Consider maintaining InSpec as a standalone testing tool that can be called from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure
  - Molecule can use Vagrant as a driver similar to Test Kitchen

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure the Apache SSL configuration continues to disable vulnerable protocols
  - Maintain the same level of TLS security (TLSv1.2)

- **SSH Security**: The SSH root login check must be preserved in the new testing framework
  - Convert the InSpec control to equivalent Ansible assertions or testinfra tests
  - Maintain compliance with the referenced security standards (STIG)

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup scripts (username, password)
  - Migration should implement Ansible Vault for these credentials
  - Self-signed certificates are generated in the playbook and should be handled securely

### Technical Challenges

- **Test Coverage**: Ensuring that the new Ansible-based tests provide the same level of validation as the InSpec tests
  - Solution: Create a test coverage matrix to map InSpec tests to new Ansible tests
  - Validate that all security checks are preserved

- **Chef Automate Replacement**: Determining the appropriate replacement for Chef Automate functionality
  - Solution: Consider AWX/Ansible Tower for web UI and job scheduling
  - Implement Ansible Collections for compliance scanning to replace Chef InSpec functionality

### Migration Order

1. **website_https.yml and poodle_fix.yml playbooks** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbooks
   - No migration needed, just integration with new testing framework

2. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible/Molecule tests
   - Convert ssh_profile.rb to Ansible/Molecule tests

3. **Chef Deployment Scripts** (high complexity)
   - Create Ansible playbooks to replace deploy-automate.sh and deploy-chef-server.sh
   - Implement Ansible Vault for credential management

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are functioning correctly and don't require modification beyond integration with new testing.
2. The organization is moving away from Chef entirely, including Chef Automate and Chef InSpec.
3. The target environment will continue to be Ubuntu 20.04 or compatible systems.
4. Vagrant will continue to be used for development/testing environments.
5. The security requirements specified in the InSpec tests must be maintained in the migrated solution.
6. No additional Chef cookbooks or resources exist beyond what's visible in the repository.
7. The Chef Automate and Chef Infra Server deployment scripts are intended to be migrated to Ansible rather than maintained as-is.
8. The hardcoded credentials in the deployment scripts are for testing purposes and will be replaced with secure credential management in the migrated solution.