# MIGRATION FROM CHEF INSPEC + ANSIBLE TO PURE ANSIBLE

This repository contains demonstration examples showing Chef InSpec integration with Ansible for compliance automation. The migration scope is limited as the repository already uses Ansible playbooks for infrastructure provisioning, with Chef InSpec providing compliance testing. The migration involves consolidating compliance testing into native Ansible solutions while preserving the existing automation workflows.

**Timeline Estimate**: 1-2 weeks
**Complexity**: Low to Medium
**Risk Level**: Low (demonstration code, no production dependencies)

## Module Migration Plan

This repository contains Ansible playbooks with Chef InSpec compliance tests that need consolidation into pure Ansible solutions:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All paths have been verified using directory listing and file reading tools.

- **website-https-provisioning**:
    - Description: Apache web server provisioning with SSL/TLS configuration, self-signed certificate generation, and virtual host setup
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL module activation

- **poodle-ssl-fix**:
    - Description: SSL protocol hardening to disable SSLv3 and enforce TLS 1.2 to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache SSL configuration replacement, TLS protocol enforcement, service restart handling

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with Ansible provisioner and InSpec verifier
- `chef-and-ansible/index.html`: Static HTML test content for web server validation
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec compliance profile for SSH root login security controls (STIG compliance)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox provider (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible native testing modules (uri, assert, service_facts)
- **Test Kitchen**: Replace with molecule for Ansible testing framework
- **Chef Automate/Server**: Remove dependency as compliance testing moves to Ansible native solutions

### Security Considerations

- **SSL/TLS Certificate Management**: Current implementation uses self-signed certificates generated via OpenSSL Ansible modules - this approach is already Ansible-native and secure
- **SSH Security Controls**: InSpec profile tests SSH root login restrictions - migrate to Ansible assert module with lineinfile verification
- **STIG Compliance**: SSH profile implements RHEL-08-000227 control - ensure Ansible equivalent maintains same compliance posture
- **Vault/secrets management**: No encrypted credentials detected in current implementation - all configurations use variables and generated certificates

### Technical Challenges

- **InSpec to Ansible Testing Migration**: Convert Ruby-based InSpec controls to Ansible assert tasks and uri module checks
  - Challenge: InSpec's `ssl()` resource for protocol testing needs equivalent Ansible solution using openssl command module
  - Mitigation: Use Ansible command module with openssl s_client to verify SSL protocols
- **Test Kitchen to Molecule**: Migrate testing framework while preserving Vagrant integration
  - Challenge: Kitchen.yml configuration needs conversion to molecule.yml format
  - Mitigation: Use molecule-vagrant driver to maintain existing VM workflow
- **Compliance Reporting**: InSpec provides structured compliance reports - need equivalent in Ansible
  - Challenge: Loss of detailed compliance reporting and STIG mapping
  - Mitigation: Implement custom Ansible callback plugins for compliance reporting

### Migration Order

1. **website-https-provisioning** (already complete - no migration needed)
2. **poodle-ssl-fix** (already complete - no migration needed)  
3. **InSpec compliance tests** (convert to Ansible assert tasks and uri module tests)
4. **Test Kitchen configuration** (migrate to Molecule with Vagrant driver)
5. **Chef server deployment scripts** (optional - remove if not needed for pure Ansible workflow)

### Assumptions

- The repository serves as demonstration/training material rather than production infrastructure
- Test Kitchen and InSpec are used solely for validation and can be replaced with Ansible-native testing
- The existing Ansible playbooks are already properly structured and don't require refactoring
- Ubuntu 20.04 target platform will remain consistent post-migration
- Self-signed certificate approach is acceptable for demonstration purposes
- No integration with external Chef Automate/Server infrastructure is required post-migration
- STIG compliance requirements (specifically RHEL-08-000227) must be maintained in pure Ansible implementation
- Local development/testing workflow using Vagrant should be preserved
- No production secrets or sensitive data are present in the demonstration code