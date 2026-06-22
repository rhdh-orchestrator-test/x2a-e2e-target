# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate a secure web server configuration. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.
**Complexity**: Low to Medium - The InSpec tests are straightforward, but ensuring equivalent test coverage in Ansible will require careful implementation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that validates the HTTPS website deployment
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file for the web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use the `ansible.builtin.assert` module for basic validation
  - Option 2: Implement Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source alternatives:
  - AWX (open-source upstream of Ansible Tower)
  - Ansible Semaphore
  - Ansible Automation Platform (commercial)

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
  - Migration approach: Preserve the existing Ansible task that modifies the Apache SSL configuration

- **SSH Security**: The SSH root login check must be maintained
  - Migration approach: Convert the InSpec control to an Ansible task that checks the SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts: The Chef deployment scripts contain hardcoded passwords that should be moved to Ansible Vault
  - SSL certificates: Self-signed certificates are generated as part of the playbook execution

### Technical Challenges

- **Compliance Testing**: Chef InSpec provides a declarative syntax for compliance testing that doesn't have a direct equivalent in Ansible
  - Mitigation: Use a combination of Ansible assert modules and custom scripts to achieve similar validation

- **Test Coverage**: Ensuring that the Ansible-native tests provide the same level of coverage as the InSpec tests
  - Mitigation: Create a test coverage matrix to map InSpec tests to their Ansible equivalents

- **Deployment Scripts**: Converting the Chef deployment scripts to Ansible requires understanding of Chef Automate architecture
  - Mitigation: Research Ansible roles for deploying similar infrastructure management tools

### Migration Order

1. **website_https_verify** (low risk, high value): Convert InSpec tests to Ansible assertions
2. **ssh_profile** (low risk, medium value): Convert InSpec control to Ansible task
3. **chef-automate-deployment** and **chef-server-deployment** (high complexity): Create Ansible playbooks to replace these deployment scripts

### Assumptions

1. The existing Ansible playbooks (`website_https.yml` and `poodle_fix.yml`) can be used as-is without modification
2. The target environment will continue to be Ubuntu 20.04 or compatible
3. The deployment scripts for Chef Automate and Chef Server are intended to be migrated to equivalent functionality in Ansible
4. The security compliance requirements (STIG references in the SSH profile) need to be maintained in the Ansible implementation
5. No external data sources or APIs are being used that would require special handling
6. The migration does not need to address scaling concerns as the current implementation appears to target single-node deployments
7. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure alternatives in the Ansible implementation