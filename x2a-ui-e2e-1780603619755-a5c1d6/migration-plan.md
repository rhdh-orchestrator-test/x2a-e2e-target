# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on compliance automation and Chef server deployment. The migration scope is relatively small, with two main components:

1. A Chef InSpec compliance testing framework used alongside Ansible playbooks
2. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **LOW to MEDIUM** as most components are already in Ansible format or are simple shell scripts that can be converted to Ansible roles. The estimated timeline for migration is **1-2 weeks** for a single developer.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **inspec-compliance-tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH hardening
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH root login testing

- **chef-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used in the website deployment

### Target Details

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Convert InSpec tests to Ansible assert modules
  - Option 2: Use Molecule for Ansible role testing
  - Option 3: Maintain InSpec as a separate testing tool but invoke it from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain the same level of Apache security configuration

- **SSH Hardening**: The SSH root login restrictions tested by InSpec must be implemented in the Ansible equivalent
  - Create an Ansible task to enforce PermitRootLogin configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible's testing capabilities may require additional modules or external tools
  - Mitigation: Consider using Ansible's assert module combined with command/shell modules to perform equivalent tests

- **Chef Server Deployment**: The Chef server deployment scripts need to be converted to Ansible roles
  - Mitigation: Create an Ansible role that performs the same steps as the bash scripts, using Ansible modules for package installation and configuration

### Migration Order

1. **website-https playbook** (already in Ansible format, low risk)
2. **poodle-fix playbook** (already in Ansible format, low risk)
3. **chef-deployment scripts** (convert bash scripts to Ansible roles, medium complexity)
4. **inspec-compliance-tests** (convert to Ansible testing framework, highest complexity)

### Assumptions

1. The current setup uses Chef InSpec primarily for testing, not for configuration management
2. The repository is used for demonstration purposes rather than production deployment
3. The hardcoded credentials in the setup scripts are not used in production environments
4. The Test Kitchen configuration is used for local development and testing only
5. The target environment will continue to be Ubuntu 20.04 or compatible systems
6. There are no external dependencies or integrations not visible in the repository
7. The migration will maintain the same level of security testing and compliance checks