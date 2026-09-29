# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains educational examples demonstrating Chef InSpec integration with Ansible playbooks rather than traditional Chef cookbooks requiring migration. The content is already primarily Ansible-based with InSpec used for compliance testing. Migration complexity is minimal as the core infrastructure automation is already implemented in Ansible.

## Module Migration Plan

This repository contains demonstration examples that showcase Chef InSpec integration with Ansible:

### MODULE INVENTORY

**website-https-demo**:
- Description: Apache HTTPS web server deployment with SSL certificate generation, virtual host configuration, and security hardening
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (with Chef InSpec testing)
- Key Features: Self-signed SSL certificates via OpenSSL modules, Apache virtual host configuration, security compliance verification

**poodle-vulnerability-fix**:
- Description: SSL/TLS security hardening to address POODLE vulnerability by disabling SSLv3 and enforcing TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (with Chef InSpec testing)
- Key Features: Apache SSL protocol configuration, TLS version enforcement, compliance verification

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification in Vagrant environment
- `tests/website_https_verify.rb`: InSpec compliance tests verifying HTTPS functionality, SSL protocols, and web service availability
- `tests/ssh_profile.rb`: InSpec security profile testing SSH root login restrictions and STIG compliance controls
- `index.html`: Static HTML test content for web server verification
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script for demonstration environment
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with native Ansible testing solutions (ansible-test, molecule, or custom verification tasks)
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing and verification
- **Vagrant**: Can be retained or replaced with container-based testing (Docker, Podman)

### Security Considerations

- **SSL Certificate Management**: Current implementation uses self-signed certificates - consider integration with Let's Encrypt or enterprise CA for production
- **Hardcoded Credentials**: Deployment scripts contain plaintext passwords and should use Ansible Vault or external secret management
- **SSH Security**: InSpec profiles verify SSH hardening - ensure equivalent Ansible verification tasks
- **STIG Compliance**: Existing InSpec controls reference RHEL-08 STIG requirements - maintain compliance verification in pure Ansible

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec compliance tests to native Ansible verification requires rewriting Ruby-based tests as Ansible tasks or using alternative testing frameworks
- **Compliance Reporting**: InSpec provides structured compliance reporting - need equivalent reporting mechanism in pure Ansible environment
- **Multi-Platform Testing**: Current Test Kitchen setup supports multiple platforms - ensure Molecule configuration maintains this capability

### Migration Order

1. **Ansible Playbooks** (already complete - no migration needed)
2. **Testing Framework** (convert InSpec tests to Ansible verification tasks or Molecule scenarios)
3. **Deployment Scripts** (convert bash scripts to Ansible playbooks with proper secret management)

### Assumptions

- The primary goal is to eliminate Chef InSpec dependency while maintaining compliance testing capabilities
- Current Ansible playbooks are considered production-ready and don't require structural changes
- Test Kitchen will be replaced with Molecule for consistent Ansible-native testing
- Compliance requirements (STIG controls) must be maintained in the new testing framework
- Local development and testing workflow should remain similar to current Test Kitchen experience
- Self-signed certificates are acceptable for demonstration purposes but production deployment would require proper certificate management
- The repository serves educational purposes and may not require full production-grade migration