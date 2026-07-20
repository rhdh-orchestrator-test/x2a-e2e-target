# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for HTTPS website deployment and SSL security
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL security hardening, compliance testing

- **setup-automate**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user/organization setup

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that configures Apache with HTTPS. Migration considerations include preserving the SSL certificate generation and virtual host configuration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that hardens SSL configuration against POODLE vulnerability. Migration considerations include ensuring security hardening is maintained.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration considerations include replacing with Ansible-native testing framework or adapting to use Molecule.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website verification. Migration considerations include converting to Ansible test framework or maintaining InSpec for compliance testing.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Migration considerations include converting to Ansible test framework or maintaining InSpec for compliance testing.
- `setup-automate/deploy-automate.sh`: Shell script for deploying Chef Automate and Chef Infra Server. Migration considerations include replacing with Ansible playbook for infrastructure setup.
- `setup-automate/deploy-chef-server.sh`: Shell script for deploying Chef Infra Server. Migration considerations include replacing with Ansible playbook for infrastructure setup.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package manager usage in playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing or maintain InSpec as a compliance tool integrated with Ansible
  - Migration strategy: Use Ansible's `assert` module for basic tests, or integrate with InSpec using the `inspec_exec` module from the `community.general` collection
  
- **Test Kitchen**: Replace with Molecule for Ansible role/playbook testing
  - Migration strategy: Create equivalent Molecule scenarios for testing the Ansible playbooks

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or other Ansible management solution
  - Migration strategy: Create Ansible playbooks to deploy and configure Ansible Automation Platform

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL and harden against POODLE vulnerability
  - Migration approach: Ensure the same SSL hardening is implemented in the migrated Ansible playbooks
  
- **SSH Security**: InSpec tests verify SSH root login is disabled
  - Migration approach: Maintain this security check in the migrated solution
  
- **Vault/secrets management**:
  - Hardcoded credentials in shell scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated on the fly and should be handled securely in the migrated solution
  - Count of credentials detected: 2 (username/password in shell scripts)

### Technical Challenges

- **Compliance Testing**: The repository demonstrates using Chef InSpec for compliance testing with Ansible
  - Mitigation strategy: Either maintain InSpec as a compliance tool or migrate to Ansible-native testing with additional modules for compliance checks
  
- **Integration Testing**: Test Kitchen is used for integration testing
  - Mitigation strategy: Replace with Molecule for Ansible role/playbook testing with equivalent functionality

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/website_https.yml, chef-and-ansible/poodle_fix.yml) - low risk, already in Ansible format
2. **Testing Framework** (chef-and-ansible/kitchen.yml, tests/) - moderate complexity, requires adapting or replacing InSpec tests
3. **Chef Deployment Scripts** (setup-automate/) - high complexity, requires replacing Chef-specific infrastructure

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec for compliance testing alongside Ansible, not for production deployment
2. The Chef Automate and Chef Infra Server deployment scripts are used for setting up a test environment
3. The hardcoded credentials in the shell scripts are for demonstration purposes only
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. The migration should maintain the same level of security compliance testing
6. The repository does not contain actual Chef cookbooks or recipes that need migration, only InSpec tests and Ansible playbooks
7. The migration will standardize on Ansible while potentially maintaining InSpec for compliance testing if required