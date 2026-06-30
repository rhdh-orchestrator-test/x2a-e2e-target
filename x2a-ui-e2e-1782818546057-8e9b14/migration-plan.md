# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, with two main components: (1) Ansible playbooks with InSpec tests for a secure web server deployment, and (2) Chef Automate/Infra Server deployment scripts. The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **secure-web-server**:
    - Description: Ansible playbook for deploying a secure Apache web server with HTTPS configuration and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL/TLS configuration, virtual host setup, self-signed certificate generation

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook to remediate POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **compliance-tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port listening verification, HTTPS content verification, SSL/TLS protocol verification, SSH root login security check

- **chef-infrastructure**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts using Chef CLI tools
    - Key Features: Chef Automate deployment, Chef Server configuration, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `index.html`: Sample HTML file for web server testing
- `deploy-automate.sh`: Script to deploy Chef Automate and Chef Infra Server
- `deploy-chef-server.sh`: Script to deploy Chef Infra Server without Automate

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Convert InSpec tests to Ansible assert modules
  - Option 2: Use ansible-lint for static analysis
  - Option 3: Integrate with Molecule for testing
  - Option 4: Keep InSpec as a testing tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - Vagrant directly for local testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI, job scheduling, and inventory management
  - Git repositories for playbook/role storage
  - Consider Red Hat Satellite if in a Red Hat environment

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
  - Approach: Convert the existing Ansible replace module to equivalent tasks or use the community.general.apache2_module module

- **Self-signed Certificates**: The migration must preserve the secure generation of self-signed certificates
  - Approach: Use the existing openssl_* modules which are already Ansible-native

- **SSH Security Hardening**: Maintain the SSH root login restrictions
  - Approach: Convert InSpec tests to Ansible assert tasks or use ansible-lint security checks

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup scripts (username, password)
  - Approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible assertions or other testing frameworks
  - Mitigation: Use Ansible's assert module with appropriate conditions, or maintain InSpec as a separate testing tool called from Ansible

- **Chef Server Replacement**: Replacing Chef Server functionality with Ansible equivalents
  - Mitigation: Implement AWX/Tower for web UI and job scheduling, use Git for version control, and implement proper inventory management

- **Testing Framework**: Replacing Test Kitchen with Ansible-native testing
  - Mitigation: Implement Molecule for comprehensive testing of Ansible roles and playbooks

### Migration Order

1. **secure-web-server** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - Convert to Ansible role structure for better reusability

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Integrate with secure-web-server role
   - Implement as a separate security hardening role

3. **compliance-tests** (moderate complexity)
   - Convert InSpec tests to Ansible assertions or Molecule tests
   - Alternatively, keep InSpec and integrate with Ansible workflow

4. **chef-infrastructure** (high complexity)
   - Replace with AWX/Tower installation playbooks
   - Implement user/organization management through Ansible

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are intended to verify security compliance of the deployed web server
3. The Chef Automate/Infra Server scripts are for setting up a Chef infrastructure environment
4. No external dependencies or cookbooks are being used beyond what's visible in the repository
5. The target environment will continue to be Ubuntu 20.04 or compatible systems
6. The migration will maintain the same level of security hardening present in the original code
7. No database or complex application dependencies exist beyond what's visible in the files
8. The hardcoded credentials in the setup scripts are for demonstration purposes only