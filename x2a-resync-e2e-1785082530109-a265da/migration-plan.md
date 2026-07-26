# MIGRATION FROM ANSIBLE WITH CHEF INSPEC TO ANSIBLE

## Executive Summary

This repository contains a small set of Ansible playbooks with Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the existing Ansible playbooks to a more structured Ansible project while preserving the compliance testing capabilities provided by Chef InSpec.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium
**Primary Technologies**: Ansible playbooks, Chef InSpec tests

## Module Migration Plan

This repository contains Ansible playbooks with Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS website configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML file for testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain InSpec for compliance testing but integrate with Ansible's native testing framework
  - Migration strategy: Convert InSpec tests to Ansible test modules where possible, or maintain InSpec as a separate testing tool
  
- **Test Kitchen with Vagrant**: Replace with Ansible-native testing frameworks
  - Migration strategy: Use Molecule for Ansible role testing with the same Vagrant driver

- **Chef Automate/Server**: Evaluate if these components are needed or if they can be replaced with Ansible Tower/AWX
  - Migration strategy: If Chef Automate is used primarily for compliance reporting, consider migrating to Ansible Tower with compliance scanning

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with SSL/TLS. Ensure proper certificate management in the Ansible migration.
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented

- **SSH Hardening**: InSpec tests verify SSH security configurations.
  - Migration approach: Implement equivalent Ansible tasks to enforce SSH security settings and maintain compliance tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Integration**: Maintaining InSpec tests while migrating to pure Ansible
  - Mitigation strategy: Use Ansible's `community.general.inspec` module to run InSpec tests as part of Ansible playbooks

- **Certificate Management**: Ensuring proper SSL/TLS certificate handling
  - Mitigation strategy: Use Ansible's native OpenSSL modules and consider integration with certificate management systems

- **Compliance Reporting**: If compliance reporting is needed, determine how to replace Chef Automate's functionality
  - Mitigation strategy: Evaluate Ansible Tower/AWX compliance scanning capabilities or integrate with third-party compliance tools

### Migration Order

1. **website-https playbook** (low risk, already Ansible)
   - Convert to Ansible role structure
   - Maintain InSpec tests

2. **poodle-fix playbook** (low risk, already Ansible)
   - Convert to Ansible role structure
   - Integrate with website-https role

3. **Chef deployment scripts** (medium complexity)
   - Evaluate if Chef components are needed
   - If needed, convert bash scripts to Ansible playbooks for Chef deployment
   - If not needed, document replacement strategy with Ansible Tower/AWX

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment.

2. The Chef Automate and Chef Server deployment scripts are examples and may not be actively used in production.

3. The target environment is Ubuntu 20.04 running on Vagrant VMs for testing purposes.

4. The repository is primarily educational/demonstrational rather than a production infrastructure codebase.

5. There is no complex dependency structure between the components, making migration relatively straightforward.

6. The InSpec tests are valuable and should be preserved in some form during migration.

7. No external inventory or variable files are being used, suggesting a simple deployment model.

8. No complex secrets management is implemented in the current codebase.