# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The repository also includes Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with a focus on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Preserving existing Ansible playbooks
3. Replacing Chef Automate and Chef Infra Server deployment scripts with Ansible equivalents

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository primarily contains Ansible playbooks already, with Chef InSpec tests and deployment scripts being the main migration targets.

## Module Migration Plan

This repository contains a mix of Ansible playbooks, Chef InSpec tests, and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to address the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality of the website
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTP response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance tagging (STIG, CCI)

- **automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be updated to use Ansible-native testing frameworks.
- `index.html`: Static HTML content for the website. Can be preserved as-is.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for both on-premises and cloud deployment (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule with testinfra for infrastructure testing
  - Option 2: Convert InSpec tests to Ansible assert tasks
  - Option 3: Use community.general.assert module for validation

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing Ansible roles and playbooks
  - Or continue using Test Kitchen with the kitchen-ansible plugin

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for web UI, job scheduling, and inventory management
  - Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure the migration preserves the security hardening (disabling SSLv3, enabling TLSv1.2).
- **SSH Hardening**: The InSpec tests check for SSH root login disablement. Ensure this security check is preserved in the Ansible testing framework.
- **Vault/secrets management**:
  - Hardcoded credentials in the deployment scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets (username/password) in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks may require learning new testing patterns and syntax.
  - Mitigation: Use Ansible's assert module or Molecule with testinfra for similar functionality.

- **Deployment Script Conversion**: The Chef Automate and Chef Infra Server deployment scripts contain specific configuration steps that need to be replicated in Ansible.
  - Mitigation: Create Ansible roles for Chef Automate and Chef Infra Server deployment, or replace with AWX/Ansible Tower deployment playbooks.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, may only need minor adjustments for best practices.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Medium complexity, convert to Ansible testing framework.
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity, convert to Ansible playbooks and roles.

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, based on the README content.
2. The Chef InSpec tests are used alongside Ansible playbooks to validate compliance, not as part of a larger Chef ecosystem.
3. The deployment scripts are used for setting up test environments, not for production deployments.
4. No external dependencies or integrations beyond what's visible in the repository.
5. The migration goal is to standardize on Ansible for both configuration management and compliance testing.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in production.