# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **inspec-tests**:
    - Description: Chef InSpec tests for verifying HTTPS website and SSH configurations
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification, SSH security compliance

- **chef-automate-setup**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring HTTPS website
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for SSL security hardening
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website verification
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

- **Chef InSpec**: Replace with Ansible's built-in testing framework or integrate with Ansible using the ansible_inspec module
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks for infrastructure management

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL security hardening in the poodle_fix.yml playbook
- **SSH Security**: The SSH compliance checks must be maintained in the Ansible implementation
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - SSL certificates generated in the Ansible playbook
  - Recommend implementing Ansible Vault for credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing mechanisms will require careful mapping of test assertions
- **Compliance Reporting**: Chef InSpec provides rich compliance reporting that needs to be replicated in the Ansible environment
- **Test Kitchen to Molecule**: Test workflows will need to be adapted to use Molecule instead of Test Kitchen

### Migration Order

1. **website-https** (low risk, already in Ansible)
2. **poodle-fix** (low risk, already in Ansible)
3. **chef-automate-setup** (moderate complexity, convert bash to Ansible)
4. **inspec-tests** (high complexity, convert InSpec to Ansible testing)

### Assumptions

1. The primary purpose of this repository is to demonstrate compliance automation with Chef InSpec alongside Ansible
2. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs
3. There are no external dependencies or integrations beyond what's visible in the repository
4. The migration will consolidate all functionality into pure Ansible without Chef components
5. The InSpec tests are intended to be run against systems provisioned by Ansible
6. The Chef Automate and Chef Infra Server deployment scripts are examples and not critical to the core functionality
7. No actual Chef cookbooks or recipes are present in the repository that need migration