# MIGRATION FROM MIXED TECHNOLOGIES TO ANSIBLE

This repository contains example Ansible playbooks, Chef InSpec compliance tests, and Chef infrastructure deployment scripts. **No actual migration is required** as the primary configuration management content is already implemented in Ansible. This is an educational/demonstration repository showing how Chef InSpec can complement Ansible for compliance automation.

## Module Migration Plan

This repository contains demonstration content that showcases Ansible and Chef InSpec integration rather than production infrastructure code requiring migration:

### MODULE INVENTORY

**No modules require migration** - the repository contains:

- **website_https**: 
  - Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed certificates, SSL/TLS security hardening, and virtual host setup
  - Path: chef-and-ansible/website_https.yml
  - Technology: Ansible (already target technology)
  - Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, SSL virtual host configuration, security hardening

- **poodle_fix**:
  - Description: Ansible playbook for SSL/TLS security remediation, specifically disabling SSLv3 and enforcing TLS 1.2 to address POODLE vulnerability
  - Path: chef-and-ansible/poodle_fix.yml  
  - Technology: Ansible (already target technology)
  - Key Features: Apache SSL protocol configuration, TLS 1.2 enforcement, service restart handling

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with Vagrant and InSpec verification
- `tests/website_https_verify.rb`: Chef InSpec compliance tests verifying HTTPS functionality, SSL/TLS protocol configuration, and security posture
- `tests/ssh_profile.rb`: Chef InSpec security control testing SSH root login restrictions (STIG compliance)
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server infrastructure
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying standalone Chef Infra Server
- `index.html`: Static HTML test content for web server verification

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address

**No migration dependencies** - this is a demonstration repository. However, for teams adopting this pattern:

- **Chef InSpec**: Continue using for compliance testing alongside Ansible
- **Test Kitchen**: Retain for integration testing of Ansible playbooks
- **Vagrant**: Keep for local development environment provisioning

### Security Considerations

The existing Ansible playbooks demonstrate good security practices that should be maintained:

- **SSL/TLS Configuration**: Playbooks show proper SSL certificate management and protocol hardening
- **Self-signed Certificates**: Current implementation uses self-signed certs for testing - production deployments should integrate with proper CA or Let's Encrypt
- **SSH Hardening**: InSpec tests verify SSH root login restrictions per STIG requirements
- **File Permissions**: Proper file mode settings for certificates and configuration files (0640, 0644, 0755)

### Technical Challenges

**No migration challenges** - content is already in Ansible format. Potential considerations for teams using this pattern:

- **InSpec Integration**: Teams need to maintain Chef InSpec alongside Ansible for compliance automation
- **Test Kitchen Complexity**: Kitchen configuration requires understanding of both Ansible and Chef ecosystems
- **Certificate Management**: Production environments need proper certificate lifecycle management beyond self-signed certificates

### Migration Order

**No migration required** - this repository serves as a reference implementation for:

1. Ansible playbook development with security best practices
2. Chef InSpec integration for compliance verification  
3. Test Kitchen usage for Ansible playbook testing
4. Chef infrastructure deployment automation

### Assumptions

- This repository is intended for educational/demonstration purposes showing Ansible and Chef InSpec integration
- No production workloads are managed by this code
- The Chef deployment scripts are for setting up Chef infrastructure to support other environments, not for migration
- Teams using this pattern already have Ansible expertise and are adding Chef InSpec for compliance automation
- The Ubuntu 20.04 target platform and specific Apache version (2.4.41-4ubuntu3.10) are appropriate for the intended use case
- Self-signed certificates are acceptable for the demonstration/testing context