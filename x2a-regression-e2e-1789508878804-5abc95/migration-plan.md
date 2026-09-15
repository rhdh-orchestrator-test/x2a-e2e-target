# MIGRATION FROM MIXED ANSIBLE/CHEF INSPEC TO ANSIBLE

This repository contains example Ansible playbooks with Chef InSpec compliance testing and Chef infrastructure deployment scripts. **No actual migration is required** as the primary configuration management is already implemented in Ansible. The repository serves as a demonstration of using Chef InSpec for compliance validation alongside Ansible automation.

## Module Migration Plan

This repository contains demonstration content rather than production infrastructure code requiring migration:

### MODULE INVENTORY

**No Chef cookbooks or modules found for migration.** The repository contains:

- **website_https**: 
    - Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed certificates, virtual host setup, and SSL/TLS security
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already target technology)
    - Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL module activation

- **poodle_fix**:
    - Description: Ansible playbook for SSL security hardening by disabling vulnerable protocols and enforcing TLS 1.2
    - Path: chef-and-ansible/poodle_fix.yml  
    - Technology: Ansible (already target technology)
    - Key Features: SSL protocol configuration, POODLE vulnerability mitigation, Apache SSL module reconfiguration

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with Chef InSpec verification
- `tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `tests/ssh_profile.rb`: Chef InSpec security compliance test for SSH root login restrictions (STIG control)
- `setup-automate/deploy-automate.sh`: Bash script for Chef Automate and Chef Infra Server deployment
- `setup-automate/deploy-chef-server.sh`: Bash script for standalone Chef Infra Server deployment
- `index.html`: Static HTML test content for web server validation

### Target Details

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured as Test Kitchen driver)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

**No migration dependencies** - the Ansible playbooks are already functional. However, for production use:

- **Chef InSpec (latest)**: Replace with Ansible compliance modules or maintain InSpec for compliance validation
- **Test Kitchen**: Replace with molecule for Ansible testing or maintain current setup
- **Apache 2.4.41**: Update to current stable version for production deployment

### Security Considerations

- **Self-signed certificates**: The playbooks generate self-signed SSL certificates suitable for testing but require proper CA-signed certificates for production
- **Hardcoded credentials**: SSH and service configurations use default settings - implement proper credential management for production
- **SSL/TLS configuration**: POODLE fix playbook demonstrates security hardening but may need additional cipher suite configuration
- **Compliance validation**: Chef InSpec tests validate STIG controls and SSL security - consider maintaining InSpec or migrating to Ansible compliance modules

### Technical Challenges

- **Testing framework transition**: If moving away from Test Kitchen, implement equivalent testing with Molecule or Ansible Test
- **Compliance tool selection**: Decide whether to maintain Chef InSpec for compliance or migrate to native Ansible compliance modules
- **Certificate management**: Implement proper certificate lifecycle management for production environments

### Migration Order

**No migration required** - this is already an Ansible-based repository. For enhancement:

1. **Immediate**: Update Apache version and SSL configuration for current security standards
2. **Short-term**: Implement proper certificate management and credential handling
3. **Long-term**: Evaluate compliance tooling strategy (InSpec vs Ansible native)

### Assumptions

- The repository serves as demonstration/example content rather than production infrastructure
- Current Ansible playbooks are functional and do not require Chef cookbook migration
- Chef InSpec testing framework may be intentionally maintained for compliance validation
- Test Kitchen configuration suggests development/testing environment rather than production deployment
- SSL certificate generation is appropriate for testing but not production use
- Ubuntu 20.04 target platform may need updating for current production standards
- Bash deployment scripts are for Chef infrastructure setup, not configuration management migration