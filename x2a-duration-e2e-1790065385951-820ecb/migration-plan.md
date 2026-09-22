# MIGRATION FROM MIXED ANSIBLE/CHEF INSPEC TO ANSIBLE

This repository contains example Ansible playbooks with Chef InSpec compliance testing and Chef infrastructure deployment scripts. The primary content is already in Ansible format, with Chef InSpec used for compliance verification. This represents a minimal migration scope focused on replacing InSpec testing with native Ansible testing approaches and migrating deployment scripts from Bash to Ansible.

## Module Migration Plan

This repository contains demonstration/example content rather than production infrastructure modules:

### MODULE INVENTORY

**website-https-deployment**:
- Description: Apache web server deployment with SSL/TLS configuration, self-signed certificate generation, and virtual host setup for a "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL module activation

**poodle-vulnerability-fix**:
- Description: SSL/TLS security hardening to disable SSLv3 and enforce TLS 1.2 only (POODLE vulnerability mitigation)
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL protocol configuration, service restart handlers

**chef-infrastructure-deployment**:
- Description: Bash scripts for deploying Chef Automate and Chef Infra Server with user and organization setup
- Path: setup-automate/
- Technology: Bash scripts
- Key Features: Chef Automate CLI deployment, user creation, organization setup, system tuning parameters

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration using Ansible provisioner with InSpec verifier for compliance testing
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality, SSL protocol verification, and service availability
- `tests/ssh_profile.rb`: InSpec security compliance test for SSH root login restrictions (STIG compliance)
- `index.html`: Static HTML test content for web server verification
- `deploy-automate.sh`: Chef Automate and Infra Server deployment automation
- `deploy-chef-server.sh`: Standalone Chef Infra Server deployment automation

### Target Details

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml), with Chef infrastructure scripts targeting Linux systems
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml for testing)
- **Cloud Platform**: Not specified - scripts support both on-premises and cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible native testing modules (uri, assert, service, etc.) or molecule with testinfra
- **Test Kitchen**: Replace with molecule for Ansible testing framework
- **Chef Automate CLI**: Convert Bash deployment scripts to Ansible playbooks using package, service, and command modules

### Security Considerations

- **SSL/TLS Configuration**: Current playbooks already implement proper SSL hardening (TLS 1.2 enforcement, SSLv3 disabling)
- **Certificate Management**: Self-signed certificates are generated using Ansible openssl modules - production deployment should integrate with proper CA or Let's Encrypt
- **SSH Hardening**: InSpec tests verify SSH root login restrictions - migrate to Ansible assert module or molecule tests
- **Credential Management**: 
  - Hardcoded credentials in Chef deployment scripts (userpassword='password')
  - No vault usage detected in current Ansible playbooks
  - Chef server certificates and keys generated during deployment

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec Ruby-based tests to Ansible native testing requires rewriting test logic in YAML/Jinja2
- **Chef Infrastructure Dependencies**: Deployment scripts rely on Chef Automate CLI and chef-server-ctl commands that have no direct Ansible equivalents
- **Compliance Framework**: InSpec provides STIG/CIS compliance testing - need to identify Ansible-native compliance testing alternatives

### Migration Order

1. **Testing Framework** (low risk, high value) - Convert InSpec tests to Ansible molecule with testinfra or native assert modules
2. **Chef Deployment Scripts** (moderate complexity) - Convert Bash scripts to Ansible playbooks using package, service, and uri modules
3. **Integration Testing** (high complexity) - Establish new CI/CD pipeline without Test Kitchen dependency

### Assumptions

- The repository serves as demonstration/example content rather than production infrastructure
- Current Ansible playbooks are already production-ready and require no migration
- Chef InSpec is used solely for compliance testing, not configuration management
- Target environment will maintain Ubuntu/Debian package management (apt module usage)
- Self-signed certificates are acceptable for demonstration purposes
- Chef infrastructure deployment is still required in the target environment
- Test Kitchen integration can be replaced with molecule or native Ansible testing
- Hardcoded credentials in deployment scripts are acceptable for demonstration purposes
- No external Chef cookbook dependencies exist that require migration