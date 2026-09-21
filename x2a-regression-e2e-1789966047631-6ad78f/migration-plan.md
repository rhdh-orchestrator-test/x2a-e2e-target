# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains Chef-related examples and deployment scripts rather than production Chef cookbooks requiring migration. The primary content consists of Ansible playbooks demonstrating Chef InSpec integration, Chef server deployment scripts, and test verification files. The migration scope is minimal as most content is already in Ansible format or consists of deployment utilities.

**Timeline Estimate**: 1-2 weeks (primarily documentation and script consolidation)
**Complexity**: Low - Most content is already Ansible-compatible or consists of standalone scripts

## Module Migration Plan

This repository contains example configurations and deployment scripts that demonstrate Chef InSpec integration with Ansible:

### MODULE INVENTORY

**apache-https-website**:
- Description: Apache web server configuration with HTTPS/SSL setup, self-signed certificate generation, and virtual host management
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: SSL certificate generation via OpenSSL, Apache virtual host configuration, security hardening with TLS 1.2

**ssl-security-hardening**:
- Description: SSL/TLS security configuration to disable vulnerable protocols (POODLE fix)
- Path: chef-and-ansible/poodle_fix.yml  
- Technology: Ansible (already migrated)
- Key Features: Apache SSL protocol restriction, TLS 1.2 enforcement, service restart handling

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `tests/ssh_profile.rb`: InSpec security profile for SSH root login compliance (STIG controls)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static test web content

### Target Details

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml), with Apache 2.4.41 package version targeting Ubuntu-specific repositories
- **Virtual Machine Technology**: Vagrant (configured in Test Kitchen for local development and testing)
- **Cloud Platform**: Not specified - deployment scripts support both on-premises and cloud VM deployment

## Migration Approach

### Key Dependencies to Address
- **apache2=2.4.41-4ubuntu3.10**: Already using Ansible apt module with specific version pinning
- **openssl/python3-openssl**: Certificate management dependencies already handled via Ansible openssl modules
- **chef-automate-cli**: Deployment utility for Chef infrastructure - no Ansible equivalent needed as this is for Chef server deployment

### Security Considerations
- **SSL/TLS Configuration**: Existing playbooks already implement security best practices:
  - Self-signed certificate generation with proper key management
  - TLS 1.2 enforcement and SSL 3.0 disabling (POODLE vulnerability mitigation)
  - Proper file permissions on certificate files (0640 for directories, 0644 for web content)
- **InSpec Integration**: Compliance testing framework integration maintained through existing Test Kitchen configuration
- **SSH Hardening**: InSpec profiles verify SSH root login restrictions per STIG requirements
- **Credential Management**: Deployment scripts contain hardcoded credentials that should be externalized to Ansible Vault

### Technical Challenges
- **Test Framework Integration**: Maintaining InSpec compliance testing workflow within pure Ansible environment
  - Mitigation: Continue using Test Kitchen with Ansible provisioner and InSpec verifier as demonstrated
- **Chef Server Dependencies**: Deployment scripts are specific to Chef infrastructure setup
  - Mitigation: These scripts serve their intended purpose and don't require migration - they deploy the Chef infrastructure that other cookbooks would connect to
- **Version Pinning**: Apache package version is Ubuntu 20.04 specific
  - Mitigation: Update package versions for target OS or use version ranges for broader compatibility

### Migration Order
1. **Documentation Consolidation** (immediate) - Update README files to clarify repository purpose and usage
2. **Security Hardening** (week 1) - Externalize hardcoded credentials in deployment scripts to environment variables or Ansible Vault
3. **Playbook Enhancement** (week 2) - Add error handling and idempotency improvements to existing Ansible playbooks

### Assumptions
- Repository serves as example/demonstration code rather than production infrastructure requiring migration
- Existing Ansible playbooks are intended to remain as-is for educational/example purposes
- Chef server deployment scripts will continue to be used for Chef infrastructure provisioning
- InSpec compliance testing integration is a key requirement to maintain
- Target environment will continue to use Ubuntu-based systems for consistency with existing examples
- Test Kitchen workflow with Vagrant is acceptable for development and testing scenarios
- Self-signed certificates are appropriate for demonstration purposes (production would require CA-signed certificates)