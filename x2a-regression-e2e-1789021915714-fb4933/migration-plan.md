# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains demonstration examples showing Chef InSpec integration with Ansible rather than production Chef infrastructure requiring migration. The Ansible playbooks are already implemented and functional, with Chef InSpec providing compliance testing capabilities. **No actual migration is required** - this is a reference implementation showing how Chef InSpec can complement Ansible automation.

## Module Migration Plan

This repository contains example Ansible playbooks and Chef InSpec tests that demonstrate compliance automation patterns:

### MODULE INVENTORY

**No Chef cookbooks or infrastructure modules found for migration.** This repository contains:

- **website_https**: 
    - Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed certificates, SSL/TLS setup, and virtual host management
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: OpenSSL certificate generation, Apache virtual host configuration, SSL module activation

- **poodle_fix**:
    - Description: Ansible playbook demonstrating SSL protocol hardening by disabling SSLv3 and enforcing TLS 1.2
    - Path: chef-and-ansible/poodle_fix.yml  
    - Technology: Ansible (already migrated)
    - Key Features: Apache SSL configuration remediation, POODLE vulnerability mitigation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `tests/ssh_profile.rb`: Chef InSpec security control for SSH root login restrictions (STIG compliance)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static HTML test content for web server validation

### Target Details

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured as Test Kitchen driver)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

**No migration dependencies** - this is a reference implementation. The existing setup demonstrates:
- **Chef InSpec**: Continue using for compliance testing alongside Ansible
- **Test Kitchen**: Retain for integration testing of Ansible playbooks
- **OpenSSL Ansible modules**: Already implemented (python3-openssl package dependency)

### Security Considerations

The examples demonstrate several security best practices that should be maintained:
- **SSL/TLS Configuration**: Self-signed certificate generation for development, TLS 1.2 enforcement
- **SSH Hardening**: InSpec controls for SSH root login restrictions (STIG compliance)
- **Apache Security**: Virtual host isolation, directory access controls
- **Certificate Management**: Proper file permissions (0640) for certificate directories and configuration files

### Technical Challenges

**No migration challenges** - the repository already contains working Ansible implementations. Considerations for teams adopting this pattern:
- **InSpec Integration**: Teams need Chef InSpec knowledge for compliance testing
- **Test Kitchen Setup**: Requires Vagrant and VirtualBox/VMware for local testing
- **Compliance Mapping**: Understanding STIG controls and security framework requirements

### Migration Order

**No migration required.** For teams implementing this pattern:
1. Deploy Ansible playbooks (already functional)
2. Implement InSpec compliance tests
3. Integrate Test Kitchen for continuous testing
4. Establish compliance reporting workflows

### Assumptions

- This repository serves as a reference implementation rather than production infrastructure requiring migration
- Teams will use this as a template for integrating Chef InSpec compliance testing with Ansible automation
- The Chef Automate deployment scripts are for setting up testing infrastructure, not production workloads requiring migration
- SSL certificates shown are self-signed for development purposes; production implementations will require proper certificate management
- The Ubuntu 20.04 target platform may need updates for current production environments
- InSpec tests demonstrate compliance patterns but may need customization for specific organizational security requirements