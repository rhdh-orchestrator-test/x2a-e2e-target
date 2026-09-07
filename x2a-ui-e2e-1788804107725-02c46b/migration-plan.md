# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains example configurations demonstrating Chef InSpec integration with Ansible playbooks, rather than traditional Chef cookbooks requiring migration. The primary migration task involves consolidating the testing framework from Chef InSpec to Ansible's native testing capabilities while preserving the existing Ansible automation logic.

**Migration Scope**: 2 Ansible playbooks with Chef InSpec test integration, 2 Chef server deployment scripts
**Estimated Timeline**: 1-2 weeks (low complexity due to minimal Chef-specific content)
**Complexity Level**: Low - primarily involves test framework migration rather than infrastructure code conversion

## Module Migration Plan

This repository contains demonstration examples that integrate Chef InSpec testing with Ansible automation:

### MODULE INVENTORY

**website-https-automation**:
- Description: Apache web server configuration with SSL/TLS setup, self-signed certificate generation, and virtual host deployment for a "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (with Chef InSpec testing)
- Key Features: Apache 2.4.41 installation, OpenSSL certificate management, virtual host configuration, SSL module activation

**ssl-security-hardening**:
- Description: Apache SSL protocol hardening to disable vulnerable SSL 3.0 and enforce TLS 1.2 (POODLE vulnerability mitigation)
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (with Chef InSpec testing)
- Key Features: SSL protocol configuration replacement, Apache service management

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with InSpec verification
- `tests/website_https_verify.rb`: Chef InSpec tests for HTTPS functionality, SSL protocol validation, and web service verification
- `tests/ssh_profile.rb`: Chef InSpec compliance test for SSH root login security (STIG control SRG-OS-000112)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script for lab environments
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static HTML test content for web server validation

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's native testing modules (uri, assert, service, etc.) or molecule with testinfra
- **Test Kitchen**: Migrate to Ansible molecule for testing framework
- **Chef Automate/Server**: Remove dependency on Chef infrastructure components

### Security Considerations

- **SSL/TLS Configuration**: Existing playbooks properly implement SSL hardening (TLS 1.2 enforcement, SSL 3.0 disabling)
- **Certificate Management**: Self-signed certificate generation is properly implemented with OpenSSL modules
- **SSH Security**: InSpec test validates SSH root login restrictions (STIG compliance)
- **Vault/Secrets Management**: No encrypted data bags or Chef Vault usage detected; credentials are hardcoded in deployment scripts (userpassword='password') - requires migration to Ansible Vault

### Technical Challenges

- **Test Framework Migration**: Converting Chef InSpec tests to Ansible native testing requires rewriting Ruby-based tests to YAML-based assertions
- **Compliance Testing**: SSH security test (STIG control) needs conversion from InSpec control format to Ansible compliance modules
- **Integration Testing**: Kitchen.yml workflow needs replacement with molecule or similar Ansible testing framework

### Migration Order

1. **website-https-automation** (Priority 1: standalone, well-defined scope)
2. **ssl-security-hardening** (Priority 2: depends on Apache configuration from module 1)
3. **Test framework consolidation** (Priority 3: convert InSpec tests to Ansible native testing)

### Assumptions

- The repository serves as demonstration/example code rather than production infrastructure requiring migration
- Target environment will use Ansible's native testing capabilities instead of Chef InSpec integration
- Chef Automate/Server deployment scripts are for lab setup only and may not require migration if Chef infrastructure is being retired
- Ubuntu 20.04 target OS assumption based on Test Kitchen configuration may need validation for production environments
- Self-signed certificates are acceptable for the target environment (production may require CA-signed certificates)
- Current hardcoded credentials in deployment scripts indicate this is lab/demo environment - production migration will require proper secrets management implementation