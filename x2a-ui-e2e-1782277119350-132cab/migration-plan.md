# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for compliance verification
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all configuration management.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling older SSL protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **inspec-website-verification**:
    - Description: Chef InSpec profile for verifying HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening tests, HTTPS content verification, SSL protocol security checks

- **inspec-ssh-compliance**:
    - Description: Chef InSpec profile for SSH security compliance verification
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization setup

- **chef-server-deployment**:
    - Description: Shell script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Integrate with ansible-lint for security checks
  - Option 3: Keep InSpec as a standalone testing tool but invoke from Ansible

- **Test Kitchen**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for environment provisioning and testing
  - Option 2: Use Vagrant directly with Ansible provisioner

- **Chef Automate/Server**: Replace with Ansible automation platform:
  - Option 1: Migrate to AWX/Ansible Tower for web UI and job scheduling
  - Option 2: Use Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Approach: Convert to Ansible role with appropriate handlers and idempotent configuration

- **Compliance Testing**: The InSpec tests contain security checks that must be preserved
  - Approach: Either convert InSpec tests to Ansible assert tasks or maintain InSpec as a testing tool called from Ansible

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates and keys should use Ansible Vault or external secret management
  - Document the count and type of credentials detected per module:
    - chef-automate-deployment: 3 credentials (username, password, organization name)
    - chef-server-deployment: 3 credentials (username, password, organization name)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Consider using Ansible's assert module or maintaining InSpec as a separate tool

- **Compliance Metadata**: InSpec tests contain rich compliance metadata (STIG IDs, CCI references)
  - Mitigation: Preserve this metadata in Ansible task documentation or use custom Ansible modules

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate testing
  - Mitigation: Replace with Ansible Molecule or direct Vagrant integration

### Migration Order

1. **website-https playbook** (low risk, already in Ansible)
   - Convert to Ansible role structure
   - Improve idempotence and variable usage

2. **poodle-fix playbook** (low risk, already in Ansible)
   - Convert to Ansible role structure
   - Integrate with website-https role

3. **InSpec tests** (moderate complexity)
   - Either convert to Ansible assert tasks or maintain as separate tool
   - Ensure compliance metadata is preserved

4. **Chef deployment scripts** (high complexity)
   - Replace with Ansible playbooks for AWX/Tower deployment
   - Use Ansible Vault for credential management

### Assumptions

1. The primary goal is to standardize on Ansible while maintaining the compliance testing capabilities
2. The InSpec tests are valuable and should be preserved in some form
3. The deployment scripts for Chef Automate/Server will be replaced with equivalent Ansible automation platform deployment
4. The target environment will continue to be Ubuntu 20.04 or compatible
5. The Vagrant/Test Kitchen testing workflow is important to preserve in some form
6. No external data sources or integrations beyond what's visible in the repository
7. The hardcoded credentials in the deployment scripts are examples and not production values