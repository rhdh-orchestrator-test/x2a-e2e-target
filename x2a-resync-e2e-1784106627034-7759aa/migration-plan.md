# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the Chef InSpec tests to Ansible-native testing solutions while maintaining the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium
**Primary Focus**: Converting InSpec tests to Ansible-native testing solutions

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities (POODLE) by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Sample HTML file used in the website deployment. Can be maintained as-is or incorporated into Ansible templates.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the scripts mention "on-prem or cloud VM" suggesting flexibility

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - **Option 1**: Use Ansible's `assert` module for basic testing
  - **Option 2**: Integrate with Molecule for more comprehensive testing
  - **Option 3**: Use ansible-lint for static analysis and best practices enforcement

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality to Test Kitchen but is designed specifically for Ansible

- **Chef Automate/Infra Server**: Replace with Ansible Tower/AWX or other Ansible management platform
  - Consider migrating to Ansible Tower/AWX for web UI, role-based access control, and job scheduling
  - Alternatively, use GitLab CI/CD or Jenkins for Ansible playbook execution

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains enabled and older protocols remain disabled
  - Consider updating to also include TLSv1.3 support

- **SSH Hardening**: The SSH security checks in ssh_profile.rb need to be maintained
  - Convert the InSpec controls to Ansible assertions or Molecule tests
  - Maintain compliance with the security standards referenced (SRG-OS-000112, RHEL-08-000227)

- **Vault/secrets management**: 
  - The deploy scripts contain hardcoded credentials (username, password) that should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbook; consider using Ansible Vault for storing private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module with carefully crafted conditions that match InSpec's intent
  - Consider using community.general.xml and community.crypto modules for specific tests

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs to be replicated
  - Mitigation: Consider integrating with tools like Ansible Tower/AWX for reporting or export test results to a format that can be consumed by compliance dashboards

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible
  - Mitigation: Create an Ansible role that performs equivalent setup of a centralized configuration management system (Ansible Tower/AWX)

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (already in Ansible format, no migration needed)
2. **website_https_verify.rb** (convert InSpec tests to Ansible assertions or Molecule tests)
3. **ssh_profile.rb** (convert InSpec compliance profile to Ansible security role with tests)
4. **deploy-automate.sh** and **deploy-chef-server.sh** (convert to Ansible playbooks for infrastructure setup)

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance testing
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't need functional changes
3. The deployment environment will continue to be Ubuntu 20.04 or compatible
4. The team has expertise in Ansible but wants to eliminate the Chef dependency
5. There's no requirement to maintain backward compatibility with Chef InSpec
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be properly secured in the migrated solution
7. The self-signed certificates are acceptable for the environment (not production)
8. The migration doesn't need to address scaling concerns as the examples appear to be for single-node deployments