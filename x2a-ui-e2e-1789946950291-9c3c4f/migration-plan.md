# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains educational examples demonstrating Chef InSpec integration with Ansible playbooks rather than traditional Chef cookbooks requiring migration. The content is already primarily Ansible-based with InSpec used for compliance testing. Migration complexity is minimal as the core infrastructure automation is already implemented in Ansible.

## Module Migration Plan

This repository contains demonstration examples rather than production modules:

### MODULE INVENTORY

**website-https-demo**:
- Description: Apache web server with HTTPS configuration, SSL certificate generation, and virtual host setup for demonstration purposes
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Self-signed SSL certificates, Apache virtual host configuration, Ubuntu 20.04 targeting

**poodle-fix-demo**:
- Description: SSL/TLS security hardening demonstration that disables SSLv3 and enforces TLS 1.2 to mitigate POODLE vulnerability
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL protocol configuration, security compliance automation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification in Vagrant
- `tests/website_https_verify.rb`: InSpec compliance tests verifying HTTPS functionality, SSL protocols, and web service availability
- `tests/ssh_profile.rb`: InSpec security control testing SSH root login restrictions (STIG compliance)
- `setup-automate/deploy-automate.sh`: Chef Automate and Chef Infra Server deployment script for lab environments
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static HTML test content for web server verification

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (explicitly specified in kitchen.yml and playbook package versions)
- **Virtual Machine Technology**: Vagrant with VirtualBox (configured in Test Kitchen)
- **Cloud Platform**: Not specified (designed for on-premises or cloud VM deployment)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Already integrated for compliance testing - no migration needed, continue using for validation
- **Test Kitchen**: Currently configured for Ansible provisioning - maintain existing testing workflow
- **Apache 2.4.41**: Specific version pinned in playbook - verify availability in target environment

### Security Considerations

- **SSL/TLS Configuration**: Existing playbooks properly implement TLS 1.2 enforcement and disable vulnerable protocols
- **Certificate Management**: Self-signed certificates used for demonstration - production deployment requires proper CA-signed certificates
- **SSH Hardening**: InSpec tests verify SSH root login restrictions per STIG requirements
- **Credential Management**: Hardcoded credentials in deployment scripts (userpassword='password') - requires vault integration for production use

### Technical Challenges

- **Testing Framework Integration**: Repository demonstrates InSpec + Ansible integration - maintain this compliance testing approach
- **Educational vs Production**: Content is designed for learning/demonstration - production deployment requires additional hardening and configuration management
- **Chef Infrastructure Dependencies**: Deployment scripts install Chef Automate/Server - evaluate if these components are needed in target environment

### Migration Order

1. **No migration required** - Ansible playbooks are already production-ready
2. **Enhance security** - Replace hardcoded credentials with Ansible Vault
3. **Production hardening** - Replace self-signed certificates with proper CA certificates
4. **Testing integration** - Maintain InSpec compliance testing workflow

### Assumptions

- This repository serves as educational/demonstration content rather than production infrastructure requiring migration
- The existing Ansible playbooks represent the desired end state rather than legacy code to be migrated
- Chef InSpec will continue to be used for compliance testing alongside Ansible automation
- The Chef Automate/Server deployment scripts may not be needed if migrating away from Chef infrastructure entirely
- Target environments will maintain Ubuntu/Debian package management (apt) as configured in existing playbooks
- Self-signed certificates are acceptable for demonstration but will need replacement with proper certificates for production use