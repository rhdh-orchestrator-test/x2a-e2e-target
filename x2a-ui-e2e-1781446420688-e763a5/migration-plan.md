# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks with Chef InSpec tests for compliance automation

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on converting the Chef Automate deployment scripts to Ansible playbooks while preserving the existing Ansible playbooks and adapting the InSpec tests to work within a pure Ansible workflow.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

- **website-https-configuration**:
    - Description: Ansible playbook for configuring Apache web server with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **ssl-poodle-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **compliance-testing**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH root login testing

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for testing web server configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuring equivalent monitoring and compliance solutions
- **Chef InSpec**: Migrate to Ansible-native testing frameworks like Molecule or maintain InSpec as a standalone tool
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Migration approach: Maintain the same configuration but use Ansible's template module instead of replace
  
- **SSH Security**: Maintain the SSH root login restrictions tested by the InSpec profile
  - Migration approach: Create an Ansible task to enforce the same SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - SSL certificates and keys
  - Migration approach: Replace hardcoded credentials with Ansible Vault

### Technical Challenges

- **Chef InSpec Integration**: Determining how to integrate Chef InSpec tests with a pure Ansible workflow
  - Mitigation strategy: Either maintain InSpec as a standalone tool or migrate tests to Ansible-native testing frameworks

- **Chef Automate Functionality**: Ensuring all Chef Automate functionality is properly replaced
  - Mitigation strategy: Map Chef Automate features to equivalent open-source tools that can be managed with Ansible

### Migration Order

1. Chef deployment scripts (setup-automate/) - high priority, moderate complexity
   - Convert to Ansible roles for deploying alternative compliance and monitoring solutions
   
2. InSpec tests (chef-and-ansible/tests/) - medium priority, low complexity
   - Either maintain as-is or convert to Ansible-native testing

3. Existing Ansible playbooks (chef-and-ansible/*.yml) - low priority, low complexity
   - Already in Ansible format, may need minor adjustments for consistency

### Assumptions

1. The primary goal is to eliminate Chef dependencies while maintaining the same functionality
2. The existing Ansible playbooks are working correctly and don't need significant changes
3. Test Kitchen can be replaced with Molecule for testing Ansible playbooks
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only
5. The target environment will continue to be Ubuntu 20.04 or compatible
6. The InSpec tests are essential and must be preserved in some form
7. The repository is primarily for demonstration/educational purposes rather than production use