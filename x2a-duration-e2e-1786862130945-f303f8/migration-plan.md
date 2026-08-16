# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate deployment scripts to Ansible playbooks
2. Consolidating existing Ansible playbooks and InSpec tests into a standardized Ansible structure
3. Preserving the compliance testing functionality provided by InSpec

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the small codebase.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-test with custom modules
  - Option 2: Integrate with Molecule for testing
  - Option 3: Maintain InSpec for testing but call it from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/collection testing
  - Or adapt existing kitchen.yml to work with Ansible collections

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in poodle_fix.yml
  - Ensure TLSv1.2 is enforced and SSLv3 is disabled
  - Maintain the same security posture for Apache

- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions
  - Implement equivalent checks in Ansible or maintain InSpec tests

- **Vault/secrets management**:
  - Current implementation uses hardcoded credentials in deploy scripts
  - Migration should use Ansible Vault for:
    - Chef user password in deployment scripts
    - Any SSL private keys

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible
  - Challenge: Ensuring idempotent installation of Chef products
  - Mitigation: Use Ansible's package management and command modules with creates/changed_when conditions

- **InSpec Test Integration**: Preserving compliance testing functionality
  - Challenge: Maintaining the same level of compliance testing without InSpec
  - Mitigation: Either integrate InSpec with Ansible or convert tests to equivalent Ansible assertions

- **SSL Certificate Management**: Ensuring proper certificate generation and configuration
  - Challenge: Maintaining the same security posture for SSL/TLS
  - Mitigation: Use Ansible's crypto modules (openssl_*) consistently

### Migration Order

1. **website_https playbook** (low risk, already Ansible)
   - Refactor into proper Ansible role structure
   - Update to use Ansible best practices (handlers, variables)

2. **poodle_fix playbook** (low risk, already Ansible)
   - Refactor into proper Ansible role structure
   - Combine with website_https role as an optional feature

3. **InSpec Tests** (moderate complexity)
   - Either integrate with Ansible or convert to equivalent Ansible assertions
   - Ensure compliance testing is maintained

4. **Chef Deployment Scripts** (high complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The primary goal is to standardize on Ansible as the configuration management tool
2. Chef InSpec tests should be preserved or converted to equivalent Ansible functionality
3. The Chef Automate and Chef Server deployment should be converted to Ansible playbooks
4. The existing Ansible playbooks need refactoring to follow Ansible best practices
5. The target environment will remain Ubuntu 20.04 or compatible systems
6. The security posture defined in the InSpec tests must be maintained
7. No application-specific logic beyond what's in the current scripts needs to be migrated