# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains Chef-related examples and tools rather than traditional Chef cookbooks requiring migration. The primary content consists of Ansible playbooks demonstrating Chef InSpec integration, Chef server deployment scripts, and testing examples. The migration scope is minimal as most content is already Ansible-based or consists of deployment utilities.

## Module Migration Plan

This repository contains example code and deployment tools that need individual migration planning:

### MODULE INVENTORY

**chef-and-ansible**:
- Description: Ansible playbooks demonstrating Chef InSpec integration for compliance automation, including HTTPS website deployment with SSL configuration and POODLE vulnerability remediation
- Path: chef-and-ansible/
- Technology: Ansible (with Chef InSpec testing)
- Key Features: Apache2 HTTPS setup, self-signed SSL certificates, Test Kitchen integration, InSpec compliance tests

**setup-automate**:
- Description: Bash deployment scripts for Chef Automate and Chef Infra Server installation on VMs
- Path: setup-automate/
- Technology: Bash scripts
- Key Features: Automated Chef server deployment, user and organization creation, system configuration

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `website_https.yml`: Ansible playbook for Apache2 HTTPS site deployment with SSL certificate generation
- `poodle_fix.yml`: Ansible playbook for SSL protocol hardening (disabling SSLv3, enabling TLS 1.2)
- `deploy-automate.sh`: Chef Automate and Infra Server deployment script with user/org setup
- `deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `ssh_profile.rb`: InSpec security profile for SSH root login compliance testing

### Target Details

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml), with Chef server scripts supporting Linux distributions
- **Virtual Machine Technology**: Vagrant (Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - scripts support both on-premises and cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Already integrated with Ansible playbooks for compliance testing - no migration needed
- **Test Kitchen**: Currently configured for Ansible provisioner - maintain existing integration
- **Apache2 (2.4.41-4ubuntu3.10)**: Specific version pinned in playbook - update to current stable version
- **OpenSSL/PyOpenSSL**: Certificate generation dependencies - already Ansible-native modules

### Security Considerations

- **SSL/TLS Configuration**: Existing playbooks implement proper SSL hardening (TLS 1.2 only, SSLv3 disabled)
- **Certificate Management**: Self-signed certificates used for testing - consider integration with proper CA or Let's Encrypt for production
- **SSH Hardening**: InSpec profiles validate SSH root login restrictions - maintain compliance testing
- **Credential Management**: Chef server deployment scripts contain hardcoded credentials in variables - migrate to Ansible Vault or external secret management

### Technical Challenges

- **InSpec Integration**: The repository demonstrates Chef InSpec working alongside Ansible - this is already the target state and requires no migration
- **Test Kitchen Compatibility**: Existing Test Kitchen configuration uses Ansible provisioner - minimal changes needed
- **Chef Server Dependencies**: Deployment scripts are infrastructure utilities rather than configuration management - consider containerization or infrastructure-as-code alternatives

### Migration Order

1. **chef-and-ansible playbooks** (already Ansible - review and modernize only)
2. **InSpec test profiles** (maintain as-is for compliance validation)
3. **Chef server deployment scripts** (convert to Ansible playbooks or Terraform modules)

### Assumptions

- The repository serves as example/demo code rather than production infrastructure requiring migration
- Chef InSpec will continue to be used for compliance testing alongside Ansible
- Test Kitchen integration with Ansible provisioner will be maintained
- Chef server deployment is for development/testing environments based on hardcoded credentials
- SSL certificate generation is for testing purposes only (self-signed certificates)
- The target audience requires examples of Chef InSpec integration with Ansible rather than pure Ansible implementations
- Ubuntu 20.04 target OS may need updating to current LTS version (22.04 or 24.04)
- Vagrant-based testing environment will continue to be used for local development