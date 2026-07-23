# MIGRATION FROM MIXED ANSIBLE/CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks with Chef InSpec tests and Chef deployment scripts. The migration scope is relatively small, focusing on consolidating the existing Ansible playbooks and converting the Chef deployment scripts to Ansible. The estimated timeline for this migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support, including self-signed certificate generation and virtual host configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses SSL POODLE vulnerability by disabling older SSL protocols and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server on a VM
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server (without Automate) on a VM
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with Vagrant and InSpec
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML file used by the website_https playbook

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml and Apache package version)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (latest)**: Replace with Ansible Molecule for testing
- **InSpec (latest)**: Replace with Ansible-compatible testing frameworks:
  - For compliance testing: Replace with ansible-lint or integrate with OpenSCAP
  - For functional testing: Replace with Molecule's built-in testing capabilities or pytest-ansible

### Security Considerations

- **SSL/TLS Configuration**: The poodle_fix.yml playbook enforces TLSv1.2 only. This should be updated to include TLSv1.3 in the Ansible migration.
- **SSH Hardening**: The ssh_profile.rb InSpec test checks for SSH root login disablement. This security check should be incorporated into the Ansible playbooks.
- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh (username, password)
  - Self-signed certificates in website_https.yml
  - Migration should use Ansible Vault for credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks will require mapping InSpec resources to equivalent Ansible modules or assertions.
- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible will require understanding the Chef server installation process and translating it to Ansible tasks.

### Migration Order

1. **website_https playbook** (low risk, already in Ansible format)
2. **poodle_fix playbook** (low risk, already in Ansible format)
3. **InSpec tests** (moderate complexity, requires conversion to Ansible testing framework)
4. **Chef deployment scripts** (high complexity, requires complete rewrite in Ansible)

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or newer.
2. The current SSL/TLS configuration meets security requirements but may need updating for newer protocols.
3. The Chef deployment scripts are used for setting up test environments and not production infrastructure.
4. The InSpec tests are used primarily for validation and compliance checking.
5. No external Chef cookbooks or recipes are being used beyond what's in the repository.
6. The migration will consolidate all components to pure Ansible without maintaining Chef components.