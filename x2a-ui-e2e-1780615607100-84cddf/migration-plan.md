# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef server deployment scripts that need to be converted to Ansible playbooks. The estimated timeline for this migration is 1-2 weeks given the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache by disabling older SSL protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-server-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash scripts
    - Key Features: Chef server installation, user and organization creation, system configuration

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with molecule for Ansible testing.
- `index.html`: Simple HTML file used for testing web server functionality. Can be preserved as-is or converted to a template.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for both on-premises and cloud deployment (referenced in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Consider maintaining InSpec as a separate tool called from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing and validation

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLS 1.2 is enforced and older protocols are disabled
  - Maintain proper certificate generation and management

- **SSH Hardening**: Preserve the SSH security controls that prevent root login
  - Convert the InSpec control to an Ansible task that enforces the same policy

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules
  - Consider using ansible.builtin.uri module for HTTP/HTTPS testing
  - Use ansible.builtin.command with openssl for SSL protocol verification

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible
  - Mitigation: Create Ansible roles for Chef server installation and configuration
  - Use Ansible variables instead of bash variables
  - Implement idempotent checks before installation steps

### Migration Order

1. **website_https.yml and poodle_fix.yml**: Already in Ansible format, only need review and potential refactoring to follow best practices (low risk)
2. **InSpec Tests**: Convert to Ansible-compatible testing framework (moderate complexity)
3. **Chef Server Deployment Scripts**: Convert to Ansible playbooks (moderate complexity)

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and don't require significant changes beyond potential refactoring.
2. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance testing.
3. The deployment scripts are used for setting up Chef infrastructure, which may be replaced entirely with Ansible infrastructure in the future.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. There's no requirement to maintain backward compatibility with Chef after migration.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be properly secured in the Ansible implementation.
7. The self-signed certificates are acceptable for the environment; there's no requirement for CA-signed certificates.