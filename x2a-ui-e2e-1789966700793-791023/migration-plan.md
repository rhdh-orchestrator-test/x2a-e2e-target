# MIGRATION FROM CHEF TO ANSIBLE

This repository contains Chef InSpec compliance testing examples and Ansible playbooks demonstrating integration patterns, rather than traditional Chef cookbooks requiring migration. The content is primarily educational/demo material showing how Chef InSpec can complement Ansible for continuous compliance monitoring. **No actual Chef cookbook migration is required** - the Ansible playbooks are already implemented and functional.

## Module Migration Plan

This repository contains demonstration content and infrastructure setup scripts rather than production Chef modules:

### MODULE INVENTORY

**No Chef cookbooks found for migration.** This repository contains:

- **website_https**: 
    - Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed certificates, SSL/TLS hardening, and virtual host setup
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: OpenSSL certificate generation, Apache virtual host configuration, SSL module activation

- **poodle_fix**:
    - Description: Ansible playbook for SSL/TLS security hardening by disabling vulnerable protocols and enforcing TLS 1.2
    - Path: chef-and-ansible/poodle_fix.yml  
    - Technology: Ansible (already migrated)
    - Key Features: Apache SSL protocol configuration, POODLE vulnerability mitigation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with Chef InSpec verification
- `tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality and SSL/TLS security
- `tests/ssh_profile.rb`: Chef InSpec compliance profile for SSH security hardening (STIG controls)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static HTML test content

### Target Details

Based on the Ansible playbooks and test configurations:

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

**No external Chef dependencies to migrate** - this is a demonstration repository. The existing Ansible playbooks have standard dependencies:

- **apache2 (2.4.41-4ubuntu3.10)**: Already specified in Ansible playbook with exact version pinning
- **openssl/python3-openssl**: Certificate management handled by Ansible openssl modules
- **curl**: Utility package for testing and verification

### Security Considerations

The repository demonstrates security best practices that are already implemented in Ansible:

- **SSL/TLS Configuration**: Self-signed certificate generation with proper file permissions (0640 for cert directory)
- **Protocol Hardening**: POODLE vulnerability mitigation by disabling SSLv3 and enforcing TLS 1.2
- **SSH Hardening**: InSpec compliance tests verify SSH root login is disabled (STIG control V-38607)
- **File Permissions**: Proper ownership and permissions for web content and configuration files
- **Service Management**: Proper handler configuration for service restarts after configuration changes

### Technical Challenges

**Minimal migration challenges** since Ansible playbooks are already functional:

- **Test Integration**: The repository uses Test Kitchen with Chef InSpec for compliance verification - teams may want to migrate to native Ansible testing frameworks (molecule, ansible-test)
- **Infrastructure Setup**: Chef Automate/Server deployment scripts are present but not needed if migrating away from Chef ecosystem entirely
- **Compliance Framework**: InSpec tests provide valuable security compliance checks that could be converted to Ansible-native compliance modules or maintained as-is

### Migration Order

**No migration required** - content is already in Ansible format. Recommended actions:

1. **Immediate Use**: Ansible playbooks can be used as-is for Apache HTTPS setup and SSL hardening
2. **Test Framework Migration**: Consider migrating from Test Kitchen + InSpec to Molecule + Ansible testing if desired
3. **Compliance Integration**: Evaluate whether to maintain InSpec compliance tests or migrate to Ansible-native compliance solutions

### Assumptions

- This repository serves as educational/demonstration content rather than production infrastructure code
- The Chef InSpec compliance tests provide value and may be retained even in an Ansible-focused environment
- Test Kitchen configuration suggests this is used for cookbook/playbook development and testing rather than production deployment
- The setup scripts for Chef Automate/Server indicate this may be part of a hybrid Chef/Ansible environment
- Ubuntu 20.04 target platform may need updating to more recent LTS versions for production use
- Self-signed certificates are acceptable for demonstration purposes but would need proper CA-signed certificates in production
- The hardcoded credentials and configuration in setup scripts are for demo purposes only