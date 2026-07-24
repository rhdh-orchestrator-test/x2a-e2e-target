# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a pure Ansible solution. The repository primarily consists of:

1. Chef InSpec test profiles for compliance validation
2. Ansible playbooks for configuration management
3. Shell scripts for Chef Automate and Chef Infra Server deployment

The migration complexity is **LOW to MEDIUM** as most of the configuration is already in Ansible format, with the main work being to convert the InSpec tests to Ansible-compatible testing frameworks and replace the Chef server deployment scripts with Ansible playbooks.

**Estimated Timeline**: 2-3 weeks for a complete migration, with the following breakdown:
- 1 week: Convert InSpec tests to Ansible-compatible testing (Molecule/TestInfra)
- 1 week: Create Ansible roles to replace Chef server deployment scripts
- 3-5 days: Documentation and knowledge transfer

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook for deploying a secure Apache web server with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache configuration, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook for fixing SSL vulnerabilities in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **ssh_profile**:
    - Description: Chef InSpec profile for validating SSH security configurations
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login validation, compliance with security standards

- **website_https_verify**:
    - Description: Chef InSpec profile for validating HTTPS website deployment
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port validation, HTTPS response validation, SSL protocol validation

- **chef-automate-deploy**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Shell Script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Shell script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Shell Script
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for website deployment testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Molecule with TestInfra for infrastructure testing
  - Option 2: Use Ansible's assert module for basic validation
  - Option 3: Keep InSpec but run it from Ansible using the command module

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible-specific test runners

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: AWX/Ansible Tower for web UI and job scheduling
  - Option 2: Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL Certificate Management**: 
  - Current approach uses Ansible's openssl modules to generate self-signed certificates
  - Migration should maintain or improve this approach, possibly using ansible.crypto collection

- **SSH Security Hardening**:
  - Current InSpec tests validate SSH root login is disabled
  - Migration should include Ansible tasks to enforce this configuration and validate it

- **Apache SSL Configuration**:
  - Current playbook disables insecure SSL protocols
  - Migration should maintain this security practice using Ansible's template module

- **Vault/secrets management**:
  - Hardcoded credentials in shell scripts (username, password)
  - Migration should use Ansible Vault to secure these credentials
  - 2 credential sets identified in shell scripts (username/password)

### Technical Challenges

- **InSpec Test Conversion**: 
  - Challenge: Converting InSpec's domain-specific language to TestInfra or other Ansible-compatible testing
  - Mitigation: Create a mapping of InSpec resources to TestInfra methods or Ansible modules

- **Compliance Validation**: 
  - Challenge: Maintaining compliance validation capabilities without InSpec
  - Mitigation: Evaluate OpenSCAP integration with Ansible or similar compliance tools

- **Chef Server Deployment**:
  - Challenge: Replacing Chef server deployment scripts with Ansible
  - Mitigation: Create Ansible roles that perform equivalent setup, possibly using the community.general.chef_* modules for transition period

### Migration Order

1. **website_https playbook** (already Ansible, low risk)
   - Review and refactor according to Ansible best practices
   - Convert to role-based structure if appropriate

2. **poodle_fix playbook** (already Ansible, low risk)
   - Review and refactor according to Ansible best practices
   - Consider merging with website_https role if appropriate

3. **InSpec tests** (medium complexity)
   - Convert to Molecule/TestInfra or Ansible assertions
   - Ensure all compliance checks are maintained

4. **Chef server deployment scripts** (high complexity)
   - Create Ansible playbooks to replace shell scripts
   - Implement Ansible Vault for credential management

### Assumptions

1. The primary goal is to standardize on Ansible and eliminate Chef dependencies
2. InSpec tests need to be converted to Ansible-compatible testing frameworks
3. The deployment scripts are used for setting up Chef infrastructure that will be replaced by Ansible infrastructure
4. The target environment will remain Ubuntu 20.04 on Vagrant VMs
5. No external Chef cookbooks or dependencies are being used beyond what's visible in the repository
6. The security compliance requirements represented in the InSpec tests must be maintained in the Ansible solution