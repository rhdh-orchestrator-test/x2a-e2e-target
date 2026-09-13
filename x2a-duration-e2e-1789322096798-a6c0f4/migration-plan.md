# MIGRATION FROM CHEF TO ANSIBLE

This repository contains example code demonstrating Chef InSpec integration with Ansible rather than traditional Chef cookbooks requiring migration. The content is already primarily Ansible-based with InSpec compliance testing, representing a best-practice approach for infrastructure automation with continuous compliance validation.

**Migration Status**: No migration required - this is a demonstration repository showing Ansible playbooks with Chef InSpec testing integration.

## Module Migration Plan

This repository contains demonstration examples rather than production Chef cookbooks:

### MODULE INVENTORY

**No Chef modules found for migration**. This repository contains:

- **website_https**: 
    - Description: Ansible playbook demonstrating Apache HTTPS configuration with SSL certificate generation and virtual host setup
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: Self-signed SSL certificates, Apache virtual host configuration, package management

- **poodle_fix**:
    - Description: Ansible playbook for SSL security hardening by disabling SSLv3 and enforcing TLS 1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already migrated)
    - Key Features: SSL protocol configuration, Apache security hardening

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL configuration
- `tests/ssh_profile.rb`: InSpec compliance profile for SSH security configuration (STIG compliance)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static HTML test file for web server validation

### Target Details

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml driver)
- **Cloud Platform**: Not specified - designed for local development and testing

## Migration Approach

### Key Dependencies to Address

**No external Chef dependencies found**. The repository uses:
- **Apache 2.4.41**: Already configured via Ansible apt module
- **OpenSSL**: Certificate generation handled by Ansible openssl modules
- **Python3-OpenSSL**: Required for Ansible SSL certificate modules

### Security Considerations

- **SSL/TLS Configuration**: Playbooks demonstrate proper SSL hardening practices:
  - Self-signed certificate generation for development/testing
  - SSLv3 protocol disabling (POODLE vulnerability mitigation)
  - TLS 1.2 enforcement
- **SSH Hardening**: InSpec profile validates SSH root login restrictions (STIG compliance)
- **Certificate Management**: Uses Ansible's built-in OpenSSL modules for certificate lifecycle
- **No hardcoded credentials detected**: Configuration uses variables and generated certificates

### Technical Challenges

**No migration challenges** - this repository demonstrates the target state:
- Ansible playbooks are already properly structured
- InSpec integration provides compliance validation
- Test Kitchen provides automated testing framework
- SSL security best practices are implemented

### Migration Order

**No migration required** - repository contents are:
1. Ansible playbooks (target technology)
2. InSpec compliance tests (recommended for continuous compliance)
3. Infrastructure deployment scripts (Chef Automate/Server setup for testing)

### Assumptions

- This repository serves as a reference implementation rather than production infrastructure requiring migration
- The Chef Automate deployment scripts are for setting up test environments to validate the Ansible + InSpec integration
- InSpec testing framework will be retained in the target Ansible environment for compliance automation
- Test Kitchen configuration suggests this is used for cookbook/playbook development and validation
- The examples target Ubuntu/Debian systems but patterns are applicable to RHEL/CentOS environments
- SSL certificate generation is for development/testing purposes - production environments would use proper CA-signed certificates or Let's Encrypt integration