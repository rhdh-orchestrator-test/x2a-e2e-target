# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec profiles and Ansible playbooks that are used together to demonstrate compliance automation. The repository also includes shell scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec profiles to Ansible-compatible compliance solutions
2. Consolidating existing Ansible playbooks
3. Replacing Chef Automate/Infra Server deployment scripts with Ansible equivalents

**Estimated Timeline**: 2-3 weeks for a small team (1-2 engineers)
**Complexity**: Medium - The repository contains a limited number of files, but requires careful handling of compliance controls and security configurations

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec profile that verifies HTTPS configuration on a website
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance controls with STIG references

- **automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `chef-and-ansible/index.html`: Simple HTML file, can be directly used in Ansible content.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint with custom rules for compliance checks
  - Option 2: Integrate with OpenSCAP using the ansible-collection-compliance collection
  - Option 3: Convert InSpec profiles to Ansible assert modules or custom modules

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for orchestration
  - Ansible Collections for configuration management
  - Compliance as Code using ansible-lint or OpenSCAP

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration must maintain:
  - Self-signed certificate generation
  - Proper SSL protocol configuration (TLSv1.2 enforcement)
  - Disabling vulnerable protocols (SSLv3)

- **SSH Hardening**: The InSpec profile checks for SSH root login being disabled. Migration must:
  - Maintain compliance checks for SSH configuration
  - Preserve STIG compliance references and documentation

- **Credentials Management**: 
  - The deployment scripts contain hardcoded credentials that should be moved to Ansible Vault
  - Credentials detected: 1 user password in each deployment script

### Technical Challenges

- **InSpec to Ansible Conversion**: Converting InSpec tests to equivalent Ansible checks requires careful mapping of resources and assertions. Mitigation: Create a mapping document for InSpec resources to Ansible modules.

- **Compliance Metadata**: The InSpec profiles contain rich compliance metadata (STIG IDs, CCI references) that must be preserved. Mitigation: Use Ansible role metadata or documentation to maintain compliance references.

- **Test Framework**: Replacing Test Kitchen with Molecule requires reconfiguration of test scenarios. Mitigation: Create equivalent Molecule scenarios that match the existing Test Kitchen configuration.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, just need consolidation and best practices applied
2. **InSpec Profiles** (website_https_verify.rb, ssh_profile.rb): Medium complexity, requires conversion to Ansible-compatible testing
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity, requires complete rewrite as Ansible roles

### Assumptions

1. The repository is primarily used for demonstration/educational purposes rather than production, based on the README description.
2. The InSpec profiles are used alongside Ansible for compliance validation rather than configuration management.
3. The deployment scripts are used for setting up Chef infrastructure, which will be replaced with Ansible infrastructure.
4. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration.
5. The SSL and SSH configurations are critical security components that must be maintained in the migration.
6. The repository does not contain actual Chef cookbooks or recipes that need migration.
7. Test Kitchen is used for testing the Ansible playbooks with InSpec verification.