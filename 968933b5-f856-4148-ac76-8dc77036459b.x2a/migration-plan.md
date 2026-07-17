# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for demonstrating compliance automation. The primary focus appears to be on showing how Chef InSpec can be used alongside Ansible for compliance testing. There are also Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: A demonstration of using Chef InSpec with Ansible for compliance automation
    - Path: chef-and-ansible
    - Technology: Chef InSpec and Ansible
    - Key Features: HTTPS website deployment, SSL/TLS configuration, compliance testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration should replace with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website. Can be directly used in Ansible migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be directly used in Ansible migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Should be migrated to Ansible test framework or kept as InSpec.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Should be migrated to Ansible test framework or kept as InSpec.
- `setup-automate/deploy-automate.sh`: Script for deploying Chef Automate and Chef Infra Server. Should be replaced with Ansible playbook for infrastructure deployment.
- `setup-automate/deploy-chef-server.sh`: Script for deploying Chef Infra Server. Should be replaced with Ansible playbook for infrastructure deployment.

### Target Details

Analyzing the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (based on kitchen.yml configuration)
- **Virtual Machine Technology**: Vagrant (based on kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions like Molecule or maintain InSpec as a separate testing tool
- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks for infrastructure deployment

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure SSL/TLS for Apache. Migration should maintain secure TLS 1.2+ configuration.
- **SSH Security**: InSpec tests verify SSH root login is disabled. Migration should maintain this security check.
- **Self-signed Certificates**: The playbooks generate self-signed certificates. Migration should maintain or improve certificate management.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL/TLS certificate references in the Apache configuration

### Technical Challenges

- **Testing Framework**: Deciding whether to keep InSpec for testing or migrate to an Ansible-native testing solution like Molecule
- **Infrastructure Deployment**: Replacing Chef Automate/Infra Server deployment scripts with equivalent Ansible playbooks
- **Compliance Automation**: Ensuring compliance checks are maintained during migration

### Migration Order

1. Ansible Playbooks (website_https.yml, poodle_fix.yml) - low risk, already in Ansible format
2. InSpec Tests (website_https_verify.rb, ssh_profile.rb) - moderate complexity, decide on testing framework
3. Chef Deployment Scripts (deploy-automate.sh, deploy-chef-server.sh) - high complexity, requires new Ansible playbooks

### Assumptions

1. The repository is primarily for demonstration purposes rather than production use
2. The InSpec tests are intended to work with Ansible playbooks as shown in the kitchen.yml configuration
3. The deployment scripts are for setting up Chef infrastructure, which may not be needed in an Ansible-only environment
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. No complex Chef cookbooks or recipes are present that would require significant refactoring
6. The primary goal is to demonstrate compliance automation, which can be achieved with Ansible and appropriate testing tools