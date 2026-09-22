# MIGRATION FROM CHEF INSPEC INTEGRATION TO ANSIBLE

This repository contains example code demonstrating Chef InSpec integration with Ansible playbooks rather than traditional Chef cookbooks requiring migration. The content is already primarily Ansible-based with InSpec used for compliance testing. Migration complexity is minimal as the core infrastructure automation is already implemented in Ansible.

## Module Migration Plan

This repository contains demonstration examples that showcase Chef InSpec integration with Ansible:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
This repository does not contain traditional Chef cookbooks, Puppet modules, or PowerShell DSC configurations that require migration. Instead, it contains:

- **website-https-demo**:
    - Description: Apache HTTPS website deployment with SSL certificate generation, virtual host configuration, and security hardening
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: Self-signed SSL certificates via OpenSSL, Apache virtual host configuration, package management for Ubuntu 20.04

- **poodle-vulnerability-fix**:
    - Description: SSL/TLS security hardening to disable SSLv3 and enforce TLS 1.2 to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache SSL protocol configuration, service restart handlers

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL/TLS security
- `tests/ssh_profile.rb`: InSpec compliance profile for SSH security configuration (STIG compliance)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static HTML test content

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (explicitly specified in kitchen.yml and playbook package versions)
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml driver)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

This repository demonstrates integration patterns rather than requiring migration:

- **Chef InSpec**: Already integrated for compliance testing - no migration needed
- **Test Kitchen**: Currently configured for Ansible provisioner - no migration needed
- **Apache 2.4.41**: Specific version pinned in playbook - version compatibility should be verified for target environment

### Security Considerations

The existing Ansible playbooks already implement security best practices:

- **SSL/TLS Configuration**: Self-signed certificate generation with proper file permissions (0640 for certs directory)
- **POODLE Vulnerability Mitigation**: Explicit disabling of SSLv3 and enforcement of TLS 1.2
- **SSH Hardening**: InSpec profile includes STIG-compliant SSH root login restrictions
- **File Permissions**: Proper ownership and permissions for web content and configuration files
- **Service Management**: Secure service restart patterns using handlers

### Technical Challenges

Minimal challenges as content is already Ansible-based:

- **InSpec Integration**: The repository demonstrates how to maintain Chef InSpec for compliance testing alongside Ansible automation - this pattern can be preserved
- **Test Kitchen Configuration**: Current setup uses Vagrant driver with Ansible provisioner - may need adjustment for different testing environments
- **Package Versions**: Hardcoded Apache version (2.4.41-4ubuntu3.10) may need updating for newer Ubuntu releases

### Migration Order

No traditional migration required - this is a reference implementation:

1. **Validation Phase**: Test existing playbooks in target environment
2. **Package Updates**: Update pinned package versions if deploying to newer OS versions  
3. **Environment Adaptation**: Modify kitchen.yml and deployment scripts for target infrastructure

### Assumptions

- The repository serves as a demonstration/example rather than production infrastructure requiring migration
- Chef InSpec will continue to be used for compliance testing alongside Ansible automation
- Target deployment environment supports the same package versions and service configurations
- Test Kitchen integration patterns will be preserved for continuous testing
- The Chef Automate/Infra Server deployment scripts are for lab/demo environments and may need production hardening
- SSL certificate generation approach (self-signed) is acceptable for the target environment or will be replaced with proper CA-signed certificates
- Ubuntu 20.04 is the intended target OS, though playbooks may need adaptation for RHEL/CentOS environments