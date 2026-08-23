# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec and Ansible configurations that need to be migrated to a pure Ansible solution. The repository appears to be a demonstration of how Chef InSpec can be used alongside Ansible for compliance automation, as indicated by the README in the chef-and-ansible directory.

The migration scope is relatively small, with only a few Ansible playbooks and Chef InSpec test files. The complexity is low to moderate, as the existing Ansible playbooks can be largely reused, while the Chef InSpec tests need to be converted to Ansible-compatible testing frameworks. The estimated timeline for this migration is 1-2 weeks, depending on the complexity of the InSpec tests and the desired level of test coverage in the new Ansible solution.

## Module Migration Plan

This repository contains a mix of Chef InSpec and Ansible that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to address the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance tagging (STIG, CCI)

- **automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used in the website deployment. Can be directly used in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use community.general.test_module for test-driven infrastructure

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source alternatives:
  - AWX (open-source upstream of Ansible Tower)
  - Ansible Automation Platform (commercial)

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL/TLS protocols are enforced in the migrated solution.
  - Migration approach: Maintain the same SSL hardening but use Ansible's `ansible.builtin.lineinfile` or templates instead of `replace` module.

- **SSH Hardening**: The InSpec tests check for SSH root login restrictions. Ensure these security checks are maintained.
  - Migration approach: Convert InSpec tests to Ansible assertions or Molecule tests.

- **Vault/secrets management**: 
  - Hardcoded credentials in the deployment scripts (username, password) should be moved to Ansible Vault.
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks may require additional logic.
  - Mitigation: Use Ansible's assert module for simple tests, and consider Molecule for more complex testing scenarios.

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs to be replicated in Ansible.
  - Mitigation: Consider integrating with tools like OpenSCAP or using Ansible's callback plugins for reporting.

### Migration Order

1. **website_https playbook** (low risk, already Ansible)
   - Minimal changes needed, just review and optimize

2. **poodle_fix playbook** (low risk, already Ansible)
   - Minimal changes needed, just review and optimize

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible assertions or Molecule tests

4. **Chef deployment scripts** (high complexity)
   - Convert to Ansible roles for infrastructure setup

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the same level of compliance testing.
2. The existing Ansible playbooks are functional and follow best practices.
3. The deployment scripts for Chef Automate and Chef Infra Server will be replaced with equivalent Ansible roles or playbooks.
4. The target environment will remain Ubuntu 20.04 on Vagrant VMs.
5. No specific compliance frameworks beyond those mentioned in the InSpec tests (STIG, CCI) are required.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be properly secured in the migrated solution.