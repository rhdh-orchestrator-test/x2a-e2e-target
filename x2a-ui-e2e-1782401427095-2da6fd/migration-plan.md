# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used for compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on:

1. Preserving the compliance testing capabilities currently provided by Chef InSpec
2. Maintaining the existing Ansible playbooks with minimal changes
3. Migrating the Chef Automate and Chef Infra Server deployment scripts to Ansible

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited scope and the fact that most of the configuration is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `index.html`: Simple HTML file used as a test page. Can be preserved as-is or incorporated into Ansible templates.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use the `ansible.builtin.assert` module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing (recommended)
  - Option 4: Maintain InSpec as a separate tool called from Ansible

- **Test Kitchen**: Replace with Molecule for testing Ansible roles and playbooks

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Approach: Convert the existing Ansible playbook to an Ansible role with proper documentation
  
- **SSH Security Controls**: The SSH root login compliance check must be maintained
  - Approach: Convert the InSpec control to an Ansible assert task or Molecule test

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely using Ansible Vault or external certificate management

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions
  
- **Maintaining Compliance Standards**: The current InSpec tests include STIG references and compliance metadata
  - Mitigation: Document compliance mappings and ensure they're preserved in Ansible tests

- **Chef Automate Functionality**: The Chef Automate deployment provides compliance reporting that needs an alternative
  - Mitigation: Evaluate Ansible AWX/Tower for compliance reporting or integrate with other compliance tools

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format
   - Convert to proper Ansible roles with variables, templates, and handlers
   - Improve idempotence and follow Ansible best practices
   
2. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Moderate complexity
   - Convert Bash scripts to Ansible playbooks
   - Use Ansible Vault for credential management
   
3. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): High complexity
   - Convert to Ansible-native testing framework
   - Preserve compliance metadata and assertions

### Assumptions

1. The primary goal is to eliminate Chef dependencies while maintaining the same functionality
2. Compliance testing is a critical requirement that must be preserved
3. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
4. The self-signed certificates are for testing only and not production use
5. The hardcoded credentials in the deployment scripts are not used in production
6. There is no external dependency on Chef Automate for compliance reporting that must be replaced
7. The migration will follow Ansible best practices including the use of roles, collections, and proper variable management