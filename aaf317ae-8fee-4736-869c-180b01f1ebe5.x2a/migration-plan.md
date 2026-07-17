# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests that demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The repository also includes Chef server deployment scripts that need to be converted to Ansible roles. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components and the fact that some components are already in Ansible format.

## Module Migration Plan

This repository contains Ansible playbooks, Chef InSpec tests, and Chef server deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that hardens SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (SRG-OS-000112)

- **deploy-automate**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **deploy-chef-server**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML test file used by the website_https playbook. No migration needed as it's a static content file.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and package versions in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen (latest)**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible roles that can:
  - Configure equivalent functionality using open-source tools
  - Or deploy Chef components if they must be retained

### Security Considerations

- **SSL Configuration**: The poodle_fix.yml playbook enforces TLSv1.2 and disables older protocols. Migration should maintain or enhance this security posture.
  - Migration approach: Preserve the same SSL hardening in Ansible roles

- **SSH Hardening**: The ssh_profile.rb test verifies SSH root login is disabled.
  - Migration approach: Create equivalent Ansible tests and ensure SSH hardening role is applied

- **Vault/secrets management**: 
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks.
  - Mitigation: Create custom Ansible modules or use community modules that provide similar testing capabilities

- **Chef Server Deployment**: Replacing Chef server deployment scripts with equivalent Ansible roles.
  - Mitigation: Evaluate if Chef server is still needed or if complete migration to Ansible automation is preferred

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they're already in Ansible format, may need minor updates for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Moderate complexity to convert to Ansible-compatible testing
3. **Chef Server Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - High complexity, requires designing equivalent Ansible roles

### Assumptions

1. The primary goal is to standardize on Ansible as the configuration management tool while maintaining the same functionality
2. The Chef InSpec tests are used for compliance validation and need to be preserved in some form
3. The deployment scripts for Chef Automate and Chef Infra Server may be replaced with equivalent Ansible roles or eliminated if Chef is being fully replaced
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. Test Kitchen is used for development and testing but will be replaced with Ansible-native testing tools
6. No external data sources or integrations are present beyond what's visible in the repository
7. The hardcoded credentials in the deployment scripts are for testing purposes only and will be replaced with secure credential management