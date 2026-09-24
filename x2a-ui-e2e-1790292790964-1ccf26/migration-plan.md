# MIGRATION FROM MIXED TECHNOLOGIES TO ANSIBLE

This repository is a collection of examples and deployment scripts rather than a traditional infrastructure-as-code repository requiring migration. The content is already primarily Ansible-based with supporting Chef InSpec tests and deployment automation scripts. No actual migration is required as the core infrastructure automation is already implemented in Ansible.

## Module Migration Plan

This repository contains example Ansible playbooks and supporting tools that demonstrate Chef InSpec integration with Ansible:

### MODULE INVENTORY

**No modules require migration** - this repository contains:

- **website_https**: 
    - Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed certificates, virtual host setup, and SSL/TLS security
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already target technology)
    - Key Features: Apache 2.4 installation, SSL certificate generation via OpenSSL, virtual host configuration, security hardening

- **poodle_fix**:
    - Description: Ansible playbook for SSL/TLS security hardening to address POODLE vulnerability by disabling SSLv3 and enforcing TLS 1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already target technology)
    - Key Features: Apache SSL protocol configuration, TLS 1.2 enforcement, service restart handling

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality and SSL/TLS security validation
- `tests/ssh_profile.rb`: Chef InSpec security profile for SSH root login compliance (STIG control)
- `setup-automate/deploy-automate.sh`: Chef Automate and Chef Infra Server deployment automation script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static HTML test content for web server validation

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

**No external dependencies requiring migration** - current dependencies are:
- **Apache 2.4.41**: Already managed via Ansible apt module
- **OpenSSL/PyOpenSSL**: Certificate management handled by Ansible openssl_* modules
- **Chef InSpec**: Compliance testing framework (complementary to Ansible, not requiring migration)

### Security Considerations

**Existing security implementations to maintain:**
- SSL/TLS certificate management: Self-signed certificate generation with proper file permissions (0640/0644)
- POODLE vulnerability mitigation: SSLv3 disabled, TLS 1.2 enforced in Apache configuration
- SSH security hardening: InSpec profile validates PermitRootLogin disabled (STIG compliance)
- File permissions: Proper ownership and permissions on web content and SSL certificates

### Technical Challenges

**No migration challenges** - considerations for maintaining current functionality:
- Test Kitchen integration: Existing Vagrant-based testing infrastructure with InSpec verification
- Compliance validation: Chef InSpec tests provide security and functionality validation
- Certificate management: Self-signed certificates suitable for testing but may need CA-signed certificates for production
- Service dependencies: Apache and SSH service restart coordination handled via Ansible handlers

### Migration Order

**No migration required** - recommended maintenance approach:
1. Continue using existing Ansible playbooks as reference implementations
2. Enhance InSpec test coverage for additional security controls
3. Consider production-ready certificate management (Let's Encrypt or enterprise CA)

### Assumptions

- This repository serves as an example/demo collection rather than production infrastructure code
- The Chef InSpec tests are intended to demonstrate compliance automation alongside Ansible
- The deployment scripts are for setting up Chef infrastructure for testing/demo purposes
- No actual Chef cookbooks exist in this repository that would require migration to Ansible
- The existing Ansible playbooks are examples and may need adaptation for production environments
- SSL certificates are self-signed for testing purposes and would need proper CA certificates for production use