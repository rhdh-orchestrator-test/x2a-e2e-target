# MIGRATION FROM CHEF TO ANSIBLE

This repository contains demonstration examples and deployment scripts rather than production Chef cookbooks requiring migration. The content shows Ansible playbooks alongside Chef InSpec tests, demonstrating compliance automation patterns. The migration scope is minimal as the actual infrastructure automation is already implemented in Ansible.

## Module Migration Plan

This repository contains example configurations and deployment scripts that demonstrate Chef InSpec integration with Ansible:

### MODULE INVENTORY

**No Chef cookbooks or recipes found for migration.** This repository contains:

- **website_https**: 
    - Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed certificates, SSL/TLS security hardening, and virtual host setup
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: OpenSSL certificate generation, Apache virtual host configuration, SSL module activation

- **poodle_fix**:
    - Description: Ansible playbook for SSL/TLS security hardening, specifically disabling vulnerable SSL protocols and enforcing TLS 1.2
    - Path: chef-and-ansible/poodle_fix.yml  
    - Technology: Ansible (already migrated)
    - Key Features: Apache SSL protocol configuration, POODLE vulnerability mitigation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with Chef InSpec verification
- `tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality and SSL/TLS security
- `tests/ssh_profile.rb`: Chef InSpec security profile for SSH root login compliance (STIG controls)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static web content for testing purposes

### Target Details

Based on the Ansible playbooks and test configurations:

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

**No external Chef dependencies found.** The existing Ansible playbooks use standard modules:
- **apache2 (2.4.41-4ubuntu3.10)**: Already configured via apt module in Ansible
- **openssl/python3-openssl**: Certificate management handled by ansible.builtin.openssl_* modules
- **curl**: Standard utility, no migration needed

### Security Considerations

The repository demonstrates security-focused automation patterns:
- **SSL/TLS Configuration**: Self-signed certificate generation and Apache SSL hardening are already implemented in Ansible
- **POODLE Vulnerability Mitigation**: TLS 1.2 enforcement is handled via Ansible replace module
- **SSH Security**: Chef InSpec profiles verify SSH root login restrictions (STIG compliance)
- **Certificate Management**: OpenSSL private keys and certificates are generated using Ansible crypto modules
- **No hardcoded credentials detected** in the reviewed playbooks

### Technical Challenges

**Minimal migration complexity** as infrastructure automation is already in Ansible:
- **Testing Integration**: The repository uses Chef InSpec for compliance testing alongside Ansible automation - this hybrid approach is intentional and functional
- **Chef Server Dependencies**: Deployment scripts install Chef Automate/Server for InSpec execution, not for cookbook management
- **Compliance Automation**: InSpec profiles provide security validation that complements Ansible automation

### Migration Order

**No migration required** - this is a demonstration repository showing:
1. Ansible playbooks for infrastructure automation (already complete)
2. Chef InSpec for compliance testing and security validation
3. Test Kitchen integration for testing Ansible + InSpec workflows

### Assumptions

- This repository serves as an example/demonstration rather than production infrastructure requiring migration
- The Chef components (InSpec tests, Automate deployment scripts) are intentionally maintained alongside Ansible for compliance automation workflows
- The hybrid Chef InSpec + Ansible approach is the intended architecture, not a migration target
- No actual Chef cookbooks, recipes, or infrastructure-as-code exist in this repository that require conversion to Ansible
- The Test Kitchen configuration suggests this is used for development and testing of the Ansible + InSpec integration pattern
- Production environments using this pattern would maintain separate Chef InSpec profiles for compliance while using Ansible for configuration management