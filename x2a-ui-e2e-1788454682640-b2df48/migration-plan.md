# MIGRATION FROM ANSIBLE TO ANSIBLE

This repository is already primarily Ansible-based with Chef InSpec testing integration. The migration scope is minimal as the core infrastructure automation is already implemented in Ansible. The repository contains demonstration examples for using Chef InSpec alongside Ansible for compliance automation, plus Chef server deployment utilities.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that demonstrate compliance automation integration:

### MODULE INVENTORY

**ansible-apache-ssl**:
- Description: Apache web server with SSL/TLS configuration, self-signed certificate generation, and virtual host setup for HTTPS website deployment
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible
- Key Features: OpenSSL certificate generation, Apache virtual host configuration, SSL module activation, directory structure creation

**ansible-ssl-hardening**:
- Description: SSL/TLS security hardening playbook that disables vulnerable SSL protocols and enforces TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible
- Key Features: Apache SSL protocol configuration, POODLE vulnerability mitigation, service restart handlers

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests for HTTPS website functionality and SSL protocol validation
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec security control for SSH root login verification (STIG compliance)
- `chef-and-ansible/index.html`: Static HTML test file for web server validation
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured as Test Kitchen driver)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

**No external dependencies requiring migration** - The Ansible playbooks use standard modules:
- **apt**: Native Ansible package management module
- **file**: Native Ansible file system module  
- **copy**: Native Ansible file deployment module
- **openssl_privatekey/openssl_csr/openssl_certificate**: Ansible community.crypto collection modules
- **command**: Native Ansible command execution module
- **service**: Native Ansible service management module

### Security Considerations

**SSL/TLS Certificate Management**: 
- Current implementation uses self-signed certificates generated via Ansible OpenSSL modules
- Migration approach: Already using Ansible best practices with community.crypto collection
- Recommendation: Consider Let's Encrypt integration for production environments

**SSH Security Hardening**:
- InSpec control validates SSH root login is disabled (STIG compliance)
- Migration approach: Already implemented as InSpec test, no Ansible migration needed
- Current security posture: Follows RHEL-08-000227 STIG requirement

**SSL Protocol Hardening**:
- Ansible playbook disables SSL 3.0 and enforces TLS 1.2 (POODLE vulnerability mitigation)
- Migration approach: Already implemented in Ansible, no changes needed
- Security validation: InSpec tests verify protocol configuration

### Technical Challenges

**No significant technical challenges identified** - Repository is already Ansible-native:
- Playbooks follow Ansible best practices with proper task naming, handlers, and variable usage
- InSpec integration provides compliance validation framework
- Test Kitchen provides automated testing infrastructure

**Minor optimization opportunities**:
- Consider migrating from deprecated `apt: update_cache=true` syntax to `ansible.builtin.apt` with `update_cache: true`
- Replace `command` module usage with more specific Ansible modules where available (a2ensite/a2dissite could use `apache2_module`)

### Migration Order

**No migration required** - Repository is already Ansible-based. Recommended maintenance order:

1. **Ansible Syntax Modernization** (low risk, immediate value)
   - Update deprecated module syntax in existing playbooks
   - Add FQCN (Fully Qualified Collection Names) for all modules

2. **InSpec Test Enhancement** (moderate complexity)
   - Expand InSpec test coverage for additional security controls
   - Add performance and configuration validation tests

3. **Chef Server Integration Optimization** (high complexity, optional)
   - Consider replacing Chef server deployment scripts with Ansible playbooks
   - Evaluate Chef Automate alternatives for compliance reporting

### Assumptions

- **Test Kitchen Integration**: Assumes continued use of Test Kitchen for Ansible playbook testing, which is an uncommon but valid approach
- **InSpec Dependency**: Repository demonstrates Chef InSpec integration with Ansible, suggesting organizational commitment to Chef InSpec for compliance testing
- **Development Environment**: Kitchen.yml configuration suggests this is primarily for development/testing rather than production deployment
- **Ubuntu Target Platform**: All configurations are Ubuntu-specific, may require adaptation for other Linux distributions
- **Self-Signed Certificates**: Current SSL implementation uses self-signed certificates, production use would require CA-signed or Let's Encrypt certificates
- **Static Configuration**: Playbooks use hardcoded values rather than inventory variables, limiting reusability across environments
- **Chef Server Purpose**: Deployment scripts suggest parallel Chef infrastructure, possibly for comparison or migration scenarios
- **Compliance Framework**: InSpec tests reference STIG controls, indicating government or high-security environment requirements