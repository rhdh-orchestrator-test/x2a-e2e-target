# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment shell scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining InSpec tests for compliance validation

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a single engineer, as the repository primarily contains shell scripts for Chef infrastructure deployment and some existing Ansible playbooks with InSpec tests.

## Module Migration Plan

This repository contains shell scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Security hardening, SSL protocol configuration

- **deploy-automate**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server on a VM
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **deploy-chef-server**:
    - Description: Bash script that deploys Chef Infra Server (without Automate) on a VM
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Infra Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management
- **Test Kitchen**: Consider migrating to Molecule for Ansible role testing
- **InSpec**: Maintain InSpec for compliance testing or consider migrating to Ansible's built-in assert module or other testing frameworks

### Security Considerations

- **SSL/TLS Configuration**: The repository includes SSL hardening (disabling SSLv3, enabling TLSv1.2) which must be preserved in the migrated solution
- **SSH Hardening**: InSpec tests verify SSH root login is disabled, which should be maintained in the Ansible configuration
- **Self-signed Certificates**: The current implementation uses self-signed certificates; consider implementing proper certificate management
- **Vault/secrets management**:
  - Hardcoded credentials in shell scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible will require understanding of Chef Automate's architecture and configuration requirements
  - Mitigation: Create dedicated Ansible roles for Chef Automate and Chef Infra Server deployment
  
- **InSpec Integration**: Maintaining the InSpec tests while migrating to pure Ansible
  - Mitigation: Use Ansible's built-in testing capabilities or continue using InSpec with Ansible

- **Configuration Validation**: Ensuring the migrated Ansible playbooks provide the same functionality as the original scripts
  - Mitigation: Develop comprehensive testing to validate the migrated playbooks

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (low risk, already Ansible)
   - Review and optimize existing Ansible playbooks
   - Enhance with Ansible best practices (roles, variables, etc.)

2. **deploy-chef-server.sh** (moderate complexity)
   - Convert to Ansible playbook
   - Implement secure credential management with Ansible Vault

3. **deploy-automate.sh** (higher complexity)
   - Convert to Ansible playbook
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment
2. InSpec tests should be preserved for compliance validation
3. The hardcoded credentials in the shell scripts are for demonstration purposes and will be replaced with secure alternatives
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
5. The migration will not change the fundamental architecture (i.e., Chef Automate and Chef Infra Server will still be deployed, but using Ansible instead of shell scripts)
6. Test Kitchen can be replaced with Molecule or another Ansible-compatible testing framework