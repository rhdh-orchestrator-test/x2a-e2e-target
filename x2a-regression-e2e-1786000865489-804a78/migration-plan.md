# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Consolidating existing Ansible playbooks into a standardized structure
3. Preserving the Chef InSpec testing capabilities within an Ansible workflow

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the limited scope of the repository.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that addresses SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: Chef InSpec test file that verifies HTTPS configuration and security

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-test with custom modules
  - Option 2: Integrate with Molecule for testing
  - Option 3: Maintain InSpec as a separate testing tool called from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - Ansible-compatible CI/CD pipeline configuration

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration and POODLE vulnerability mitigation
  - Migration approach: Preserve the same SSL hardening in the Ansible playbooks
  - Consider using the ansible.builtin.lineinfile module instead of replace for better idempotency

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

- **Certificate Management**:
  - Self-signed certificates are generated in the playbook
  - Migration approach: Consider using ansible.builtin.openssl_* modules (already in use) with Ansible Vault for key storage

### Technical Challenges

- **Chef Automate/Infra Server Deployment**: Converting the bash scripts to Ansible playbooks
  - Mitigation: Create dedicated roles for Chef server deployment
  - Consider using official Chef collection from Ansible Galaxy if available

- **InSpec Testing Integration**: Maintaining compliance testing capabilities
  - Mitigation: Create a custom Ansible module or role that can execute InSpec tests
  - Alternative: Migrate tests to Ansible-native assertion methods

### Migration Order

1. **Ansible Playbooks Standardization** (Low risk, high value)
   - Restructure existing Ansible playbooks into proper roles
   - Implement Ansible best practices (variables, handlers, etc.)

2. **Chef Deployment Scripts Conversion** (Moderate complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement secure credential management

3. **Testing Framework Integration** (High complexity)
   - Integrate or migrate InSpec tests to work with the new Ansible structure

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment, based on the README content.
2. The Chef InSpec tests are essential to maintain for compliance verification.
3. The hardcoded credentials in the deployment scripts are for demonstration only and would be replaced with secure alternatives.
4. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file.
5. The Apache configuration is intended to be a simple example and may need enhancement for production use.
6. The repository structure may not follow Ansible best practices as it appears to be primarily educational.