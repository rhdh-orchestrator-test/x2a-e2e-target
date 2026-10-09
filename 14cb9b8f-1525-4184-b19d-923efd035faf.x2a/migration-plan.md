# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository is a demonstration project showing Chef InSpec integration with Ansible for compliance automation. The migration scope is limited as the repository already contains Ansible playbooks with Chef InSpec used only for testing and compliance verification. The primary migration task involves replacing Chef InSpec tests with native Ansible testing frameworks while preserving the compliance automation capabilities.

## Module Migration Plan

This repository contains demonstration content that combines Ansible automation with Chef InSpec compliance testing:

### MODULE INVENTORY

**apache-https-website**:
- Description: Apache web server configuration with HTTPS/SSL setup, self-signed certificate generation, and virtual host deployment for a simple "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: SSL certificate generation via OpenSSL, Apache virtual host configuration, package management for Ubuntu 20.04

**ssl-security-hardening**:
- Description: SSL/TLS security hardening playbook that disables vulnerable SSL protocols (POODLE vulnerability fix) and enforces TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL protocol configuration, vulnerability remediation, service restart handling

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification in Vagrant environment
- `tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality, SSL protocol verification, and web service validation
- `tests/ssh_profile.rb`: Chef InSpec security compliance test for SSH root login restrictions (STIG compliance)
- `setup-automate/deploy-chef-server.sh`: Chef Infra Server deployment script for demonstration environment
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `index.html`: Static HTML test content for web server validation

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (explicitly specified in kitchen.yml and playbook package versions)
- **Virtual Machine Technology**: Vagrant with VirtualBox (configured in Test Kitchen)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible native testing modules (ansible.builtin.uri, ansible.builtin.service_facts, community.crypto.openssl_certificate_info)
- **Test Kitchen**: Replace with Ansible Molecule for testing framework
- **Chef Automate/Server**: Remove dependency - not needed for pure Ansible environment

### Security Considerations

- **SSL/TLS Configuration**: Current playbooks implement proper SSL hardening practices that should be preserved
  - Self-signed certificate generation using community.crypto collection
  - TLS 1.2 enforcement and SSL 3.0 disabling
  - Proper file permissions on certificate files (0640)
- **SSH Security**: InSpec test validates SSH root login restrictions - implement equivalent Ansible assertions
- **Compliance Automation**: Current STIG compliance checks (V-38607, RHEL-08-000227) need native Ansible verification
- **Credential Management**: No hardcoded credentials detected - uses variables and generated certificates

### Technical Challenges

- **Testing Framework Migration**: Converting Chef InSpec tests to Ansible native testing requires:
  - Replacing InSpec `describe` blocks with Ansible `assert` tasks
  - Converting SSL protocol verification to use `community.crypto.openssl_certificate_info`
  - Implementing HTTP response validation with `ansible.builtin.uri` module
- **Compliance Reporting**: Loss of InSpec's compliance reporting capabilities - consider integrating with Ansible compliance collections
- **Test Kitchen Replacement**: Migrating from Test Kitchen to Molecule requires restructuring test scenarios and verification methods

### Migration Order

1. **Testing Framework Setup** (low risk, foundational)
   - Install and configure Ansible Molecule
   - Create molecule scenarios replacing Test Kitchen suites
2. **InSpec Test Conversion** (moderate complexity)
   - Convert website_https_verify.rb to Ansible verification tasks
   - Convert ssh_profile.rb STIG compliance checks to Ansible assertions
3. **Infrastructure Cleanup** (low risk)
   - Remove Chef Server deployment scripts
   - Update documentation to reflect pure Ansible approach

### Assumptions

- The existing Ansible playbooks are already well-structured and follow best practices
- Ubuntu 20.04 remains the target platform (package versions may need updates for newer releases)
- Test Kitchen/Vagrant testing environment can be replaced with Molecule/Docker for faster testing cycles
- Chef InSpec compliance reporting features are not critical business requirements
- The demonstration nature of this repository means production-grade secret management is not implemented
- SSL certificate management will continue using self-signed certificates for demonstration purposes
- The current Apache configuration patterns are suitable for the target environment
- No external Chef cookbook dependencies exist that would complicate migration
- The repository serves as educational/demonstration content rather than production infrastructure code