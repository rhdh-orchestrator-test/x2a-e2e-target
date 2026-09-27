# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains example code demonstrating Chef InSpec integration with Ansible rather than traditional Chef cookbooks requiring migration. The content is already primarily Ansible-based with InSpec for compliance testing. This represents a **demonstration repository** rather than production infrastructure requiring migration.

**Migration Scope**: Minimal - repository already uses Ansible playbooks
**Complexity**: Low - no Chef cookbooks present
**Timeline Estimate**: 1-2 days for cleanup and standardization

## Module Migration Plan

This repository contains example Ansible playbooks and Chef InSpec tests that demonstrate compliance automation patterns:

### MODULE INVENTORY

**website-https**:
- Description: Apache web server configuration with HTTPS/SSL setup, self-signed certificate generation, and virtual host management
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: SSL certificate generation via OpenSSL modules, Apache virtual host configuration, package management for Ubuntu 20.04

**poodle-fix**:
- Description: SSL protocol hardening playbook that disables SSLv3 and enforces TLS 1.2 to mitigate POODLE vulnerability
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL configuration replacement, service restart handlers

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `tests/ssh_profile.rb`: InSpec security control for SSH root login restrictions (STIG compliance)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static HTML test file for web server validation

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (explicitly specified in kitchen.yml and playbooks)
- **Virtual Machine Technology**: Vagrant (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

**No external Chef dependencies present** - this repository uses:
- **apache2 (2.4.41-4ubuntu3.10)**: Already managed via Ansible apt module
- **openssl/python3-openssl**: Certificate management handled by Ansible OpenSSL modules
- **Chef InSpec**: Compliance testing framework - retain for security validation

### Security Considerations

**SSL/TLS Configuration**: 
- Self-signed certificate generation is properly implemented using Ansible OpenSSL modules
- POODLE vulnerability mitigation enforces TLS 1.2 minimum
- Certificate files stored with appropriate permissions (0640)

**SSH Hardening**: 
- InSpec control validates SSH root login restrictions
- Compliance testing follows STIG guidelines (RHEL-08-000227)

**Credential Management**: 
- No hardcoded credentials detected in playbooks
- Certificate generation uses secure OpenSSL modules
- Service account management handled through proper Ansible patterns

### Technical Challenges

**Test Kitchen Integration**: 
- Current setup uses Test Kitchen with Ansible provisioner and InSpec verifier
- Consider migrating to molecule for Ansible-native testing workflow
- InSpec tests can be retained for compliance validation

**Chef Infrastructure Scripts**: 
- Deployment scripts in setup-automate/ are for Chef server installation
- These may be obsolete if migrating away from Chef ecosystem entirely
- Consider replacing with Ansible-based infrastructure provisioning

### Migration Order

1. **Standardization** (immediate): Review and standardize existing Ansible playbooks for production use
2. **Testing Framework** (1-2 days): Migrate from Test Kitchen to Molecule for Ansible testing
3. **Infrastructure Provisioning** (optional): Replace Chef server deployment scripts with Ansible equivalents

### Assumptions

- **Repository Purpose**: This appears to be a demonstration/example repository rather than production infrastructure
- **Chef InSpec Retention**: Assuming InSpec will be retained for compliance testing alongside Ansible
- **Target Environment**: Examples target Ubuntu 20.04; production targets may differ
- **Testing Requirements**: Current Test Kitchen + InSpec workflow may need adaptation for production CI/CD
- **Chef Infrastructure**: Setup scripts suggest this was part of a Chef-managed environment that may be transitioning to Ansible
- **Compliance Standards**: SSH hardening follows RHEL STIG guidelines; may need adaptation for other compliance frameworks
- **Certificate Management**: Self-signed certificates are acceptable for examples but production will likely require proper CA-signed certificates