# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains Chef-related examples and deployment scripts rather than traditional Chef cookbooks requiring migration. The primary content consists of Ansible playbooks demonstrating Chef InSpec integration, Chef server deployment scripts, and compliance testing examples. The migration scope is minimal as most content is already Ansible-based or consists of deployment utilities.

## Module Migration Plan

This repository contains mixed technologies with limited migration requirements:

### MODULE INVENTORY

**website-https-demo**:
- Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed SSL certificates, virtual host setup, and SSL protocol hardening
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, SSL certificate generation via OpenSSL, virtual host configuration, SSL/TLS security hardening

**poodle-ssl-fix**:
- Description: Ansible playbook for SSL protocol hardening to disable SSLv3 and enforce TLS 1.2 in Apache configurations
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: SSL protocol configuration replacement, Apache service management, POODLE vulnerability mitigation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script for lab environments
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL protocol verification
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec security control for SSH root login verification (STIG compliance)
- `chef-and-ansible/index.html`: Static HTML test file for web server validation

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

**No external dependencies requiring migration** - The Ansible playbooks use standard modules:
- **apt module**: Native Ansible package management (no migration needed)
- **openssl_* modules**: Native Ansible SSL certificate management (no migration needed)
- **file/copy modules**: Native Ansible file operations (no migration needed)

### Security Considerations

**SSL/TLS Certificate Management**: 
- Current implementation uses self-signed certificates generated via Ansible OpenSSL modules
- Production migration should consider certificate authority integration or Let's Encrypt automation
- Private key permissions are properly restricted (mode 0640)

**SSH Security Hardening**:
- InSpec tests verify SSH root login is disabled (STIG compliance)
- Migration should maintain or enhance SSH security configurations
- Consider implementing additional SSH hardening measures in Ansible

**Credential Management**:
- Deployment scripts contain hardcoded credentials (userpassword='password')
- Chef server deployment uses plaintext passwords in shell scripts
- Migration requires implementing Ansible Vault for credential management

### Technical Challenges

**Test Kitchen Integration**:
- Current setup uses Test Kitchen with Ansible provisioner and InSpec verifier
- Migration may require transitioning to molecule for Ansible role testing
- InSpec integration provides compliance validation that should be preserved

**Chef Infrastructure Dependencies**:
- Deployment scripts install Chef Automate and Infra Server
- These are infrastructure components, not configuration management code
- Consider whether Chef infrastructure is still needed post-migration

**Mixed Technology Environment**:
- Repository demonstrates Chef InSpec integration with Ansible
- Migration planning must account for continued InSpec usage for compliance testing
- Ansible and InSpec integration patterns should be maintained

### Migration Order

1. **Infrastructure Assessment** (immediate): Evaluate need for Chef server infrastructure post-migration
2. **Credential Security** (high priority): Implement Ansible Vault for deployment script credentials
3. **Testing Framework** (medium priority): Transition from Test Kitchen to Molecule if needed
4. **Documentation Update** (low priority): Update README files to reflect pure Ansible approach

### Assumptions

- The Ansible playbooks in chef-and-ansible/ are demonstration code rather than production configurations
- Chef InSpec will continue to be used for compliance testing alongside Ansible
- The Chef server deployment scripts may still be needed for hybrid environments
- Ubuntu 20.04 target platform will be maintained (though package versions may need updates)
- Self-signed certificates are acceptable for development/testing (production may require CA-signed certificates)
- The repository serves as educational/example content rather than production infrastructure code
- Test Kitchen configuration suggests this is primarily a development/testing repository
- Hardcoded credentials in deployment scripts are acceptable for lab environments but not production