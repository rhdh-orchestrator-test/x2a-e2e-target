# MIGRATION FROM CHEF AND BASH SCRIPTS TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks, Chef InSpec tests, and Bash scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing on converting the Chef InSpec tests and Bash deployment scripts to Ansible. The existing Ansible playbooks can be retained with minor modifications to align with best practices.

**Estimated Timeline**: 1-2 weeks for a single engineer to complete the migration, including testing and documentation.

**Complexity**: Low to Medium - The repository contains a limited number of files with straightforward functionality.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Automated deployment of Chef Automate and Chef Infra Server, user and organization creation

- **website-https-configuration**:
    - Description: Ansible playbook for configuring Apache with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **compliance-tests**:
    - Description: Chef InSpec tests for SSH and HTTPS configuration
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, HTTPS configuration testing, SSL protocol verification

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `chef-and-ansible/index.html`: Sample HTML file for testing web server configuration
- `setup-automate/deploy-automate.sh`: Script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Script for deploying Chef Infra Server only

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible's built-in assert module or community.general.assert_cmd for basic tests. For more complex compliance testing, consider:
  - Ansible's built-in assert module for simple checks
  - ansible-lint for static analysis
  - Molecule for test-driven development
  - Integration with OpenSCAP or other compliance tools via Ansible

- **Test Kitchen (latest)**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible roles for:
  - Configuration management
  - Compliance automation
  - Infrastructure automation

### Security Considerations

- **SSL/TLS Configuration**: The current implementation configures Apache with TLSv1.2 and disables older protocols. Ensure the Ansible migration maintains or improves this security posture.
  - Migration approach: Create an Ansible role for Apache SSL configuration with configurable protocol settings

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled.
  - Migration approach: Create an Ansible role for SSH hardening that applies the same security controls

- **Self-signed Certificates**: The current implementation generates self-signed certificates.
  - Migration approach: Create an Ansible role that can generate self-signed certificates or integrate with Let's Encrypt for production environments

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration approach: Use Ansible Vault to secure credentials

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification methods.
  - Mitigation: Use Ansible's assert module for basic tests and consider integrating with specialized testing tools for more complex scenarios.

- **Maintaining Idempotency**: Ensure all converted scripts maintain idempotency.
  - Mitigation: Use Ansible's built-in idempotent modules instead of commands where possible.

- **Certificate Management**: Ensuring proper certificate generation and management.
  - Mitigation: Use Ansible's crypto modules for certificate operations.

### Migration Order

1. **chef-automate-deployment** (Medium complexity, high value)
   - Convert Bash scripts to Ansible roles for deploying infrastructure components
   - Implement Ansible Vault for credential management

2. **compliance-tests** (Medium complexity)
   - Convert InSpec tests to Ansible assertions or integrate with a compliance tool

3. **website-https-configuration** and **poodle-vulnerability-fix** (Low complexity)
   - Refactor existing Ansible playbooks into roles following best practices
   - Implement proper variable management
   - Ensure idempotency for all tasks

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or a compatible Linux distribution.
2. The deployment will continue to use self-signed certificates rather than certificates from a trusted CA.
3. The current security posture (TLSv1.2, disabled root SSH login) is sufficient and doesn't need enhancement.
4. The migration will not involve significant changes to the application architecture.
5. The Chef Automate and Chef Infra Server deployment will be replaced with equivalent Ansible functionality.
6. Test Kitchen will be replaced with Molecule or another Ansible-native testing framework.
7. The current Apache version (2.4.41-4ubuntu3.10) will continue to be the target version.