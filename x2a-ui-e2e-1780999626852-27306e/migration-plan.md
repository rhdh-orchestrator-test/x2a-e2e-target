# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks

**Estimated Timeline**: 1-2 weeks for a complete migration, with the majority of time spent on converting InSpec tests to Ansible-native solutions.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled (security compliance)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider OpenSCAP integration for STIG compliance

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that:
  - Set hostname
  - Configure system parameters
  - Install and configure alternative compliance and infrastructure management tools

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should maintain or improve security by:
  - Ensuring modern TLS protocols (TLSv1.2+) are enforced
  - Implementing proper certificate management
  - Following current best practices for web server security

- **SSH Security**: The InSpec test verifies SSH root login is disabled. Migration should:
  - Maintain this security check in Ansible
  - Consider expanding SSH hardening based on CIS or STIG benchmarks

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions will require:
  - Understanding the compliance requirements being tested
  - Implementing equivalent checks using Ansible modules
  - Ensuring the same level of reporting and documentation

- **Chef Deployment Scripts**: Converting the Chef deployment scripts to Ansible will require:
  - Understanding the Chef Automate/Infra Server architecture
  - Creating equivalent Ansible roles for deployment
  - Handling user and organization creation
  - Managing certificates and authentication

### Migration Order

1. **website_https.yml and poodle_fix.yml** (Priority 1, low risk): These are already Ansible playbooks and require minimal changes, possibly just refactoring into roles.

2. **Chef deployment scripts** (Priority 2, moderate complexity): Convert these to Ansible playbooks, focusing on maintaining the same functionality while improving security practices.

3. **InSpec tests** (Priority 3, high complexity): Convert these to Ansible-native testing solutions, ensuring all compliance checks are maintained.

### Assumptions

1. The primary goal is to move entirely to Ansible and eliminate Chef dependencies.
2. The current setup is used primarily for demonstration/testing rather than production.
3. The security compliance requirements (STIG references in ssh_profile.rb) need to be maintained.
4. No external data sources or complex integrations exist beyond what's visible in the repository.
5. The target environment will continue to be Ubuntu 20.04 or compatible systems.
6. The self-signed certificate approach is acceptable for the migrated solution.
7. The hardcoded credentials in deployment scripts are for demonstration purposes and will be properly secured in the migration.