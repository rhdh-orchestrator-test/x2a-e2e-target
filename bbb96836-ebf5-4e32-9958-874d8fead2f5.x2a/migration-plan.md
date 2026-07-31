# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef Automate/Infra Server deployment scripts. The migration scope is relatively small, focusing on:

1. Consolidating existing Ansible playbooks into a standardized Ansible structure
2. Converting Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks
3. Preserving the InSpec testing capabilities within an Ansible workflow

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a single engineer to complete the migration, including testing and documentation.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration, including self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL configuration hardening, service restart handlers

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

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test profile for verifying HTTPS website deployment
- `tests/ssh_profile.rb`: InSpec test profile for SSH security compliance checks

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **InSpec**: Maintain InSpec for compliance testing, integrating with Ansible using the ansible_inspec module or Molecule's verifier
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source alternatives like AWX

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
- **Self-signed Certificates**: The certificate generation process should be maintained in the Ansible roles
- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys should be handled securely

### Technical Challenges

- **InSpec Integration**: Ensuring InSpec tests continue to work with the new Ansible structure
  - Mitigation: Use Ansible's built-in support for InSpec or integrate with Molecule's verifier
  
- **Chef Automate Functionality**: Replacing Chef Automate's functionality with Ansible equivalents
  - Mitigation: Map Chef Automate features to Ansible Automation Platform or AWX features

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - Refactor into a proper Ansible role structure
   - Update the playbook to use variables from inventory or vars files

2. **poodle_fix.yml** (low risk, already Ansible)
   - Refactor into a proper Ansible role structure
   - Consider merging with the website_https role as an optional feature

3. **InSpec Tests** (medium risk)
   - Set up Molecule for testing
   - Configure InSpec as a verifier in Molecule

4. **Chef Deployment Scripts** (high complexity)
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment
   - Implement Ansible Vault for credential storage
   - Consider whether Chef Automate/Infra Server is still needed or can be replaced with Ansible Automation Platform

### Assumptions

1. The primary goal is to standardize on Ansible and eliminate Chef dependencies
2. InSpec testing capabilities should be preserved
3. The Chef Automate and Chef Infra Server deployment scripts are still relevant and needed
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The existing Ansible playbooks are functional and follow best practices
6. No external dependencies or inventory files exist beyond what's in the repository