# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a demonstration environment that combines Chef InSpec for compliance testing with Ansible playbooks for configuration management. The migration scope is relatively small, focusing on:

1. Two Ansible playbooks that configure Apache HTTPS and implement SSL security fixes
2. Two Chef InSpec profiles for compliance testing of SSH security and HTTPS functionality
3. Two Chef deployment scripts for setting up Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on replacing Chef InSpec profiles with Ansible-native testing solutions while preserving the existing Ansible playbooks.

## Module Migration Plan

This repository contains a mix of Ansible playbooks, Chef InSpec profiles, and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS, generates self-signed certificates, and deploys a simple "Hello World" website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache virtual host configuration, website deployment

- **poodle_fix**:
    - Description: Ansible playbook that mitigates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2 in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, STIG compliance check (SRG-OS-000112)

- **website_https_verify**:
    - Description: Chef InSpec profile that verifies HTTPS functionality and SSL/TLS protocol security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL/TLS protocol verification

- **deploy-automate**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server on a VM
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **deploy-chef-server**:
    - Description: Bash script that deploys Chef Infra Server (without Automate) on a VM
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `README.md`: Repository overview, pointing to Chef.io blog content
- `chef-and-ansible/README.md`: Description of the Chef InSpec with Ansible integration examples

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu (inferred from apt package manager usage in Ansible playbooks)
- **Virtual Machine Technology**: Not specified (deployment scripts are generic and could work with any VM platform)
- **Cloud Platform**: Not specified (no cloud-specific configurations found)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Migrate `ssh_profile.rb` to Ansible Lint rules or Molecule tests
  - Migrate `website_https_verify.rb` to Ansible URI module checks in a verification playbook

- **Chef Automate/Infra Server**: Replace with Ansible alternatives:
  - Replace `deploy-automate.sh` with Ansible AWX/Tower deployment playbook
  - Replace `deploy-chef-server.sh` with Ansible AWX/Tower deployment playbook

### Security Considerations

- **SSL/TLS Configuration**: Preserve the security hardening in `poodle_fix.yml` that disables SSLv3 and enables only TLSv1.2
- **SSH Security**: Maintain the SSH root login restriction verified by `ssh_profile.rb`
- **Self-signed Certificates**: Consider replacing with Let's Encrypt integration for production environments
- **Vault/secrets management**: 
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` (username, password) should be migrated to Ansible Vault
  - Total credentials detected: 2 sets of hardcoded credentials in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach may require additional logic
  - Mitigation: Use Ansible's assert module with custom conditions to replicate InSpec tests
  
- **Compliance Reporting**: InSpec provides built-in compliance reporting that needs to be replicated
  - Mitigation: Implement custom reporting using Ansible's callback plugins or integrate with AWX/Tower reporting

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format
   - Review and update to current Ansible best practices
   - Implement idempotency improvements if needed
   
2. **InSpec Profiles** (ssh_profile.rb, website_https_verify.rb): Moderate complexity
   - Convert to Ansible verification playbooks
   - Implement equivalent compliance checks using Ansible modules
   
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity
   - Convert to Ansible roles for infrastructure deployment
   - Replace Chef Automate/Infra Server with Ansible AWX/Tower
   - Secure credentials using Ansible Vault

### Assumptions

1. The existing Ansible playbooks are functional and follow best practices
2. The InSpec profiles are used for post-deployment verification rather than continuous compliance
3. The deployment scripts are used for initial setup rather than ongoing management
4. No external Chef cookbooks or complex Chef-managed infrastructure exists beyond what's in this repository
5. The target environment will continue to use Ubuntu or a Debian-based distribution
6. The migration will replace Chef InSpec with Ansible-native testing while preserving the security checks
7. The Chef Automate and Chef Infra Server deployment will be replaced with Ansible AWX/Tower