# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used for compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while maintaining the existing Ansible playbooks. The estimated timeline for this migration is 1-2 weeks given the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests in a Vagrant environment
- `index.html`: Simple HTML file used as a test page for the web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace with `ansible-test` for integration testing
  - Use Ansible's `assert` module for in-playbook validation
  - Consider Molecule for more comprehensive testing
  - Alternatively, integrate with pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role and playbook testing
  - Ansible's built-in `ansible-playbook --check` for validation

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
  - Approach: Preserve the same configuration in the Ansible playbooks

- **SSH Security Controls**: The SSH root login restriction must be maintained
  - Approach: Convert the InSpec control to an Ansible task that ensures the same configuration

- **Self-signed Certificates**: The current implementation uses self-signed certificates
  - Approach: Maintain the same approach or consider integrating with Let's Encrypt for production environments

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module with appropriate conditionals to achieve similar validation

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs to be replicated
  - Mitigation: Consider integrating with tools like AWX/Tower for reporting or implement custom reporting using Ansible's callback plugins

- **Chef Automate/Server Deployment**: The Chef infrastructure deployment scripts need to be completely replaced
  - Mitigation: Create Ansible roles for infrastructure management or consider if this functionality is still needed

### Migration Order

1. **website_https_verify** (Priority 1): Convert InSpec tests to Ansible assertions or Molecule tests
2. **ssh_profile** (Priority 2): Convert InSpec control to Ansible task with appropriate checks
3. **Chef deployment scripts** (Priority 3): Determine if Chef infrastructure is still needed; if not, remove; if yes, create equivalent Ansible roles

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance testing
2. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) can remain largely unchanged
3. The Chef Automate and Chef Server deployment scripts may no longer be needed if moving entirely to Ansible
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. Test Kitchen is only used for development/testing and not in production pipelines
6. The security compliance requirements (STIG references in ssh_profile.rb) must be maintained in the Ansible implementation
7. No external data sources or dynamic inventory is being used in the current implementation