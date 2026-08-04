# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef infrastructure setup scripts and Ansible playbooks that need to be migrated to a consistent Ansible-based approach. The repository appears to be a demonstration environment showing how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, with only a few scripts and playbooks to convert. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef infrastructure setup scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Security hardening, service restart handlers

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks in a Vagrant environment
- `tests/website_https_verify.rb`: InSpec tests for verifying HTTPS website functionality
- `tests/ssh_profile.rb`: InSpec compliance profile for SSH security settings
- `index.html`: Simple HTML file used for testing web server functionality

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management
- **Test Kitchen**: Replace with Ansible Molecule for testing
- **InSpec**: Can be retained for compliance testing or replaced with Ansible-native solutions like ansible-lint

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should maintain or improve the security settings:
  - Ensure TLSv1.2 or higher is enforced
  - Maintain proper certificate generation and management
  
- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions. Migration should:
  - Implement equivalent SSH hardening in Ansible
  - Maintain compliance with security benchmarks referenced (SRG-OS-000112)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec Integration**: Determining how to maintain the compliance testing functionality currently provided by InSpec:
  - Option 1: Keep InSpec for compliance testing alongside Ansible
  - Option 2: Migrate to Ansible-native compliance checking
  - Option 3: Integrate with another compliance tool like OpenSCAP

- **Chef Server Replacement**: Determining the appropriate Ansible-based replacement for Chef Server functionality:
  - Option 1: Ansible AWX/Tower
  - Option 2: GitOps approach with CI/CD pipelines
  - Option 3: Simple Ansible playbook repository with inventory management

### Migration Order

1. **website-https.yml** and **poodle-fix.yml** (already Ansible playbooks, need minimal changes)
2. **chef-server-deploy.sh** and **chef-automate-deploy.sh** (convert Bash scripts to Ansible roles)
3. **Test Kitchen configuration** (replace with Ansible Molecule)
4. **InSpec tests** (decide on compliance strategy and implement)

### Assumptions

1. The primary goal is to standardize on Ansible and remove Chef dependencies
2. InSpec tests may still be valuable and could be retained even after migration
3. The repository is primarily for demonstration/educational purposes rather than production use
4. No external Chef cookbooks or complex Chef-managed infrastructure exists beyond what's visible in the repository
5. The hardcoded credentials in the setup scripts are for demonstration purposes and not used in production
6. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions