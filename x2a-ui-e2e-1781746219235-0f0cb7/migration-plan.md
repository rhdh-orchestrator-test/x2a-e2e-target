# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks designed to demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL/TLS protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (STIG)

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Sample HTML file used for testing the web server. Can be preserved as-is or included in Ansible content.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - **Option 1**: Use Ansible's built-in `assert` module for basic testing
  - **Option 2**: Integrate with Molecule for more comprehensive testing
  - **Option 3**: Use ansible-lint for static analysis and best practices validation

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality to Test Kitchen but is designed specifically for Ansible

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks
  - Consider using community-maintained Ansible roles for Chef server deployment if Chef infrastructure is still needed
  - Alternatively, migrate completely to Ansible AWX/Tower for similar functionality

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains the minimum protocol version
  - Consider updating to also include TLSv1.3 support

- **SSH Hardening**: The SSH security controls from the InSpec profile need to be implemented in Ansible
  - Convert the InSpec control to Ansible tasks that enforce the same security policy
  - Consider using the ansible.posix.sshd module for managing SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests
  - Challenge: InSpec provides domain-specific language for compliance testing that doesn't directly map to Ansible
  - Mitigation: Use a combination of Ansible assert module and custom modules where needed

- **Compliance Reporting**: InSpec provides rich compliance reporting capabilities
  - Challenge: Replicating the compliance reporting functionality in Ansible
  - Mitigation: Consider integrating with tools like Ansible AWX/Tower for reporting or using community modules for compliance reporting

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible
  - Challenge: Ensuring all Chef server configuration options are properly translated
  - Mitigation: Use Ansible's uri module to interact with Chef APIs where needed

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format
   - Review and update to current Ansible best practices
   - Ensure idempotency and proper error handling

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity
   - Convert to Ansible assertions or Molecule tests
   - Ensure equivalent coverage and validation

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity
   - Convert to Ansible playbooks
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and don't require significant changes beyond migration to current best practices.

2. The Chef InSpec tests are used primarily for validation and compliance checking, not for configuration management.

3. The deployment scripts for Chef Automate and Chef Infra Server are used for setting up a Chef infrastructure, which may be replaced entirely by Ansible or may still be needed depending on organizational requirements.

4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.

5. The security requirements specified in the InSpec profiles (particularly SSH hardening) must be maintained in the Ansible implementation.

6. Test Kitchen is currently used for testing the Ansible playbooks, and this functionality needs to be preserved in the migration.

7. The repository appears to be a demonstration or example repository rather than production code, but the migration should treat it as production-quality code.