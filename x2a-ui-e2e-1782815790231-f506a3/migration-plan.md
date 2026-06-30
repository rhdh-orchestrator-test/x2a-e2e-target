# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, with two main components: (1) Ansible playbooks with InSpec tests and (2) Chef Automate/Infra Server deployment scripts. The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling older SSL protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **inspec_compliance_tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol validation, SSH root login security check

- **chef_automate_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with on-premises focus

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Integrate with Ansible Automation Platform's compliance capabilities
  - Option 3: Convert InSpec tests to Ansible assert modules or custom modules

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - ansible-test for collection testing

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in poodle_fix.yml
  - Ensure TLSv1.2 remains enforced
  - Consider upgrading to also include TLSv1.3 support

- **SSH Hardening**: Maintain the SSH root login restrictions verified by InSpec tests
  - Convert the InSpec control to equivalent Ansible assertions or molecule tests

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts need to be moved to Ansible Vault
  - Count: 3 credentials detected (username, useremail, userpassword)

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native verification methods
  - Mitigation: Use assert module or custom modules to perform equivalent checks
  - Consider ansible.builtin.uri module for HTTP/HTTPS checks

- **Chef Automate Deployment**: Replacing Chef Automate deployment with equivalent infrastructure
  - Mitigation: Determine if Chef Automate is still needed or if it can be replaced with Ansible Automation Platform

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - Review and optimize existing Ansible code
   - Update to follow current Ansible best practices

2. **poodle_fix.yml** (low risk, already Ansible)
   - Review and optimize existing Ansible code
   - Consider merging with website_https.yml as a role

3. **InSpec Tests** (moderate complexity)
   - Convert to Ansible assert statements or molecule tests
   - Ensure all compliance checks are maintained

4. **Chef Automate Deployment Scripts** (high complexity)
   - Convert bash scripts to Ansible roles for infrastructure deployment
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are essential and their functionality must be preserved in the migration
3. The Chef Automate and Chef Infra Server deployment may be replaced with Ansible Automation Platform
4. The target environment will continue to be Ubuntu 20.04 or newer
5. Vagrant will continue to be used for development/testing environments
6. The hardcoded credentials in deployment scripts are not for production use
7. The SSL/TLS security requirements will remain the same or become more stringent