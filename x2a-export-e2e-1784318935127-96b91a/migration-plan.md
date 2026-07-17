# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need to be migrated to a unified Ansible solution. The repository primarily consists of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec tests for validating security compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **MEDIUM** with an estimated timeline of 2-3 weeks. The primary focus will be on converting InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks and enhancing them with proper roles and collections structure.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Main module containing Ansible playbooks for Apache HTTPS configuration and InSpec tests for compliance validation
    - Path: chef-and-ansible
    - Technology: Mixed (Ansible playbooks and Chef InSpec)
    - Key Features: Apache HTTPS configuration, SSL security hardening, compliance testing

- **setup-automate**:
    - Description: Shell scripts for Chef Automate and Chef Infra Server deployment
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef infrastructure deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `chef-and-ansible/index.html`: Sample HTML file for website testing
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance
- `setup-automate/deploy-automate.sh`: Script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Script for deploying Chef Infra Server only

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule with testinfra for infrastructure testing
  - Option 2: Use ansible-test framework for validation
  - Option 3: Integrate with ansible-lint for static analysis

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure
  - Molecule provides similar functionality with native Ansible support
  - Will require new molecule.yml configuration files

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible roles
  - Create Ansible roles for configuration management
  - Consider using AWX/Ansible Tower as a replacement for Chef Automate

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the POODLE fix playbook
  - Ensure TLSv1.2 remains enabled and older protocols disabled
  - Maintain proper certificate generation and management

- **SSH Hardening**: The SSH security profile must be converted to Ansible
  - Create equivalent Ansible tasks to enforce SSH root login restrictions
  - Maintain STIG compliance requirements

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username: 'jtonello', password: 'password')
  - Replace with Ansible Vault for secure credential storage
  - SSL certificate generation should use Ansible Vault for key protection

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks
  - InSpec has rich testing capabilities that may require multiple Ansible modules to replicate
  - Solution: Use combination of Molecule, testinfra, and custom Ansible modules

- **Maintaining Compliance Standards**: Ensuring STIG compliance is preserved
  - The SSH profile contains specific STIG IDs and CCI references
  - Solution: Document mapping between InSpec controls and Ansible tasks

- **Chef Server Replacement**: Determining the appropriate Ansible management solution
  - Chef Server provides centralized management that needs an equivalent
  - Solution: Implement AWX/Ansible Tower or other Ansible management platform

### Migration Order

1. **Apache HTTPS Configuration** (low risk, already Ansible)
   - Refactor `chef-and-ansible/website_https.yml` into proper Ansible role structure
   - Add documentation and improve variable usage

2. **POODLE Vulnerability Fix** (low risk, already Ansible)
   - Integrate `chef-and-ansible/poodle_fix.yml` with website-https role
   - Improve idempotence and testing

3. **HTTPS Compliance Tests** (medium complexity)
   - Convert `chef-and-ansible/tests/website_https_verify.rb` to Molecule/testinfra
   - Ensure all compliance checks are preserved

4. **SSH Security Profile** (medium complexity)
   - Convert `chef-and-ansible/tests/ssh_profile.rb` to Ansible role with appropriate checks
   - Maintain STIG compliance documentation

5. **Chef Deployment Scripts** (high complexity)
   - Replace `setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh` with Ansible roles
   - Implement secure credential handling

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or compatible systems
2. Vagrant will remain the primary testing platform
3. The security compliance requirements (STIG, CCI) must be maintained
4. The migration will consolidate to pure Ansible without maintaining Chef components
5. Test Kitchen functionality needs to be replicated in the Ansible ecosystem
6. The Apache configuration details (virtual hosts, SSL settings) must be preserved exactly
7. The Chef Automate/Infra Server deployment may be replaced with an Ansible management solution
8. The current hardcoded credentials in scripts will be replaced with secure alternatives