# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains Chef-related examples and demonstration materials that showcase integration between Chef InSpec and Ansible. The migration scope is minimal as the repository already contains Ansible playbooks and primarily serves as educational content rather than production infrastructure code. The estimated timeline is 1-2 weeks for cleanup and documentation updates.

## Module Migration Plan

This repository contains mixed technologies with Ansible playbooks, Chef InSpec tests, and Chef server deployment scripts:

### MODULE INVENTORY

**website-https-demo**:
- Description: Apache web server with HTTPS configuration using self-signed certificates, virtual host setup, and SSL/TLS security hardening
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, SSL certificate generation via OpenSSL, virtual host configuration, security compliance

**poodle-ssl-fix**:
- Description: SSL/TLS security hardening playbook that disables vulnerable SSL protocols and enforces TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml  
- Technology: Ansible (already migrated)
- Key Features: Apache SSL protocol configuration, POODLE vulnerability mitigation, service restart handling

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification - requires updating for pure Ansible workflow
- `tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality and SSL protocol verification - needs conversion to Ansible testing framework
- `tests/ssh_profile.rb`: Chef InSpec security compliance test for SSH root login restrictions - needs conversion to Ansible testing framework
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script - can be retired or converted to Ansible automation
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script - can be retired or converted to Ansible automation
- `index.html`: Static test content for web server verification - no migration needed

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address

- **apache2 (2.4.41-4ubuntu3.10)**: Already using Ansible apt module - no migration needed
- **openssl**: Already using Ansible openssl_* modules - no migration needed  
- **python3-openssl**: Already using Ansible crypto modules - no migration needed
- **Test Kitchen**: Replace with native Ansible testing tools like ansible-test or molecule
- **Chef InSpec**: Convert compliance tests to Ansible-native testing frameworks

### Security Considerations

- **SSL/TLS Configuration**: Current playbooks already implement proper SSL hardening practices including TLS 1.2 enforcement and SSL 3.0 disabling
- **Certificate Management**: Self-signed certificate generation is already implemented using Ansible openssl modules - production environments should integrate with proper CA or Let's Encrypt
- **SSH Security**: InSpec test validates SSH root login restrictions - convert to Ansible assert tasks or molecule tests
- **File Permissions**: Proper file permissions (0640, 0644, 0755) are already configured in Ansible tasks
- **Service Security**: Apache and SSH service restart handlers are properly implemented

### Technical Challenges

- **Testing Framework Migration**: Converting Chef InSpec tests to Ansible-native testing requires rewriting Ruby-based tests into YAML-based assertions or Python-based molecule tests
- **Test Kitchen Replacement**: Current workflow uses Test Kitchen for orchestration - needs replacement with molecule or native Ansible testing tools
- **Chef Server Dependencies**: Deployment scripts assume Chef infrastructure - these can be retired or converted to Ansible-based Chef server automation

### Migration Order

1. **Testing Framework Conversion** (immediate priority - convert InSpec tests to Ansible testing)
2. **Documentation Updates** (update README files to reflect pure Ansible approach)
3. **Chef Server Scripts** (optional - convert deployment scripts to Ansible or retire)

### Assumptions

- This repository serves as educational/demonstration content rather than production infrastructure
- The existing Ansible playbooks are already functional and follow best practices
- Test Kitchen integration with InSpec is used for demonstration purposes showing Chef/Ansible integration
- Ubuntu 20.04 target environment is acceptable for continued use
- Self-signed certificates are acceptable for demonstration purposes
- Local development/testing environment is the primary use case
- Chef server deployment scripts may be retained for educational purposes about Chef infrastructure
- The repository maintainers want to showcase pure Ansible workflows rather than mixed Chef/Ansible approaches