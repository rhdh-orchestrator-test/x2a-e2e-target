# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server setup. The migration scope is relatively small, focusing on two main components:

1. Chef InSpec tests used alongside Ansible for compliance verification
2. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is **LOW to MEDIUM** as most of the repository already contains Ansible playbooks. The primary focus will be on replacing Chef InSpec tests with Ansible-native solutions and converting Chef server deployment scripts to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **inspec_compliance_tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH root login security check

- **chef_server_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash/Chef
    - Key Features: Chef server installation, user and organization creation, system configuration

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Will need to be replaced with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing the web server deployment. Can be reused as-is in the Ansible migration.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - For compliance testing: Use Ansible's `assert` module or migrate to Ansible Lint
  - For security scanning: Consider integrating with OpenSCAP or using Ansible security roles from Ansible Galaxy

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that:
  - Set hostname
  - Configure system parameters
  - Install and configure equivalent functionality (Ansible AWX/Tower or other configuration management tools)

### Security Considerations

- **SSL Configuration**: The current implementation configures Apache with TLS 1.2 and disables older protocols. Migration should maintain or enhance this security posture.
  - Migration approach: Use Ansible's `apache2_module` and `lineinfile` modules to achieve the same configuration

- **SSH Hardening**: InSpec tests verify that SSH root login is disabled.
  - Migration approach: Create an Ansible role for SSH hardening that implements the same controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification methods.
  - Mitigation: Use Ansible's `assert` module with appropriate conditions or consider using the `community.general.test_command` module

- **Chef Server Functionality**: Replacing Chef Server functionality if required.
  - Mitigation: Evaluate if Ansible AWX/Tower can provide equivalent functionality or if a simpler Git-based workflow is sufficient

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format; may need minor updates for best practices
2. **InSpec Tests**: Convert to Ansible-native testing solutions
3. **Chef Server Deployment Scripts**: Create equivalent Ansible playbooks for server deployment

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment.
2. The Chef server deployment scripts are examples and not actively used in production environments.
3. There are no external dependencies or integrations not visible in the repository.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be replaced with secure alternatives.
6. The self-signed certificates in the web server setup are for testing only and would be replaced with proper certificates in production.