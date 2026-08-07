# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests that are used together to deploy and validate secure web applications. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, with only a few Ansible playbooks and InSpec test files to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as the Ansible components can be largely preserved while replacing the InSpec testing with Ansible-native solutions.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that validates SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login validation, compliance with security standards (STIG)

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

- `kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Static HTML file used in the website deployment. Can be directly used in Ansible without modification.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic validation
  - Option 2: Implement Ansible Molecule for comprehensive testing
  - Option 3: Use ansible-lint for static code analysis

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that either:
  - Option 1: Deploy alternative compliance tools like OpenSCAP
  - Option 2: Deploy Ansible AWX/Tower for centralized management

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Approach: Preserve the existing Ansible tasks that enforce TLSv1.2 and disable SSLv3

- **SSH Hardening**: The SSH security checks in ssh_profile.rb need to be implemented in Ansible
  - Approach: Create Ansible tasks that configure and validate SSH settings using the `lineinfile` module and `assert` for validation

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **Compliance Testing**: Replacing Chef InSpec's declarative testing approach with Ansible equivalents
  - Mitigation: Use Ansible's `assert` module combined with `command`/`shell` modules to run validation checks
  - Consider implementing custom Ansible modules for complex compliance checks

- **Test Automation**: Replacing Test Kitchen with an Ansible-native testing framework
  - Mitigation: Implement Ansible Molecule for test automation with similar capabilities

- **Deployment Scripts**: Converting the Chef Automate and Chef Server deployment scripts to Ansible
  - Mitigation: Create Ansible roles that perform equivalent setup steps, potentially using community roles as a starting point

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they can be largely preserved
2. **Testing Framework** - Replace Test Kitchen with Ansible Molecule
3. **InSpec Tests** - Convert InSpec tests to Ansible assertions or Molecule verifiers
4. **Deployment Scripts** - Replace Chef Automate/Server deployment scripts with Ansible equivalents

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependencies while preserving or enhancing security validation capabilities
2. The existing Ansible playbooks are functioning correctly and follow best practices
3. There is no requirement to maintain backward compatibility with Chef tools
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. The self-signed certificates are for testing/development purposes only
6. The deployment scripts contain default/example credentials that will be replaced in production
7. The migration will include updating documentation to reflect the new all-Ansible approach