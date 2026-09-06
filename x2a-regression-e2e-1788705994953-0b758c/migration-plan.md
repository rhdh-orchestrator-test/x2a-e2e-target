# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains demonstration examples of using Chef InSpec for compliance testing alongside Ansible playbooks. The migration scope is minimal as the core automation is already in Ansible format, with the primary task being the replacement of Chef InSpec testing with native Ansible testing approaches. Timeline estimate: 1-2 weeks for a small team.

## Module Migration Plan

This repository contains Ansible playbooks with Chef InSpec compliance testing that need migration to pure Ansible solutions:

### MODULE INVENTORY

**website-https-deployment**:
- Description: Apache web server deployment with HTTPS/SSL configuration, self-signed certificate generation, and virtual host setup
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL/TLS enablement

**poodle-ssl-fix**:
- Description: SSL security hardening playbook that disables vulnerable SSL protocols and enforces TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL protocol configuration, POODLE vulnerability mitigation, service restart handling

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with InSpec verification
- `tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `tests/ssh_profile.rb`: Chef InSpec security compliance test for SSH root login restrictions (STIG control)
- `index.html`: Static HTML test file for web server validation
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox provider (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with Ansible's built-in testing modules (uri, assert, service_facts)
- **Test Kitchen**: Replace with molecule for Ansible testing framework
- **Chef Automate/Server**: Remove deployment scripts as they're not needed for pure Ansible workflow

### Security Considerations
- **SSL/TLS Configuration**: Current playbooks properly implement SSL certificate generation and secure protocol configuration
  - Self-signed certificate generation using openssl_* modules
  - Proper file permissions (0640) for certificate directories
  - TLS 1.2 enforcement and SSL 3.0 disabling for POODLE mitigation
- **SSH Hardening**: InSpec test validates SSH root login restrictions - migrate to Ansible assert module
- **Vault/secrets management**: No encrypted secrets detected - all configurations use inline variables and generated certificates

### Technical Challenges
- **InSpec Test Migration**: Convert Ruby-based InSpec tests to Ansible native testing
  - Port 443 listening check → use wait_for module
  - HTTP response validation → use uri module with return_content
  - SSL protocol verification → use openssl_certificate_info module
- **Test Kitchen Replacement**: Migrate from kitchen.yml to molecule.yml configuration
  - Vagrant driver configuration needs conversion to molecule format
  - InSpec verifier needs replacement with Ansible testinfra or native assertions
- **STIG Compliance Validation**: SSH root login test needs conversion from InSpec control to Ansible task with assert module

### Migration Order
1. **website-https-deployment** (Priority 1: Already in Ansible, only needs test migration)
2. **poodle-ssl-fix** (Priority 1: Simple Ansible playbook, minimal testing needs)
3. **Test framework migration** (Priority 2: Convert InSpec tests to Ansible native testing)
4. **Infrastructure cleanup** (Priority 3: Remove Chef-specific deployment scripts)

### Assumptions
- Target environment will continue to use Ubuntu 20.04 LTS as specified in current configuration
- Vagrant-based local testing approach will be maintained but migrated to molecule framework
- Self-signed certificates are acceptable for the demonstration/testing use case
- Apache 2.4.41 version pinning is intentional and should be preserved in migration
- SSH hardening requirements follow RHEL-08 STIG controls and should be maintained
- No production secrets or sensitive data are present in the repository
- The demonstration nature of the repository means comprehensive error handling may not be required
- Test Kitchen's ansible_playbook provisioner configuration suggests the playbooks are already production-ready
- Chef Automate deployment scripts are for demonstration purposes and not part of the core migration scope