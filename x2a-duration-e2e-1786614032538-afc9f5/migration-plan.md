# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment of Ansible playbooks and Chef InSpec tests, along with Chef Automate/Chef Infra Server setup scripts. The migration scope is relatively small, focusing primarily on:

1. Preserving the compliance testing functionality currently provided by Chef InSpec
2. Maintaining the existing Ansible playbook functionality
3. Replacing Chef Automate/Chef Infra Server deployment scripts with Ansible equivalents

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a single engineer. The primary challenge will be replacing Chef InSpec tests with equivalent Ansible-native solutions.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and port availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configurations
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (STIG)

- **automate_deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash + Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef_server_deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash + Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Will need to be replaced with Ansible-native testing framework.
- `chef-and-ansible/index.html`: Static HTML file used in the website deployment. Can be preserved as-is.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use [ansible-lint](https://ansible-lint.readthedocs.io/) for static analysis
  - Option 2: Use [Molecule](https://molecule.readthedocs.io/) for Ansible role testing
  - Option 3: Use [testinfra](https://testinfra.readthedocs.io/) for server validation testing
  - Option 4: Convert InSpec tests to Ansible assert modules within playbooks

- **Test Kitchen**: Replace with Molecule for Ansible role testing and validation

- **Chef Automate/Infra Server**: Replace with:
  - [AWX](https://github.com/ansible/awx) (open source version of Ansible Tower)
  - Ansible Automation Platform (commercial)
  - GitLab CI/CD or Jenkins for automation orchestration

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure the Ansible migration maintains:
  - Self-signed certificate generation
  - Proper SSL protocol configuration (TLSv1.2 only)
  - Appropriate file permissions for certificates

- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Ensure SSH root login remains disabled
  - Maintain compliance with security standards (STIG)
  - Consider implementing these checks as Ansible assert tasks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets in deploy scripts (username/password combinations)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing mechanisms:
  - Challenge: InSpec provides a domain-specific language for compliance testing
  - Mitigation: Use testinfra with Python for more complex tests, or implement simple checks using Ansible's assert module

- **Compliance Reporting**: Chef InSpec provides compliance reporting capabilities:
  - Challenge: Replicating compliance reporting functionality in Ansible
  - Mitigation: Consider integrating with tools like OpenSCAP or Compliance as Code frameworks

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format
   - Review and update as needed for best practices
   - Add documentation

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Medium complexity
   - Convert to testinfra or Ansible assert modules
   - Validate functionality matches original tests

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Medium complexity
   - Create Ansible playbooks to replace bash scripts
   - Implement Ansible Vault for credential storage

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment
2. The Chef Automate and Chef Infra Server deployment scripts are examples and not actively used in production
3. The security configurations (especially passwords in scripts) are examples and not used in production
4. The migration will maintain the same level of security validation currently provided by InSpec
5. The target environment will continue to be Ubuntu 20.04 or compatible systems
6. The self-signed certificates are acceptable for the use case and don't need to be replaced with CA-signed certificates