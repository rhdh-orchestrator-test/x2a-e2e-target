# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while standardizing their structure
3. Maintaining Chef InSpec testing capabilities within the Ansible workflow

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository contains minimal Chef-specific code, with most infrastructure already defined in Ansible

## Module Migration Plan

This repository contains both Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Security hardening, SSL protocol configuration

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

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with Chef InSpec verification
- `tests/website_https_verify.rb`: Chef InSpec test file for verifying HTTPS configuration
- `index.html`: Likely a sample HTML file for the website_https playbook

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Currently used for compliance testing of Ansible playbooks. Replace with:
  - Option 1: Continue using InSpec with Ansible (recommended for compatibility)
  - Option 2: Migrate to Ansible's built-in testing framework (ansible-test)
  - Option 3: Use Molecule for Ansible role testing

- **Test Kitchen**: Currently used for testing Ansible playbooks. Replace with:
  - Option 1: Continue using Test Kitchen with Ansible (recommended for compatibility)
  - Option 2: Migrate to Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Currently deployed via bash scripts. Replace with:
  - Ansible playbooks that perform equivalent server setup and configuration

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration must maintain or improve security settings:
  - Ensure TLS 1.2+ is enforced (as in poodle_fix.yml)
  - Consider upgrading to more modern SSL configurations (TLS 1.3)
  
- **Self-signed Certificates**: The current implementation uses self-signed certificates:
  - Consider integrating with Let's Encrypt for production environments
  - Maintain self-signed option for development/testing

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Recommend migrating to Ansible Vault for secure credential storage

### Technical Challenges

- **Chef InSpec Integration**: Maintaining compliance testing while migrating to pure Ansible:
  - Solution: Use Ansible's `community.general.inspec` module to run InSpec tests from Ansible

- **Chef Server Deployment**: Converting Chef server deployment to Ansible:
  - Challenge: Ensuring idempotent installation of Chef components
  - Solution: Create dedicated Ansible roles for Chef server components with proper state checking

### Migration Order

1. **Ansible Playbooks Standardization** (Low risk, high value)
   - Refactor existing Ansible playbooks into proper roles
   - Implement Ansible best practices (variables, handlers, etc.)

2. **Chef Automate/Server Deployment Scripts** (Medium complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement secure credential management with Ansible Vault

3. **Testing Framework** (Medium complexity)
   - Ensure InSpec tests continue to work with the new Ansible structure
   - Consider adding additional test coverage

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment
2. The Chef InSpec tests are valuable and should be preserved in the migration
3. The hardcoded credentials in the setup scripts are for demonstration only and would be replaced in a production environment
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. The Apache configuration requirements will remain the same after migration