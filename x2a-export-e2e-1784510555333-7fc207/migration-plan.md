# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Main directory containing Ansible playbooks and InSpec tests
    - Path: chef-and-ansible
    - Technology: Mixed (Ansible playbooks and Chef InSpec)
    - Key Features: Website HTTPS configuration, SSL security, compliance testing
    - Components:
      - website_https.yml: Ansible playbook for Apache HTTPS setup
      - poodle_fix.yml: Ansible playbook for SSL vulnerability remediation
      - tests/: Directory containing InSpec test files

- **setup-automate**:
    - Description: Directory containing Chef deployment scripts
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef Automate and Chef Infra Server deployment
    - Components:
      - deploy-automate.sh: Script for deploying Chef Automate and Chef Infra Server
      - deploy-chef-server.sh: Script for deploying Chef Infra Server only

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/index.html`: Sample HTML file for website testing
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec tests for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance
- `setup-automate/deploy-automate.sh`: Shell script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Shell script for deploying Chef Infra Server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Integrate with Ansible Automation Platform's compliance capabilities
  - Option 3: Keep InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - ansible-test for collection testing

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible playbooks for deploying alternative compliance platforms
  - Consider AWX/Ansible Tower as a replacement for Chef Automate's functionality

### Security Considerations

- **SSL Configuration**: Maintain the security improvements from poodle_fix.yml
  - Ensure TLSv1.2 or higher is enforced
  - Disable vulnerable protocols

- **SSH Security**: Preserve the SSH hardening checks
  - Migrate the InSpec SSH profile to Ansible security roles
  - Consider using ansible-lockdown or similar security roles

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - SSL certificates generated in the playbook
  - Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Migration**: Converting InSpec tests to equivalent Ansible verification
  - Solution: Use assert modules in Ansible or integrate with a testing framework like Molecule

- **Compliance Reporting**: Replacing Chef Automate's compliance reporting
  - Solution: Consider integrating with Ansible Automation Platform's compliance capabilities or a third-party tool

### Migration Order

1. Ansible Playbooks (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
2. Deployment Scripts (deploy-automate.sh, deploy-chef-server.sh) - Medium complexity
3. InSpec Tests (website_https_verify.rb, ssh_profile.rb) - Higher complexity due to testing framework differences

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are a critical component that must be preserved in some form
3. The deployment scripts are for setting up a test environment and not production infrastructure
4. There are no external dependencies or integrations beyond what's visible in the repository
5. The target environment will continue to be Ubuntu 20.04 or compatible
6. No state data or databases need to be migrated
7. The migration will consolidate to pure Ansible without maintaining Chef components