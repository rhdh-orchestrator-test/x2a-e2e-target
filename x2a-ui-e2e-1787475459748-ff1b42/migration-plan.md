# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks designed to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation. The repository also includes scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing on converting the existing Ansible playbooks to a more structured Ansible format and replacing Chef InSpec tests with Ansible-native solutions.

**Estimated Timeline**: 1-2 weeks for a single engineer, including testing and documentation.

**Complexity**: Low to Medium - The existing Ansible playbooks are straightforward, but proper test conversion requires careful attention.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to address POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a website
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML content for the website deployment

## Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace InSpec tests with equivalent Ansible assert modules or molecule tests
  - For compliance testing, consider using ansible-lint with custom rules or OpenSCAP integration

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - ansible-navigator for playbook development and testing

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for orchestration and management
  - Ansible Content Collections for configuration management
  - Compliance automation using ansible-lint or OpenSCAP

### Security Considerations

- **SSL Configuration**: The current playbooks configure SSL for Apache. Migration should:
  - Maintain or improve the SSL security settings
  - Update the SSL protocol settings to current best practices
  - Consider using Let's Encrypt instead of self-signed certificates

- **SSH Hardening**: The InSpec profile checks SSH security. Migration should:
  - Implement equivalent SSH hardening in Ansible
  - Maintain compliance with security standards referenced in the InSpec profile (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Current implementation has hardcoded credentials in the Chef server deployment scripts
  - Migration should use Ansible Vault for storing sensitive information like passwords

### Technical Challenges

- **Test Conversion**: Converting InSpec tests to Ansible-native testing requires careful mapping of test assertions
  - Mitigation: Use Ansible assert module and custom modules where needed

- **Compliance Validation**: Ensuring the same level of compliance validation without InSpec
  - Mitigation: Implement equivalent checks using ansible-lint custom rules or OpenSCAP

- **Infrastructure Setup**: Replacing Chef Automate/Infra Server with equivalent Ansible infrastructure
  - Mitigation: Document AWX/Tower setup procedures to replace Chef server functionality

### Migration Order

1. **website_https.yml** (Priority 1): Core web server configuration playbook
2. **poodle_fix.yml** (Priority 1): Security-related playbook that should be migrated early
3. **InSpec Tests** (Priority 2): Convert tests to Ansible-native testing
4. **Chef Deployment Scripts** (Priority 3): Replace with AWX/Tower setup procedures

### Assumptions

1. The primary goal is to consolidate on Ansible and remove Chef dependencies
2. Compliance testing is a critical requirement that must be maintained
3. The current infrastructure is relatively simple and doesn't have complex Chef-specific features
4. The migration will maintain or improve the current security posture
5. Test Kitchen is only used for development/testing and not in production
6. The hardcoded credentials in deployment scripts are for demonstration purposes only
7. The target environment will continue to be Ubuntu 20.04 or compatible systems
8. The migration will include documentation for setting up equivalent infrastructure