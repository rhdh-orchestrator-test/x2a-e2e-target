# MIGRATION FROM CHEF TO ANSIBLE

This repository contains demonstration and example materials rather than production Chef cookbooks requiring migration. The primary content consists of Ansible playbooks with Chef InSpec compliance tests, deployment scripts for Chef infrastructure, and documentation. The migration scope is minimal as the repository already contains Ansible implementations and serves as educational/reference material.

## Module Migration Plan

This repository contains example and demonstration content that does not require traditional cookbook-to-playbook migration:

### MODULE INVENTORY

**No Chef cookbooks or recipes found for migration.** This repository contains:

- **website_https**: 
    - Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed certificates, SSL/TLS setup, and virtual host management
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: OpenSSL certificate generation, Apache virtual host configuration, SSL module activation

- **poodle_fix**:
    - Description: Ansible playbook for SSL security hardening by disabling SSLv3 and enforcing TLS 1.2 to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache SSL protocol configuration, security compliance remediation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `tests/ssh_profile.rb`: Chef InSpec security control for SSH root login verification (STIG compliance)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script for lab environments
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static HTML test content for web server validation

### Target Details

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml driver)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

**No external Chef dependencies identified** - this repository uses:
- **Chef InSpec**: Retain for compliance testing alongside Ansible playbooks
- **Test Kitchen**: Continue using for integration testing of Ansible content
- **Apache 2.4.41**: Already configured in existing Ansible playbooks

### Security Considerations

- **SSL/TLS Configuration**: Existing Ansible playbooks already implement proper SSL hardening
  - Self-signed certificate generation with OpenSSL
  - TLS 1.2 enforcement and SSLv3 disabling (POODLE mitigation)
  - Proper certificate file permissions (0640)
- **SSH Security**: InSpec controls verify SSH root login restrictions
- **Credential Management**: 
  - Hardcoded credentials present in deployment scripts (userpassword='password')
  - No encrypted data bags or vault usage detected
  - SSL certificates generated dynamically (no hardcoded certificate secrets)

### Technical Challenges

- **Minimal Migration Required**: Repository already contains Ansible implementations
- **InSpec Integration**: Maintain Chef InSpec for compliance verification alongside Ansible
- **Documentation Updates**: Update README files to reflect pure Ansible approach rather than Chef/Ansible hybrid examples

### Migration Order

1. **Documentation Review** (immediate, low risk)
   - Update README files and documentation
   - Clarify that examples are Ansible-native with InSpec testing

2. **Security Hardening** (immediate, high value)
   - Replace hardcoded passwords in deployment scripts with variables or vault integration
   - Review and validate SSL/TLS configurations

3. **Testing Framework** (low priority)
   - Maintain existing Test Kitchen + InSpec integration
   - Consider molecule for pure Ansible testing if desired

### Assumptions

- Repository serves as educational/demonstration material rather than production infrastructure
- Existing Ansible playbooks are considered the target state (no migration needed)
- Chef InSpec will be retained for compliance testing capabilities
- Test Kitchen integration with Ansible provisioner is acceptable for testing workflow
- Ubuntu 20.04 target platform is appropriate for demonstration purposes
- Self-signed certificates are acceptable for testing/lab environments
- Hardcoded credentials in deployment scripts are acceptable for lab/demo use cases
- No production workloads depend on this repository content
- Repository maintainers prefer to keep Chef InSpec for compliance validation rather than migrating to Ansible compliance modules