# MIGRATION FROM CHEF/ANSIBLE HYBRID TO ANSIBLE

## Executive Summary

This repository contains a hybrid environment with Chef InSpec for compliance testing and Ansible playbooks for configuration management. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec compliance tests to Ansible-native solutions
2. Refactoring existing Ansible playbooks to follow best practices
3. Migrating Chef Automate/Chef Server deployment scripts to Ansible

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited scope and the fact that most configuration is already in Ansible format.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS configuration and security compliance
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening tests, HTTPS content verification, SSL protocol security checks

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `index.html`: Simple HTML template for the website

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for testing Ansible roles
  - Option 2: Ansible Assert module for inline compliance checks
  - Option 3: OpenSCAP with Ansible for compliance scanning

- **Test Kitchen**: Replace with:
  - Ansible Molecule for role testing
  - GitHub Actions or other CI/CD pipeline for automated testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains the minimum protocol version
  - Consider upgrading to include TLSv1.3 support

- **Certificate Management**: 
  - Current implementation uses self-signed certificates
  - Consider integrating with Let's Encrypt for production environments

- **Vault/secrets management**:
  - The deploy scripts contain hardcoded credentials that should be moved to Ansible Vault
  - Credentials detected: 
    - chef-automate-deploy: 1 password in plaintext
    - chef-server-deploy: 1 password in plaintext

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require:
  - Mapping InSpec resources to Ansible modules
  - Implementing equivalent assertions using Ansible's assert module
  - Ensuring the same level of compliance reporting

- **Chef Server Deployment**: Converting the Chef Server deployment scripts to Ansible will require:
  - Creating idempotent Ansible tasks for Chef Server installation
  - Managing Chef user and organization creation through Ansible
  - Handling certificate and key file management

### Migration Order

1. **website_https.yml** (Priority 1 - already in Ansible format, minimal changes needed)
   - Refactor to use Ansible roles for better organization
   - Implement variable files for environment-specific configurations

2. **poodle_fix.yml** (Priority 1 - already in Ansible format, minimal changes needed)
   - Integrate into a security hardening role
   - Update to include additional modern TLS best practices

3. **website_https_verify.rb** (Priority 2 - requires conversion from InSpec to Ansible)
   - Convert to Ansible assert tasks or Molecule tests
   - Ensure all compliance checks are maintained

4. **Chef Server Deployment Scripts** (Priority 3 - complex conversion from bash to Ansible)
   - Create Ansible roles for Chef Server deployment
   - Implement Ansible Vault for credential management
   - Add idempotency checks to prevent duplicate installations

### Assumptions

1. The current environment uses Test Kitchen primarily for testing Ansible playbooks, not for developing Chef cookbooks
2. The InSpec tests are used only for verification and not as part of a larger compliance strategy
3. The Chef Server deployment scripts are used for setting up test environments, not production infrastructure
4. There are no external dependencies on Chef-specific features that would be lost in migration
5. The target environment will continue to be Ubuntu-based systems
6. No custom Chef resources or complex Chef-specific logic exists that would require special handling