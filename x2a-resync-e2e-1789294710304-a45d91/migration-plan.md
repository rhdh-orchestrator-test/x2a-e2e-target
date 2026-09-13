# MIGRATION FROM CHEF TO ANSIBLE

This repository contains example code demonstrating Chef InSpec integration with Ansible rather than traditional Chef cookbooks requiring migration. The content is primarily educational/demonstration material showing how to achieve compliance automation using Ansible playbooks with InSpec verification. **No actual migration is required** as the Ansible playbooks are already in their target state.

## Module Migration Plan

This repository contains demonstration examples rather than production Chef modules:

### MODULE INVENTORY

**No Chef modules found for migration.** This repository contains:

- **website_https**: 
    - Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed certificates, SSL/TLS security hardening, and virtual host setup
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: OpenSSL certificate generation, Apache virtual host configuration, SSL module activation

- **poodle_fix**:
    - Description: Ansible playbook demonstrating SSL protocol hardening to disable vulnerable SSL 3.0 and enforce TLS 1.2
    - Path: chef-and-ansible/poodle_fix.yml  
    - Technology: Ansible (already migrated)
    - Key Features: Apache SSL configuration remediation, POODLE vulnerability mitigation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: InSpec compliance tests verifying HTTPS functionality and SSL protocol configuration
- `tests/ssh_profile.rb`: InSpec compliance profile for SSH security hardening verification
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static HTML test content for web server verification

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address

**No external Chef dependencies found.** The existing Ansible playbooks use standard modules:
- **apache2 (2.4.41-4ubuntu3.10)**: Already configured via apt module
- **openssl/python3-openssl**: Certificate management handled by ansible.builtin.openssl_* modules
- **curl**: Standard utility for testing and verification

### Security Considerations

The existing Ansible playbooks already implement security best practices:
- **SSL/TLS Configuration**: Self-signed certificate generation with proper key management, SSL 3.0 disabled, TLS 1.2 enforced
- **File Permissions**: Appropriate permissions set for certificate files (0640) and web content (0644/0755)
- **SSH Hardening**: InSpec profile includes SSH root login verification (PermitRootLogin disabled)
- **Vault/Secrets Management**: No hardcoded credentials found - uses Ansible variables and generated certificates

### Technical Challenges

**No migration challenges** - this is a demonstration repository showing:
- How to use Test Kitchen with Ansible instead of Chef
- Integration patterns between Ansible and Chef InSpec for compliance automation
- SSL/TLS security configuration examples

### Migration Order

**No migration required.** For teams using this as a reference:
1. Review existing Ansible playbook patterns for SSL configuration
2. Adapt InSpec compliance tests for your environment
3. Integrate Test Kitchen workflow for Ansible playbook testing

### Assumptions

- This repository serves as educational/demonstration content rather than production infrastructure code
- The Chef Automate deployment scripts are for setting up the Chef platform to run InSpec, not for migrating Chef cookbooks
- Teams referencing this content are learning how to integrate Chef InSpec with Ansible workflows
- The Test Kitchen configuration demonstrates testing Ansible playbooks with InSpec verification rather than traditional Chef cookbook testing
- No production workloads depend on this repository content requiring careful migration planning