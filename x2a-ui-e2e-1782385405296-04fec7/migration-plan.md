# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on compliance automation and Chef server deployment. The migration scope is relatively small, with two main components:

1. A Chef InSpec compliance testing framework used alongside Ansible playbooks
2. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **LOW to MEDIUM** as most of the Ansible components can be retained with minimal changes, while the Chef InSpec tests need to be converted to Ansible-native solutions. The Chef server deployment scripts need to be completely replaced.

**Estimated Timeline**: 1-2 weeks for a complete migration

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL module configuration, service restart handlers

- **compliance_tests**:
    - Description: Chef InSpec tests for validating HTTPS configuration and SSH security settings
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTP response validation, SSL protocol verification, SSH configuration validation

- **chef_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts
    - Key Features: Chef server installation, user and organization creation, system configuration

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework
- `index.html`: Sample HTML file used for testing - can be retained as-is or incorporated into Ansible templates

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For infrastructure testing: Use Ansible Molecule for testing playbooks
  - For compliance testing: Use ansible-lint with custom rules or integrate with OpenSCAP
  
- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure code

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower for centralized management or consider other configuration management approaches

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Approach: Preserve the same SSL protocol restrictions in the migrated Ansible roles
  
- **SSH Hardening**: The SSH security controls tested by InSpec need to be implemented in Ansible
  - Approach: Create an Ansible role that applies the same SSH hardening configurations

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **Compliance Testing**: Converting InSpec tests to Ansible-native testing frameworks
  - Mitigation: Use Ansible assert modules or integrate with tools like OpenSCAP for compliance testing
  
- **Certificate Management**: Ensuring secure certificate generation and management
  - Mitigation: Use Ansible's crypto modules with proper secret management via Ansible Vault

- **Chef Server Replacement**: Determining the appropriate replacement for Chef Server functionality
  - Mitigation: Evaluate whether Ansible AWX/Tower meets the requirements or if additional tools are needed

### Migration Order

1. **website_https.yml** (Priority 1 - low risk, already Ansible)
   - Minimal changes needed, mainly refactoring into proper Ansible role structure
   
2. **poodle_fix.yml** (Priority 1 - low risk, already Ansible)
   - Minimal changes needed, can be incorporated into the website_https role
   
3. **compliance_tests** (Priority 2 - moderate complexity)
   - Convert InSpec tests to Ansible assertions or Molecule tests
   
4. **chef_deployment** (Priority 3 - high complexity)
   - Replace with Ansible playbooks for setting up Ansible AWX/Tower or alternative management platform

### Assumptions

1. The primary purpose of this repository is for demonstration/examples rather than production use
2. The InSpec tests are used for validation of infrastructure rather than continuous compliance monitoring
3. There is no dependency on Chef-specific resources that cannot be replicated in Ansible
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only
5. There are no external dependencies on Chef Automate features that would require additional tools beyond Ansible
6. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
7. The migration does not need to preserve Test Kitchen functionality as it will be replaced with Ansible-native testing