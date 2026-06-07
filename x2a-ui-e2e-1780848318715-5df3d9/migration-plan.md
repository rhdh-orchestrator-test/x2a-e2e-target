# MIGRATION FROM CHEF AND BASH TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests, Ansible playbooks, and Bash scripts for deploying Chef infrastructure. The migration scope is relatively small, focusing on two main components:

1. Chef InSpec tests that validate Ansible-deployed configurations
2. Bash scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a single developer to complete. The primary focus will be on converting the Chef InSpec tests to Ansible-native testing solutions and transforming the Chef server deployment scripts into Ansible playbooks.

## Module Migration Plan

This repository contains Chef InSpec tests and Bash scripts that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing of web server configurations
    - Path: chef-and-ansible/
    - Technology: Chef InSpec + Ansible
    - Key Features: HTTPS configuration testing, SSL/TLS protocol validation, Apache web server configuration

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash
    - Key Features: Chef server installation, user and organization creation, system configuration

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec. Migration should replace with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure web server. Can be kept as-is or refactored into Ansible roles.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be kept as-is or integrated into a security role.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Should be converted to an Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Should be converted to an Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Determine if these components are still needed or if they can be replaced with:
  - Ansible AWX/Tower for web UI and job scheduling
  - Git repositories for configuration management
  - CI/CD pipelines for automation

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security improvements in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain certificate generation and management

- **SSH Hardening**: The ssh_profile.rb InSpec test checks for SSH root login restrictions
  - Implement equivalent checks in Ansible or integrate with ansible-lint

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely, potentially using ansible-vault or an external secrets manager

### Technical Challenges

- **Testing Framework Transition**: Moving from InSpec to Ansible-native testing
  - Challenge: InSpec provides specialized resources for testing (like ssl, http, port)
  - Mitigation: Use Ansible's uri module, wait_for module, and command module with appropriate assertions

- **Chef Server Deployment**: If Chef Server is still required in the environment
  - Challenge: Ensuring idempotent installation and configuration via Ansible
  - Mitigation: Use Ansible's package, service, and command modules with appropriate state checking

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format
   - Review and refactor into roles if needed
   - Add documentation

2. **Testing Framework** (InSpec tests): Moderate complexity
   - Convert InSpec tests to Ansible assertions or Molecule tests
   - Ensure equivalent coverage for security checks

3. **Chef Server Deployment Scripts**: Higher complexity
   - Convert Bash scripts to Ansible playbooks
   - Implement proper secret management
   - Add idempotence to ensure repeatable runs

### Assumptions

1. The Chef InSpec tests are used primarily for validation and compliance checking, not for active configuration management.
2. The deployment of Chef Automate/Infra Server is still required in the target environment.
3. The security requirements (TLS versions, SSH hardening) must be maintained in the migrated solution.
4. Test Kitchen is used for development and testing, not for production deployments.
5. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
6. No external dependencies or integrations beyond what's visible in the repository.
7. The hardcoded credentials in the setup scripts are for demonstration purposes and will be replaced with secure alternatives.