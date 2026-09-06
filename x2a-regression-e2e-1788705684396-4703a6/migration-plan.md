# MIGRATION FROM MIXED ANSIBLE/CHEF EXAMPLES TO STANDARDIZED ANSIBLE

This repository contains Ansible playbooks with Chef InSpec testing examples that demonstrate compliance automation patterns. The migration involves standardizing the existing Ansible content and extracting reusable patterns for enterprise deployment.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need standardization and modularization:

### MODULE INVENTORY

**website-https**:
- Description: Apache web server with HTTPS configuration using self-signed certificates, virtual host setup, and SSL/TLS security hardening
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL module activation, security compliance

**poodle-fix**:
- Description: SSL/TLS security hardening playbook that disables vulnerable SSL protocols and enforces TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible
- Key Features: Apache SSL configuration hardening, POODLE vulnerability mitigation, protocol enforcement

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with InSpec verification
- `index.html`: Static HTML test content for web server validation
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `tests/ssh_profile.rb`: InSpec security compliance test for SSH root login restrictions (STIG compliance)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address
- **apache2 (2.4.41-4ubuntu3.10)**: Specific version pinning needs review for current security patches
- **python3-openssl**: Required for Ansible OpenSSL certificate modules
- **openssl**: System dependency for certificate generation
- **curl**: Used for package downloads and testing

### Security Considerations
- **Certificate Management**: Self-signed certificates are used for testing - production deployment needs proper CA integration
  - Current implementation generates certificates on-demand using Ansible openssl modules
  - Private keys stored in /etc/apache2/certs/ with 0640 permissions
  - No certificate rotation or expiration handling
- **SSL/TLS Configuration**: POODLE vulnerability mitigation implemented but needs comprehensive SSL hardening
- **SSH Security**: InSpec tests verify SSH root login restrictions (STIG compliance)
- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (userpassword='password')
  - No encrypted variable usage detected
  - Certificate private keys generated but not secured with Ansible Vault
  - 2 credential instances detected in setup scripts requiring vault integration

### Technical Challenges
- **Version Pinning**: Apache package version is hardcoded and may be outdated for security patches
- **Certificate Lifecycle**: No automated certificate renewal or validation processes
- **Test Integration**: InSpec tests are separate from Ansible execution - needs integration strategy
- **Idempotency Issues**: Some tasks use command module without proper change detection
- **Handler Dependencies**: Handler naming inconsistencies (apache vs apache2) may cause execution failures

### Migration Order
1. **Security Hardening Module** (poodle-fix) - Low complexity, high security value, no dependencies
2. **Web Server Base Module** (website-https) - Moderate complexity, depends on security hardening
3. **Testing Framework Integration** - High complexity, requires InSpec and Test Kitchen coordination

### Assumptions
- The repository serves as examples rather than production-ready code requiring full enterprise migration
- Ubuntu 20.04 is the target platform, though playbooks may work on other Debian-based systems
- Self-signed certificates are acceptable for testing environments
- Chef InSpec will continue to be used for compliance testing alongside Ansible
- The setup scripts are for development/testing Chef infrastructure, not production deployment
- Network connectivity allows package downloads from official repositories
- Root or sudo access is available on target systems
- The examples are meant to demonstrate Chef InSpec integration with Ansible rather than comprehensive infrastructure automation
- Test Kitchen and Vagrant are available in the development environment
- The hardcoded credentials in setup scripts are placeholder values for demonstration purposes