# MIGRATION FROM CHEF INSPEC TO ANSIBLE

This repository contains demonstration examples of using Chef InSpec for compliance testing alongside Ansible playbooks. **No actual migration is required** as the content is already Ansible-based with InSpec used purely for testing and compliance verification. This is a reference implementation showing best practices for compliance automation rather than a traditional infrastructure-as-code repository requiring migration.

## Module Migration Plan

This repository contains example Ansible playbooks and Chef InSpec compliance tests that demonstrate integration patterns:

### MODULE INVENTORY

**No modules require migration** - this repository contains:

**ansible-apache-https**:
- Description: Ansible playbook demonstrating Apache HTTPS configuration with SSL certificate generation, virtual host setup, and security hardening
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Self-signed SSL certificates via OpenSSL modules, Apache virtual host configuration, package management

**ansible-ssl-hardening**:
- Description: Ansible playbook for SSL/TLS security hardening by disabling vulnerable protocols
- Path: chef-and-ansible/poodle_fix.yml  
- Technology: Ansible (already migrated)
- Key Features: POODLE vulnerability mitigation, TLS protocol enforcement, Apache SSL configuration

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `index.html`: Static HTML test content for web server validation
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `tests/ssh_profile.rb`: InSpec compliance profile for SSH security hardening verification
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script (infrastructure setup, not application code)
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script (infrastructure setup, not application code)

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address

**No migration dependencies** - this is already an Ansible-based implementation. Current dependencies include:

- **apache2 (2.4.41-4ubuntu3.10)**: Already managed via Ansible apt module
- **openssl/python3-openssl**: Certificate management handled by Ansible OpenSSL modules
- **Chef InSpec**: Used for compliance testing - can remain as-is or be replaced with Ansible molecule/testinfra

### Security Considerations

**Current security implementations (no migration needed):**
- SSL/TLS certificate management: Self-signed certificates generated via Ansible OpenSSL modules
- Protocol hardening: POODLE vulnerability mitigation through TLS protocol enforcement
- SSH hardening: InSpec compliance tests verify SSH root login restrictions
- File permissions: Proper ownership and permissions set on certificate files and web content

### Technical Challenges

**No migration challenges** - this repository demonstrates:
- **Integration Pattern**: Shows how Chef InSpec can complement Ansible for compliance testing
- **Testing Strategy**: Demonstrates infrastructure testing with InSpec alongside Ansible automation
- **Compliance Automation**: Example of continuous compliance verification in Ansible workflows

### Migration Order

**No migration required** - this repository serves as a reference implementation for:
1. Ansible playbook development with security best practices
2. InSpec integration for compliance testing
3. Test Kitchen usage for infrastructure testing workflows

### Assumptions

- This repository is a demonstration/example collection rather than production infrastructure code
- The Chef components (InSpec tests, Test Kitchen) are intentionally used for testing and compliance verification
- No actual Chef cookbooks or recipes exist that require migration to Ansible
- The setup scripts are for Chef server infrastructure deployment, not application configuration management
- Users may want to replace InSpec with Ansible-native testing tools (molecule, testinfra) but this is optional
- The examples target Ubuntu/Debian systems but could be adapted for RHEL/CentOS with package manager changes