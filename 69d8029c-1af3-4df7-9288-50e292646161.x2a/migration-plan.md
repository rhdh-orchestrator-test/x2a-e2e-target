# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains demonstration examples of Chef InSpec integration with Ansible playbooks for compliance automation. The migration scope is minimal as the infrastructure automation is already implemented in Ansible, with Chef InSpec serving as the compliance verification layer. The primary migration task involves replacing Chef InSpec tests with native Ansible testing approaches or alternative compliance frameworks.

## Module Migration Plan

This repository contains Ansible playbooks with Chef InSpec compliance tests that need migration planning:

### MODULE INVENTORY

**apache-https-website**:
- Description: Apache web server deployment with HTTPS/SSL configuration, self-signed certificate generation, and virtual host setup for a test website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (primary) + Chef InSpec (testing)
- Key Features: SSL certificate generation via OpenSSL, Apache virtual host configuration, directory structure creation, service management

**ssl-security-hardening**:
- Description: SSL/TLS security hardening for Apache to disable vulnerable protocols (POODLE vulnerability fix)
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (primary) + Chef InSpec (testing)
- Key Features: SSL protocol configuration, Apache module management, security compliance enforcement

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with Ansible provisioner and InSpec verifier
- `chef-and-ansible/index.html`: Static HTML test content for web server validation
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality, SSL protocol validation, and web service verification
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec security compliance test for SSH root login restrictions (STIG compliance)
- `setup-automate/deploy-automate.sh`: Chef Automate and Chef Infra Server deployment script for testing infrastructure
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible native testing modules (uri, assert, service_facts) or alternative compliance frameworks like Testinfra
- **Test Kitchen**: Replace with Ansible Molecule for testing and validation workflows
- **Chef Automate/Server**: Remove dependency as these are only used for demonstration purposes, not production infrastructure

### Security Considerations

- **SSL/TLS Configuration Management**: Current playbooks handle SSL certificate generation and protocol hardening
  - Self-signed certificate generation using openssl_* modules
  - SSL protocol restriction to TLS 1.2+ for POODLE vulnerability mitigation
  - Apache SSL module configuration and virtual host security settings
- **SSH Security Compliance**: InSpec test validates SSH root login restrictions per STIG requirements
  - Migration should include Ansible tasks to enforce SSH security configurations
  - Consider implementing ansible-hardening role or custom security baseline playbooks
- **Vault/secrets management**: No encrypted credentials detected - uses hardcoded test values and self-signed certificates
  - Production migration should implement Ansible Vault for sensitive data management

### Technical Challenges

- **Compliance Testing Migration**: Converting Chef InSpec Ruby-based tests to Ansible native testing
  - InSpec's declarative testing syntax needs translation to Ansible assert/uri/command modules
  - SSL protocol testing requires alternative validation methods (openssl s_client, nmap, or custom scripts)
  - STIG compliance validation needs mapping to Ansible security roles or custom verification tasks
- **Test Kitchen Replacement**: Migrating from Test Kitchen to Ansible Molecule
  - Kitchen.yml configuration needs conversion to molecule.yml scenarios
  - Vagrant driver configuration requires mapping to Molecule's delegated or vagrant driver
  - Verifier integration needs replacement with Molecule's built-in or custom verifiers

### Migration Order

1. **apache-https-website** (Priority 1: Already Ansible-native, minimal InSpec dependency)
2. **ssl-security-hardening** (Priority 2: Simple playbook with focused compliance requirements)
3. **Testing Infrastructure** (Priority 3: Test Kitchen to Molecule migration, InSpec test conversion)

### Assumptions

- The repository serves as a demonstration/proof-of-concept rather than production infrastructure code
- Target environment will continue using Ubuntu/Debian-based systems with Apache web server
- Compliance requirements (STIG, SSL/TLS hardening) remain the same in the target Ansible-only environment
- Test Kitchen and Chef InSpec are acceptable to remove in favor of Ansible-native testing approaches
- The Chef Automate/Server deployment scripts are for demonstration purposes and not required in production
- Self-signed certificates are acceptable for testing; production deployment will use proper CA-signed certificates
- SSH security compliance requirements follow the same STIG guidelines currently tested by InSpec
- Vagrant-based local testing environment will be maintained or replaced with equivalent Molecule scenarios