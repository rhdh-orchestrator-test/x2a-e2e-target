# MIGRATION FROM CHEF AND BASH TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The repository also includes bash scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks and ensuring the existing Ansible playbooks follow best practices. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already Ansible-compatible or can be easily converted.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **inspec_tests**:
    - Description: Chef InSpec tests for verifying HTTPS functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTPS content verification, SSL protocol verification, SSH configuration compliance

- **chef_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used for testing web server functionality

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic tests
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the ansible-lint tool for static analysis
  - Option 4: Consider maintaining InSpec as a complementary tool if its specific compliance features are required

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or maintain Test Kitchen with the kitchen-ansible plugin if preferred

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains the minimum protocol version
  - Consider updating to also include TLSv1.3 support

- **SSH Hardening**: The SSH compliance profile must be maintained
  - Convert the InSpec SSH profile to equivalent Ansible assertions or molecule tests
  - Ensure root login remains disabled

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules
  - Consider using Ansible's uri module for HTTP/HTTPS testing

- **Chef Server Deployment**: The Chef server deployment scripts need to be converted to Ansible roles
  - Mitigation: Create an Ansible role that performs the same server setup and configuration
  - Consider whether Chef Automate/Server is still needed or if it should be replaced with Ansible Tower/AWX

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Review and refactor according to Ansible best practices
2. **poodle_fix.yml** (low risk, already Ansible): Review and refactor according to Ansible best practices
3. **InSpec Tests** (moderate complexity): Convert to Ansible-native testing framework
4. **Chef Deployment Scripts** (high complexity): Convert to Ansible roles for server deployment

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as indicated in the README.
2. The existing Ansible playbooks are functional and don't require significant changes beyond best practices refactoring.
3. The target environment will continue to be Ubuntu 20.04 or compatible systems.
4. The deployment of Chef Automate and Chef Infra Server may still be required after migration, rather than being replaced entirely by Ansible Tower/AWX.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only and would be replaced with secure credential management in production.
6. The Test Kitchen configuration is used primarily for testing and demonstration, not for production deployments.
7. The self-signed certificates are for testing purposes and would be replaced with proper certificates in production.