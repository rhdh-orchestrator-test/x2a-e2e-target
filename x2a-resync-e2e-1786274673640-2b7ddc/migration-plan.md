# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment of Chef InSpec for compliance testing and Ansible playbooks for configuration management. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec compliance tests to Ansible-native solutions
2. Consolidating existing Ansible playbooks
3. Migrating Chef Automate and Chef Infra Server deployment scripts to Ansible

The repository appears to be primarily a demonstration environment showing how Chef InSpec can work alongside Ansible for compliance automation. The migration complexity is **LOW** with an estimated timeline of 1-2 weeks for a single engineer to complete.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and port availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH security compliance (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, CCI compliance mapping, STIG validation

- **automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Simple HTML template for the website deployed by the Ansible playbook

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly defined in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml as the driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - For website_https_verify.rb: Use Ansible URI module with assert for HTTP checks and community.crypto.openssl_certificate_info for SSL validation
  - For ssh_profile.rb: Use ansible-lint security rules or OpenSCAP Ansible integration

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with AWX/Ansible Tower or other Ansible management platform

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in poodle_fix.yml
  - Approach: Use ansible.builtin.lineinfile or ansible.builtin.template with proper SSL configuration
  
- **SSH Hardening**: Maintain the SSH security controls verified by ssh_profile.rb
  - Approach: Create equivalent Ansible tasks to configure SSH properly

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **Compliance Testing**: Converting Chef InSpec tests to equivalent Ansible validation
  - Mitigation: Use Ansible assert module combined with command/shell modules to run validation checks
  - Consider ansible-lint or OpenSCAP integration for compliance validation

- **Self-signed Certificates**: Maintaining proper SSL certificate generation
  - Mitigation: Use Ansible's crypto modules (community.crypto collection) for certificate operations

### Migration Order

1. **website_https.yml** (Priority 1 - already Ansible, low risk)
   - Minimal changes needed, just code review and potential refactoring

2. **poodle_fix.yml** (Priority 1 - already Ansible, low risk)
   - Minimal changes needed, just code review and potential refactoring

3. **InSpec Tests** (Priority 2 - moderate complexity)
   - Convert to Ansible-native testing using assert, uri, and command modules
   - Alternatively, integrate with ansible-lint or OpenSCAP

4. **Chef Deployment Scripts** (Priority 3 - higher complexity)
   - Convert bash scripts to Ansible roles for deploying management platforms
   - Consider AWX/Tower as replacement for Chef Automate

### Assumptions

1. The repository is primarily for demonstration purposes showing Chef InSpec with Ansible integration
2. No actual Chef cookbooks or recipes are in use, only InSpec for compliance testing
3. The target environment is Ubuntu 20.04 running on Vagrant VMs
4. The deployment scripts are intended for lab/demo environments (based on default passwords and domain names)
5. No complex state management or data bags are in use
6. No external dependencies beyond standard Ansible modules and Chef InSpec
7. The migration will maintain the same level of security validation currently provided by InSpec