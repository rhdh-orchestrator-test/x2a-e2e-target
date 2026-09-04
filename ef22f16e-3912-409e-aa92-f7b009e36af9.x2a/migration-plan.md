# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains demonstration examples of Chef InSpec integration with Ansible playbooks for compliance automation. The migration scope is minimal as the repository already contains Ansible playbooks with Chef InSpec used only for testing and verification. The primary migration task involves replacing Chef InSpec tests with native Ansible testing frameworks while preserving the compliance automation functionality.

**Migration Complexity**: Low  
**Estimated Timeline**: 1-2 weeks  
**Primary Challenge**: Replacing InSpec compliance tests with Ansible-native testing solutions

## Module Migration Plan

This repository contains Ansible playbooks with Chef InSpec testing integration that need migration planning:

### MODULE INVENTORY

**ansible-apache-https**:
- Description: Apache web server configuration with HTTPS/SSL setup, self-signed certificate generation, and virtual host management for a "Hello World" test site
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: SSL certificate generation via OpenSSL, Apache virtual host configuration, package management for Ubuntu 20.04

**ansible-ssl-hardening**:
- Description: SSL/TLS security hardening playbook that disables vulnerable SSL protocols (POODLE fix) and enforces TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL protocol configuration, service restart handlers, regex-based configuration replacement

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with Ansible provisioner and InSpec verifier
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality, port listening, and SSL protocol verification
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec security compliance test for SSH root login restrictions (STIG compliance)
- `chef-and-ansible/index.html`: Static HTML test file for web server verification
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (explicitly specified in kitchen.yml and playbook package versions)
- **Virtual Machine Technology**: Vagrant with VirtualBox (configured in Test Kitchen)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible Molecule + Testinfra or native Ansible assert modules
- **Test Kitchen**: Replace with Ansible Molecule for testing framework
- **Vagrant**: Can be retained or replaced with Docker for faster testing cycles
- **Chef Automate/Server**: Remove deployment scripts as they're not needed for pure Ansible workflow

### Security Considerations

- **SSL/TLS Configuration**: Current playbooks implement proper SSL hardening practices that should be preserved:
  - Disables SSL 3.0 protocol (POODLE vulnerability mitigation)
  - Enforces TLS 1.2 minimum protocol version
  - Self-signed certificate generation for testing environments
- **SSH Hardening**: InSpec test verifies SSH root login is disabled (STIG compliance SRG-OS-000112)
- **Vault/secrets management**: No encrypted secrets detected - uses hardcoded test values and self-signed certificates
  - 2 credential patterns identified: SSH configuration and SSL certificate management
  - All credentials are test/demo values, no production secrets detected

### Technical Challenges

- **InSpec Test Migration**: Converting Ruby-based InSpec tests to Ansible-native testing requires:
  - Replacing `describe port(443)` with Ansible `wait_for` or `uri` modules
  - Converting SSL protocol checks to Ansible `openssl_certificate_info` or custom shell commands
  - Migrating STIG compliance checks to Ansible `lineinfile` verification tasks
- **Test Kitchen Replacement**: Migrating from Test Kitchen to Ansible Molecule requires:
  - Converting kitchen.yml configuration to molecule.yml
  - Adapting Vagrant driver configuration for Molecule
  - Restructuring test scenarios and verification steps

### Migration Order

1. **ansible-ssl-hardening** (Priority 1: Low risk, standalone security configuration)
2. **ansible-apache-https** (Priority 2: Moderate complexity with SSL certificate dependencies)
3. **Test Framework Migration** (Priority 3: Replace InSpec tests with Ansible Molecule + native testing)

### Assumptions

- The repository is intended for demonstration and learning purposes, not production deployment
- Ubuntu 20.04 is the target OS, though playbooks could be adapted for other Debian-based distributions
- Self-signed certificates are acceptable for testing environments (production would require proper CA-signed certificates)
- The Chef Automate/Server deployment scripts are out of scope for Ansible migration as they serve a different purpose
- Test Kitchen and InSpec are used solely for validation and can be replaced with Ansible-native testing tools
- No integration with existing Chef infrastructure is required post-migration
- The compliance requirements (STIG controls) need to be maintained in the migrated testing framework
- Vagrant-based testing environment is preferred over Docker for maintaining VM-like testing conditions