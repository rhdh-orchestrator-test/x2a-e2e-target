# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together for compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, with minimal complexity due to the limited scope of Chef components that need migration.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https_verify**:
    - Description: InSpec tests for verifying HTTPS website configuration including port listening, content verification, and SSL/TLS protocol validation
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port testing, HTTP response validation, SSL/TLS protocol verification

- **ssh_profile**:
    - Description: InSpec compliance profile for SSH security configuration focusing on root login restrictions
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, CCI compliance mapping, STIG validation

- **website_https_deployment**:
    - Description: Ansible playbook for deploying an HTTPS website with Apache2, self-signed certificates, and proper configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook for remediating POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef_automate_deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef_server_deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Sample HTML file used for testing website deployment. Can be preserved as-is or incorporated into Ansible templates.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Implement Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing and verification

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that configure equivalent functionality:
  - For compliance scanning: Consider AWX/Ansible Tower with custom scanning roles
  - For configuration management: Native Ansible with AWX/Tower for orchestration

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening that disables SSLv3 and enables only TLSv1.2
  - Migration approach: Convert the InSpec tests to Ansible assert tasks that verify the same security controls

- **SSH Security**: The SSH root login restriction tests must be preserved
  - Migration approach: Create an Ansible role with both configuration and verification tasks

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup scripts (username, password)
  - Migration strategy: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Compliance Testing**: InSpec provides rich testing capabilities that may be challenging to replicate with Ansible's built-in modules
  - Mitigation: Consider using a combination of Ansible assert, custom modules, and external tools like Molecule

- **STIG Compliance**: The SSH profile includes STIG compliance tags and CCI references
  - Mitigation: Ensure these compliance mappings are preserved in documentation or as Ansible tags/metadata

- **Self-signed Certificates**: The current implementation generates self-signed certificates
  - Mitigation: Use Ansible's crypto modules to replicate this functionality while providing an option to use proper CA-signed certificates

### Migration Order

1. **InSpec Tests to Ansible Tests** (Priority 1, low risk)
   - Convert website_https_verify.rb to Ansible assert tasks
   - Convert ssh_profile.rb to Ansible assert tasks

2. **Chef Deployment Scripts to Ansible Playbooks** (Priority 2, moderate complexity)
   - Create Ansible playbooks to replace deploy-automate.sh and deploy-chef-server.sh
   - Implement Ansible Vault for credential storage

3. **Test Kitchen to Molecule** (Priority 3, moderate complexity)
   - Replace kitchen.yml with Molecule configuration
   - Ensure all tests run correctly in the new environment

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) will be preserved as-is and do not require migration
2. The primary goal is to replace Chef InSpec testing with Ansible-native testing solutions
3. The deployment scripts for Chef Automate and Chef Infra Server need to be replaced with equivalent Ansible functionality
4. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs
5. No external dependencies or integrations beyond what's visible in the repository need to be considered
6. The hardcoded credentials in the deployment scripts are for testing purposes only and will be replaced with secure alternatives
7. The compliance requirements (STIG, CCI) need to be preserved in the migrated solution