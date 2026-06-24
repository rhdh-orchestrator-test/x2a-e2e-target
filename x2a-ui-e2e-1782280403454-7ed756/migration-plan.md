# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for continuous compliance. The migration scope is relatively small, with only a few Ansible playbooks and InSpec test files to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled (security compliance)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing web server functionality. Can be directly used in Ansible content.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with testinfra for infrastructure testing
  - Option 2: Integrate with other compliance tools like Ansible Lint or OpenSCAP
  - Option 3: Convert InSpec tests to Ansible assert tasks

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL/TLS settings are maintained during migration.
  - Migration approach: Preserve the same SSL configuration parameters in the Ansible tasks
  
- **SSH Security**: The InSpec tests verify SSH root login is disabled.
  - Migration approach: Create equivalent Ansible tasks to verify and enforce SSH security settings

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions.
  - Mitigation: Use Ansible assert modules or integrate with testinfra for similar functionality.

- **Chef Automate Deployment**: The bash scripts for Chef Automate deployment need to be converted to Ansible roles.
  - Mitigation: Create Ansible roles that perform equivalent setup steps for a compliance solution.

### Migration Order

1. **website_https playbook** (low risk, already Ansible)
   - Only needs minor adjustments to follow best practices
   
2. **poodle_fix playbook** (low risk, already Ansible)
   - Only needs minor adjustments to follow best practices
   
3. **InSpec tests** (moderate complexity)
   - Convert to Ansible-native testing solutions
   
4. **Chef Automate deployment scripts** (high complexity)
   - Convert to Ansible roles for deploying alternative compliance solutions

### Assumptions

1. The primary goal is to migrate all functionality to pure Ansible without Chef dependencies.
2. The InSpec tests need to be replaced with equivalent functionality in Ansible.
3. The Chef Automate and Chef Server deployment scripts will be replaced with Ansible roles that deploy alternative compliance solutions.
4. The target environment will remain Ubuntu 20.04 or compatible Linux distributions.
5. The hardcoded credentials in the setup scripts are for demonstration purposes and will be properly secured in the migrated solution.
6. The Test Kitchen configuration will be replaced with Ansible Molecule for testing.