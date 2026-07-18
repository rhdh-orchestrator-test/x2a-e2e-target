# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for compliance verification
3. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing capabilities while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Ansible playbook for configuring Apache with HTTPS, self-signed certificates, and a basic website
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-ssl-fix**:
    - Description: Ansible playbook for remediating SSL POODLE vulnerability by disabling SSLv3 and enabling TLSv1.2
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-https-compliance**:
    - Description: Chef InSpec profile for verifying HTTPS website functionality and security
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: Port listening tests, HTTPS content verification, SSL protocol security checks

- **ssh-security-compliance**:
    - Description: Chef InSpec profile for verifying SSH security configuration
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but deployment scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Keep InSpec but integrate with Ansible using the ansible_inspec module
  - Option 3: Convert InSpec tests to equivalent Ansible assert tasks

- **Test Kitchen**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing infrastructure
  - Option 2: Use simple Vagrant or Docker-based testing with Ansible

- **Chef Automate/Server**: Replace with Ansible automation platform:
  - Option 1: Migrate to AWX/Ansible Tower
  - Option 2: Use GitLab CI/CD with Ansible
  - Option 3: Use GitHub Actions with Ansible

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Approach: Convert to Ansible role with appropriate handlers and idempotent tasks

- **SSH Security**: The SSH compliance checks must be preserved
  - Approach: Convert InSpec tests to Ansible assert tasks or maintain InSpec tests but run them from Ansible

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **Compliance Testing**: The primary challenge is maintaining the compliance testing capabilities currently provided by InSpec
  - Mitigation: Either keep InSpec and integrate with Ansible, or convert tests to equivalent Ansible assertions
  - Consider using ansible-lint for static code analysis of security issues

- **Chef Automate Functionality**: Chef Automate provides compliance reporting that needs an equivalent in Ansible
  - Mitigation: Consider AWX/Tower for reporting or integrate with a compliance tool like OpenSCAP

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate testing
  - Mitigation: Replace with Ansible Molecule or a simple Vagrant/Docker setup with Ansible provisioning

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to a proper Ansible role structure

2. **poodle-ssl-fix** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Integrate with the website-https role

3. **InSpec Tests** (moderate complexity)
   - Decide on testing strategy (keep InSpec or migrate to Ansible native testing)
   - Implement chosen strategy

4. **Chef Deployment Scripts** (high complexity)
   - Create Ansible playbooks to replace Chef Automate/Server deployment
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is demonstrating Chef InSpec with Ansible rather than production deployment
2. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
3. There are no external dependencies or integrations not visible in the repository
4. The deployment scripts are examples and not used in production (they contain hardcoded credentials)
5. The compliance testing requirements will remain the same after migration
6. No custom Chef resources or complex Chef-specific functionality is being used
7. The migration will consolidate all infrastructure provisioning into Ansible while maintaining or replacing the compliance testing capabilities