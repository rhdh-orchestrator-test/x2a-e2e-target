# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef infrastructure setup scripts that need to be migrated to a unified Ansible approach. The repository appears to be a demonstration of how Chef InSpec can be used alongside Ansible for compliance automation, along with scripts for setting up Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and bash scripts to migrate. The estimated timeline for this migration is 1-2 weeks, with low complexity for the Ansible playbooks (which can be directly reused) and medium complexity for the Chef server setup scripts (which need to be converted to Ansible roles).

## Module Migration Plan

This repository contains Ansible playbooks and Chef setup scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **chef-automate-setup**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-setup**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS website configuration
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or any cloud platform

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles
- **InSpec**: Can be retained as a testing framework or replaced with Ansible's built-in assert module and community.general collection
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source alternatives like AWX

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates. Migration should maintain or improve this security practice.
- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. This security check should be maintained in the Ansible migration.
- **Vault/secrets management**:
  - Hardcoded credentials in the Chef setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated on the fly, but in production should be managed securely

### Technical Challenges

- **InSpec Integration**: If keeping InSpec for compliance testing, ensure proper integration with Ansible workflows
- **Chef Server Functionality**: Determine if all Chef Server functionality is needed or if some can be eliminated in an Ansible-only approach
- **Testing Framework**: Establish a new testing framework to replace Test Kitchen while maintaining the same level of validation

### Migration Order

1. Ansible playbooks (website_https.yml, poodle_fix.yml) - low risk, can be directly reused
2. InSpec tests - moderate complexity, convert to Ansible assert or keep as InSpec
3. Chef server setup scripts - high complexity, convert to Ansible roles

### Assumptions

1. The repository is primarily for demonstration purposes and may not represent a production environment
2. The Chef setup scripts are used for infrastructure setup rather than ongoing configuration management
3. InSpec is being used as a compliance tool alongside Ansible rather than as part of a Chef-based workflow
4. The migration goal is to consolidate on Ansible rather than maintain a hybrid approach
5. No external data sources or complex state management is present in the current implementation
6. The hardcoded credentials in the setup scripts are for demonstration only and would be replaced in production

## Migration Steps

1. **Ansible Playbooks**:
   - Retain existing playbooks with minimal changes
   - Update to use Ansible best practices (roles, collections, etc.)
   - Implement Ansible Vault for any sensitive data

2. **Chef Server Setup**:
   - Create Ansible roles to replace the Chef server setup scripts
   - Use Ansible's package management modules instead of curl/bash commands
   - Implement idempotent configuration for all steps

3. **Testing Framework**:
   - Set up Ansible Molecule for testing
   - Either convert InSpec tests to Ansible assertions or maintain InSpec integration
   - Ensure all compliance checks are maintained

4. **Documentation**:
   - Update documentation to reflect the Ansible-only approach
   - Provide migration notes for users familiar with the original repository