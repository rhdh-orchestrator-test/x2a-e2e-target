# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and verify secure web server configurations. The migration scope is relatively small, focusing on two main components:

1. Ansible playbooks for deploying and configuring Apache web servers with HTTPS
2. Chef InSpec tests for verifying compliance and security of the deployed configurations

The migration complexity is **LOW** as most of the content is already in Ansible format. The primary task will be to replace Chef InSpec tests with equivalent Ansible testing mechanisms (such as ansible-test or molecule). Estimated timeline: **1-2 weeks** for a single developer to complete the migration, test, and document the new approach.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used as a test page for the web server. Can be directly incorporated into Ansible as a template.

### Target Details

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible testing solutions:
  - Option 1: Use ansible-test for integration testing
  - Option 2: Use Molecule for scenario-based testing
  - Option 3: Implement custom testing using Ansible assert modules

- **Test Kitchen (latest)**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using kitchen-ansible if preferred

- **Vagrant (latest)**: Can be retained as the development/testing platform or replaced with containers for faster testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
  - Migration approach: Convert the existing Ansible task in poodle_fix.yml to an Ansible role with appropriate variables

- **Self-signed Certificates**: The current implementation generates self-signed certificates
  - Migration approach: Create an Ansible role for certificate management that can be extended to support proper CA-signed certificates

- **SSH Security**: The SSH security tests need to be converted to Ansible assertions
  - Migration approach: Create Ansible tasks that check the same SSH configuration parameters

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration approach: Move credentials to Ansible Vault

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible verification
  - Mitigation: Use Ansible's assert module with appropriate conditions to verify the same conditions
  - Example: Replace InSpec port check with Ansible's wait_for module and assert

- **Test Kitchen Workflow**: Replacing the Test Kitchen workflow with an Ansible-native testing approach
  - Mitigation: Implement Molecule testing framework which is designed for Ansible roles

### Migration Order

1. **website_https.yml** (Priority 1): Convert to Ansible role with proper variable parameterization
2. **poodle_fix.yml** (Priority 1): Incorporate into the web server role as a security hardening task
3. **InSpec Tests** (Priority 2): Convert to Ansible-based tests using assert or Molecule
4. **Chef Automate Scripts** (Priority 3): Convert deployment scripts to Ansible roles for infrastructure management

### Assumptions

1. The current implementation is used primarily for testing and demonstration purposes, not production deployment
2. The self-signed certificates are acceptable for the use case
3. The hardcoded values in the deployment scripts are for demonstration only
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The SSH security profile is relevant to the target systems
6. The migration does not need to include Chef Automate functionality, only the deployment automation
7. Test Kitchen is only used for development/testing and not for production deployments