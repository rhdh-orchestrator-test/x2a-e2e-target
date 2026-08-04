# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef setup scripts and Ansible playbooks focused on demonstrating Chef InSpec with Ansible for compliance automation. The migration scope is relatively small, consisting of two Ansible playbooks for web server configuration and a set of Chef Automate/Infra Server setup scripts. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains Chef setup scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Apache web server configuration with SSL/TLS setup, including self-signed certificate generation and virtual host configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Security fix for the POODLE vulnerability in SSL by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-setup**:
    - Description: Deployment script for Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-setup**:
    - Description: Deployment script for Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with Vagrant and InSpec verification
- `tests/website_https_verify.rb`: InSpec tests for verifying HTTPS website functionality and security
- `tests/ssh_profile.rb`: InSpec compliance profile for SSH security configuration
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - For compliance testing: Use ansible-lint with custom rules
  - For infrastructure testing: Use Molecule with testinfra or Ansible's assert module
  - For security scanning: Consider integration with OpenSCAP or DISA STIG tools

- **Chef Automate/Infra Server**: Replace with Ansible automation platform:
  - Ansible AWX/Tower for web UI, job scheduling, and inventory management
  - Ansible Galaxy for role sharing
  - Git repositories for playbook version control

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
  - Migration approach: Convert the Apache SSL configuration to an Ansible role with appropriate templates and handlers

- **Self-signed Certificates**: The current implementation generates self-signed certificates
  - Migration approach: Use Ansible's openssl_* modules (already in use) with proper certificate management

- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions
  - Migration approach: Create an Ansible role for SSH hardening that applies the same security controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible testing frameworks
  - Mitigation: Map InSpec resources to equivalent testinfra or Ansible assert statements
  - Example: InSpec's `describe port(443)` can be replaced with testinfra's `host.socket("tcp://0.0.0.0:443").is_listening`

- **Chef Server Functionality**: Replacing Chef Server's functionality with Ansible equivalents
  - Mitigation: Document the mapping between Chef Server concepts (cookbooks, roles, environments) and Ansible concepts (playbooks, roles, inventories)

### Migration Order

1. **website-https playbook** (low risk, already in Ansible format)
   - Only needs review and potential refactoring to follow Ansible best practices
   - Consider converting to a reusable role

2. **poodle-fix playbook** (low risk, already in Ansible format)
   - Consider merging with the website-https role as a security hardening task

3. **Chef Automate/Server setup scripts** (moderate complexity)
   - Convert bash scripts to Ansible playbooks for infrastructure setup
   - Replace Chef-specific commands with Ansible AWX/Tower setup tasks

4. **InSpec tests** (moderate complexity)
   - Convert to equivalent Ansible testing framework
   - Ensure all compliance checks are maintained

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are essential and need to be preserved in some form
3. The Chef setup scripts are used for setting up a test environment, not for production deployment
4. No external Chef cookbooks or roles are being used that would need migration
5. The target environment will continue to be Ubuntu 20.04 or compatible systems
6. The security requirements (TLS 1.2, SSH hardening) must be maintained in the migrated solution
7. No complex data bags or Chef environments are in use that would need migration