# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains Chef-related examples and deployment scripts rather than traditional Chef cookbooks. The primary content consists of Ansible playbooks demonstrating Chef InSpec integration, deployment scripts for Chef infrastructure, and compliance testing examples. The migration scope is limited as most content is already in Ansible format or consists of infrastructure deployment scripts.

## Module Migration Plan

This repository contains mixed technologies that need individual migration planning:

### MODULE INVENTORY

**website-https-demo**:
- Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed SSL certificates, virtual host setup, and SSL protocol hardening
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL/TLS security hardening

**poodle-ssl-fix**:
- Description: Ansible playbook for SSL protocol hardening to disable SSLv3 and enforce TLS 1.2 only (POODLE vulnerability mitigation)
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL configuration replacement, TLS protocol enforcement, service restart handling

**chef-automate-deployment**:
- Description: Bash script for automated deployment of Chef Automate and Chef Infra Server with user and organization setup
- Path: setup-automate/deploy-automate.sh
- Technology: Bash Shell Script
- Key Features: Hostname configuration, system tuning, Chef Automate CLI deployment, user/org creation

**chef-server-deployment**:
- Description: Bash script for standalone Chef Infra Server deployment without Automate components
- Path: setup-automate/deploy-chef-server.sh
- Technology: Bash Shell Script
- Key Features: Chef Infra Server installation, system configuration, user management setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with Vagrant driver and InSpec verification
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality, SSL protocol verification, and port accessibility
- `tests/ssh_profile.rb`: InSpec security profile for SSH root login compliance (STIG control SRG-OS-000112)
- `index.html`: Static HTML test content for web server verification
- `README.md` files: Documentation for Chef InSpec and Ansible integration examples

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

- **apache2 (2.4.41-4ubuntu3.10)**: Already using Ansible apt module for package management
- **openssl**: Certificate generation handled by Ansible openssl_* modules
- **python3-openssl**: Required for Ansible OpenSSL certificate modules
- **curl**: System utility for package downloads and testing
- **Chef Automate CLI**: Downloaded and executed via curl in deployment scripts

### Security Considerations

- **SSL/TLS Configuration**: Both playbooks implement proper SSL security practices:
  - Self-signed certificate generation with proper key management
  - SSL protocol hardening (disabling SSLv3, enforcing TLS 1.2)
  - Certificate file permissions (0640 for sensitive files)
- **SSH Security**: InSpec profile enforces SSH root login restrictions per STIG requirements
- **Credential Management**: 
  - Deployment scripts contain hardcoded credentials (username: 'jtonello', password: 'password')
  - SSL private keys generated locally without external secret management
  - No vault or encrypted data bag usage detected

### Technical Challenges

- **Mixed Technology Stack**: Repository combines Ansible playbooks, Bash scripts, and InSpec tests requiring different migration strategies
- **Hardcoded Credentials**: Deployment scripts contain plaintext passwords and configuration values that need externalization
- **Test Kitchen Integration**: Current testing framework uses Chef's Test Kitchen with InSpec - may need migration to Ansible testing tools
- **Chef Infrastructure Dependencies**: Deployment scripts rely on Chef Automate CLI and specific Chef server components

### Migration Order

1. **Ansible Playbooks** (already complete - no migration needed)
   - website_https.yml and poodle_fix.yml are already in Ansible format
2. **InSpec Test Migration** (moderate complexity)
   - Convert InSpec tests to Ansible testing framework or maintain hybrid approach
3. **Deployment Script Migration** (high complexity)
   - Convert Bash deployment scripts to Ansible playbooks for Chef infrastructure setup
   - Externalize hardcoded credentials using Ansible Vault

### Assumptions

- The repository serves as an example/demo collection rather than production infrastructure code
- Current Ansible playbooks are functional and don't require migration (they demonstrate Chef InSpec integration)
- Ubuntu 20.04 target environment will be maintained for compatibility
- Test Kitchen with InSpec integration may be preserved for compliance testing workflows
- Chef infrastructure deployment scripts may need to remain as-is if they're specifically for Chef server provisioning
- Hardcoded credentials in deployment scripts are acceptable for demo purposes but should be externalized for production use
- The mixed Ansible/Chef InSpec approach is intentional for demonstrating compliance automation integration