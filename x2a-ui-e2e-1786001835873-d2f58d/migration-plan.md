# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Consolidating existing Ansible playbooks into a standardized structure
3. Preserving the InSpec testing capabilities within an Ansible-only workflow

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the limited scope of the repository.

## Module Migration Plan

This repository contains both Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS, creates self-signed certificates, and deploys a simple "Hello World" website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server on a VM
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server (without Automate) on a VM
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `tests/website_https_verify.rb`: Chef InSpec test file that verifies HTTPS configuration and security

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-test with custom modules
  - Option 2: Integrate with Molecule for testing
  - Option 3: Maintain InSpec as a separate tool called from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/collection testing
  - Ansible-specific CI/CD pipelines

### Security Considerations

- **SSL/TLS Configuration**: The playbooks handle SSL configuration and certificate generation
  - Migration approach: Preserve the same SSL hardening in the consolidated Ansible playbooks
  - Consider using the `community.crypto` collection for certificate operations

- **Hardcoded Credentials**: 
  - The Chef deployment scripts contain hardcoded credentials (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

- **Self-signed Certificates**:
  - Current implementation uses self-signed certificates
  - Migration approach: Maintain the same approach but consider adding support for Let's Encrypt as an option

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible
  - Challenge: Ensuring idempotent installation of Chef components
  - Mitigation: Create dedicated Ansible roles for Chef server deployment with proper state checking

- **InSpec Testing Integration**: Maintaining compliance testing capabilities
  - Challenge: Integrating InSpec tests with Ansible-only workflow
  - Mitigation: Create an Ansible role that can execute InSpec tests as part of playbook runs

### Migration Order

1. **website_https playbook** (low risk, already Ansible)
   - Refactor into a proper Ansible role structure
   - Update to use Ansible best practices and collections

2. **poodle_fix playbook** (low risk, already Ansible)
   - Refactor into a proper Ansible role structure
   - Could be merged with the website_https role as a security enhancement

3. **InSpec tests** (moderate complexity)
   - Create an Ansible framework to execute the existing InSpec tests
   - Consider gradually migrating to Ansible-native testing

4. **Chef deployment scripts** (high complexity)
   - Create Ansible roles to replace the Chef Automate and Chef Server deployment scripts
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The primary goal is to consolidate on Ansible as the single configuration management tool
2. The InSpec testing functionality needs to be preserved
3. The Chef deployment scripts are used for setting up Chef infrastructure, not for ongoing configuration management
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
5. The existing SSL/TLS security configurations must be maintained or enhanced
6. No external dependencies or integrations beyond what's visible in the repository