# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on compliance automation and Chef server deployment. The migration scope is relatively small, with two main components:

1. A Chef InSpec compliance testing framework used alongside Ansible playbooks
2. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks. The primary focus will be on replacing Chef InSpec tests with Ansible-native solutions while preserving the existing Ansible playbooks.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that addresses SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **inspec_compliance_tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS content verification, SSL protocol validation, SSH root login security check

- **chef_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef server installation, user and organization creation, system configuration

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Will need to be replaced with Ansible-native testing framework.
- `index.html`: Simple HTML test file used in the website deployment. Can be preserved as-is.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For infrastructure testing: Use the `ansible.builtin.assert` module or Molecule for testing
  - For compliance testing: Consider migrating to OpenSCAP with Ansible or Ansible's `assert` module
  - For continuous compliance: Consider implementing Ansible Automation Platform with built-in compliance capabilities

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality but is designed specifically for Ansible

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains enabled and older protocols remain disabled
  - Maintain proper certificate generation and configuration

- **SSH Security**: Preserve the SSH root login restrictions from the InSpec tests
  - Implement equivalent checks using Ansible's assert module or OpenSCAP

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup-automate scripts (username, password)
  - Recommendation: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions
  - Mitigation: Create a mapping document for each InSpec resource and its Ansible equivalent

- **Chef Server Deployment**: The Chef server deployment scripts need to be completely replaced
  - Mitigation: Create Ansible roles for infrastructure management that were previously handled by Chef

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format
   - Only need to update testing framework integration

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Medium complexity
   - Convert to Ansible-native testing solutions
   - Ensure all compliance checks are preserved

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity
   - These need complete replacement with Ansible roles for infrastructure management
   - Consider if Chef Automate/Server is still needed or if it can be replaced with Ansible Automation Platform

### Assumptions

1. The primary purpose of this repository is for demonstration/examples rather than production use
2. The InSpec tests are used for compliance verification of infrastructure provisioned by Ansible
3. The Chef server deployment scripts are separate from the main Ansible+InSpec workflow
4. No external Chef cookbooks or complex Chef-specific features are in use
5. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only
7. There are no additional Chef-specific files not visible in the repository structure
8. The migration will preserve the same level of security compliance checking