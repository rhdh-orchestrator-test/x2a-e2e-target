# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be migrated to a unified Ansible approach. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for configuring web servers with HTTPS
3. InSpec tests for compliance verification

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **2-3 weeks**. The primary focus will be on converting Chef server deployment scripts to Ansible playbooks while preserving the existing compliance testing framework.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring Apache web servers with HTTPS and InSpec tests for compliance verification
    - Path: chef-and-ansible
    - Technology: Ansible + Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL certificate generation, InSpec compliance testing for HTTPS and SSH security

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash + Chef
    - Key Features: Chef server deployment, user and organization creation, system configuration for Chef Automate

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should replace this with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS. Can be preserved with minor updates to align with current Ansible best practices.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be preserved with minor updates.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Can be preserved as Ansible supports InSpec for compliance testing.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Can be preserved as Ansible supports InSpec for compliance testing.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Needs to be converted to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs to be converted to Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version 2.4.41-4ubuntu3.10)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
  - Current version: Latest (downloaded dynamically in scripts)
  - Migration: Create Ansible role for server configuration management
- **Chef Server**: Replace with Ansible AWX/Tower or alternative configuration management approach
  - Current version: Latest (downloaded dynamically in scripts)
  - Migration: Implement Ansible inventory and collection management
- **InSpec**: Preserve InSpec for compliance testing, as it's compatible with Ansible workflows
  - Current version: Not specified, but compatible with Test Kitchen
  - Migration: Integrate with Ansible using the ansible_inspec module or as a separate verification step
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
  - Current version: Not specified
  - Migration: Create equivalent Molecule scenarios for testing

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in `poodle_fix.yml` that disables vulnerable SSL protocols
  - Migration approach: Convert to Ansible lineinfile or template module with identical regex pattern
- **SSH Security**: The SSH compliance profile in `ssh_profile.rb` must be maintained to ensure SSH root login remains disabled
  - Migration approach: Create equivalent Ansible task to enforce SSH configuration and maintain InSpec test
- **Vault/secrets management**:
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` (username, password) should be moved to Ansible Vault
    - Count: 5 credentials (username, longusername, useremail, userpassword, orgname)
  - SSL certificates are generated dynamically in the playbook, which is a good practice to maintain
    - Migration approach: Use Ansible's openssl_* modules as already implemented in website_https.yml

### Technical Challenges

- **Chef Server Replacement**: Determining whether to replace Chef Server functionality with Ansible AWX/Tower or another solution
  - Mitigation: Evaluate organization needs for a web UI and role-based access control to determine if AWX/Tower is necessary
  - Complexity: Medium - requires architectural decision and potential new infrastructure
- **InSpec Integration**: Ensuring InSpec tests continue to work with the new Ansible-only approach
  - Mitigation: Use Ansible's built-in support for InSpec or convert tests to Ansible assertions where appropriate
  - Complexity: Low - InSpec is already compatible with Ansible workflows
- **Configuration Drift Detection**: Chef provides built-in configuration drift detection that needs to be replicated in Ansible
  - Mitigation: Implement regular Ansible runs with check mode and reporting to detect configuration drift
  - Complexity: Medium - requires operational process changes

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Update existing playbooks to follow current Ansible best practices
   - Convert Test Kitchen configuration to Ansible Molecule

2. **InSpec Tests** (Low risk, compatible with Ansible)
   - Preserve InSpec tests and integrate with Ansible workflows
   - Update test references if necessary

3. **Chef Server Deployment Scripts** (Medium complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement secure credential management with Ansible Vault
   - Test deployment in isolated environment

### Assumptions

1. The organization is moving away from Chef as the primary configuration management tool and standardizing on Ansible.
2. InSpec will continue to be used for compliance testing, as it's compatible with Ansible workflows.
3. The existing Ansible playbooks (`website_https.yml` and `poodle_fix.yml`) are working correctly and only need minor updates.
4. The Chef Automate and Chef Infra Server deployment scripts are being used for on-premises or cloud VM deployments.
5. There is no complex Chef cookbook logic that needs to be migrated, as the repository only contains deployment scripts.
6. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
7. The hardcoded credentials in the deployment scripts are for testing purposes and will be replaced with secure credential management in production.
8. The organization has the necessary expertise to work with both Ansible and InSpec for compliance testing.
9. The migration will not require changes to the underlying infrastructure or operating systems.