# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains example code demonstrating Chef InSpec integration with Ansible for compliance automation. **No actual migration is required** as the infrastructure automation is already implemented in Ansible. The repository serves as a reference implementation showing how to use Chef InSpec as a testing framework alongside Ansible playbooks.

## Module Migration Plan

This repository contains demonstration code and deployment scripts rather than production infrastructure modules:

### MODULE INVENTORY

**No infrastructure modules require migration** - the repository contains:

- **website_https**: 
    - Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed certificates, SSL/TLS security hardening, and virtual host setup
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache 2.4 installation, SSL certificate generation via OpenSSL, virtual host configuration, security hardening

- **poodle_fix**:
    - Description: Ansible playbook demonstrating SSL protocol hardening to disable SSLv3 and enforce TLS 1.2 (POODLE vulnerability mitigation)
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache SSL configuration updates, protocol restriction, service restart handling

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `tests/ssh_profile.rb`: Chef InSpec security compliance profile for SSH root login restrictions (STIG compliance)
- `setup-automate/deploy-automate.sh`: Chef Automate and Chef Infra Server deployment script for lab environments
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static HTML test content for web server validation

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured as Test Kitchen driver)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address

**No migration dependencies** - this is a reference implementation. For organizations adopting this pattern:

- **Chef InSpec**: Continue using as compliance testing framework alongside Ansible
- **Test Kitchen**: Retain for integration testing of Ansible playbooks
- **Apache 2.4**: Already managed via Ansible apt module with version pinning

### Security Considerations

The repository demonstrates security best practices that should be maintained:

- **SSL/TLS Configuration**: Self-signed certificate generation for development; production environments should integrate with proper CA or certificate management solutions
- **Protocol Hardening**: POODLE vulnerability mitigation by disabling SSLv3 and enforcing TLS 1.2
- **SSH Security**: InSpec profile validates SSH root login restrictions per STIG requirements
- **Credential Management**: Deployment scripts contain hardcoded credentials for lab environments - production implementations must use Ansible Vault or external secret management

### Technical Challenges

**No migration challenges** - this repository demonstrates the target state. Organizations implementing this pattern may face:

- **InSpec Integration**: Teams unfamiliar with Chef InSpec will need training on compliance-as-code practices
- **Test Kitchen Learning Curve**: Development teams may need guidance on Test Kitchen workflow for Ansible playbook testing
- **Certificate Management**: Production environments require integration with proper certificate authorities rather than self-signed certificates

### Migration Order

**No migration required** - this repository serves as a reference implementation for:

1. Organizations wanting to adopt Ansible + InSpec compliance automation
2. Teams learning to integrate compliance testing with infrastructure automation
3. Development of security-focused Ansible playbooks with automated validation

### Assumptions

- This repository is intended as educational/reference material rather than production infrastructure requiring migration
- The Chef components (InSpec, Test Kitchen) are intentionally retained as testing and compliance frameworks
- Organizations using this pattern will adapt the examples to their specific infrastructure requirements
- Production implementations will replace hardcoded credentials and self-signed certificates with proper secret management and certificate authorities
- The Ubuntu 20.04 target platform may need updates for current production environments (Ubuntu 22.04 LTS or RHEL 9)