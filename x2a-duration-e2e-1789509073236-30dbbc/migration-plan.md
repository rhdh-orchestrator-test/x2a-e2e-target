# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains Chef-related examples and demonstration code rather than production Chef cookbooks requiring migration. The primary content consists of Ansible playbooks demonstrating Chef InSpec integration for compliance automation, along with Chef server deployment scripts. This represents a **minimal migration effort** focused on consolidating example code and deployment automation rather than converting infrastructure-as-code modules.

## Module Migration Plan

This repository contains demonstration and deployment scripts rather than traditional Chef cookbooks:

### MODULE INVENTORY

**No Chef cookbooks or recipes found for migration.** This repository contains:

- **website_https**: 
    - Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed certificates and SSL hardening
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache 2.4 installation, SSL certificate generation, virtual host configuration, security hardening

- **poodle_fix**:
    - Description: Ansible playbook for SSL protocol hardening to disable SSLv3 and enforce TLS 1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache SSL configuration remediation, POODLE vulnerability mitigation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS configuration validation
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec security profile for SSH root login compliance (STIG controls)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment automation script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `chef-and-ansible/index.html`: Static web content for demonstration purposes

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml), with deployment scripts targeting Linux systems
- **Virtual Machine Technology**: Vagrant (Test Kitchen driver), cloud VM compatible deployment scripts
- **Cloud Platform**: Cloud-agnostic deployment scripts with on-premises and cloud VM support

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Already integrated with Ansible via Test Kitchen verifier - no migration needed
- **Test Kitchen**: Currently configured for Ansible playbook testing - maintain existing workflow
- **Apache 2.4.41**: Specific version pinned in playbook - verify availability in target repositories
- **OpenSSL/PyOpenSSL**: Certificate management dependencies already handled by Ansible modules

### Security Considerations

- **SSL/TLS Configuration**: Existing playbooks implement security best practices:
  - Self-signed certificate generation for testing environments
  - SSL protocol hardening (TLS 1.2 enforcement, SSLv3 disabled)
  - Proper file permissions on certificate files (0640)
- **SSH Hardening**: InSpec profiles validate SSH root login restrictions per STIG requirements
- **Compliance Automation**: Chef InSpec integration provides continuous compliance validation
- **No hardcoded credentials found**: Deployment scripts use variables for user configuration

### Technical Challenges

- **InSpec Integration**: Maintain Chef InSpec testing capabilities within Ansible workflow - Test Kitchen already provides this integration
- **Compliance Validation**: Ensure InSpec profiles remain compatible with target Ansible-managed systems
- **Certificate Management**: Self-signed certificates suitable for testing only - production environments require proper CA integration

### Migration Order

1. **Documentation Review** (immediate): Update README files to reflect Ansible-first approach
2. **Deployment Script Enhancement** (low priority): Consider converting shell scripts to Ansible playbooks for consistency
3. **Test Framework Validation** (ongoing): Verify InSpec profiles work correctly with target systems

### Assumptions

- Repository serves as demonstration/example code rather than production infrastructure
- Existing Ansible playbooks are already properly structured and functional
- Chef InSpec will continue to be used for compliance validation alongside Ansible
- Test Kitchen workflow with Vagrant driver meets testing requirements
- Deployment scripts target development/lab environments rather than production systems
- SSL certificate generation is for testing purposes only
- Ubuntu package repositories contain required Apache version (2.4.41-4ubuntu3.10)
- Target environments have internet connectivity for package installation and Chef Automate deployment