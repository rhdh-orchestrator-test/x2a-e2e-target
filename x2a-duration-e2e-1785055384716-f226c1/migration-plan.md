# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef Automate/Infra Server deployment scripts. The migration scope is relatively small, focusing on:

1. Consolidating existing Ansible playbooks into a standardized Ansible structure
2. Converting Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks
3. Preserving the InSpec compliance testing functionality within the Ansible workflow

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the small codebase.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS website functionality and security
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration compliance

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **InSpec**: Maintain InSpec tests but integrate with Ansible using the `ansible_inspec` module or Molecule's InSpec verifier
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or maintain as a separate system managed by Ansible

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the POODLE fix playbook
  - Approach: Create an Ansible role for Apache SSL hardening that enforces TLSv1.2
  
- **Self-signed Certificates**: The current implementation uses self-signed certificates
  - Approach: Create an Ansible role for certificate management with options for self-signed or proper CA certificates

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
    - Approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Integration**: Ensuring InSpec tests continue to work with the migrated Ansible structure
  - Mitigation: Use Ansible Molecule with InSpec verifier or create a post-deployment verification playbook

- **Chef Automate Functionality**: Determining if all Chef Automate functionality is needed or if it can be replaced
  - Mitigation: Assess which Chef Automate features are actually used and find Ansible equivalents or complementary tools

### Migration Order

1. **website_https playbook** (low risk, already Ansible)
   - Refactor into proper Ansible role structure with variables
   - Integrate InSpec tests with Molecule

2. **poodle_fix playbook** (low risk, already Ansible)
   - Refactor into proper Ansible role structure
   - Consider merging with website_https as a security hardening option

3. **Chef deployment scripts** (moderate complexity)
   - Create Ansible playbooks to replace the bash scripts
   - Use Ansible Vault for credential management

### Assumptions

1. The existing Ansible playbooks are functional but not organized according to best practices
2. InSpec tests are required for compliance verification and must be preserved
3. The Chef Automate and Chef Infra Server deployments are for infrastructure management that will be replaced by Ansible
4. No actual Chef cookbooks or recipes need migration, only the deployment scripts
5. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
6. The hardcoded credentials in the deployment scripts are for testing only and will be replaced with secure alternatives