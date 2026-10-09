# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository is a demonstration project showing Chef InSpec integration with Ansible for compliance automation. The migration scope is limited as the repository already contains Ansible playbooks with Chef InSpec used only for testing and compliance verification. The primary migration task involves replacing Chef InSpec tests with native Ansible testing frameworks while preserving the compliance automation capabilities.

**Timeline Estimate**: 1-2 weeks
**Complexity**: Low to Medium
**Risk Level**: Low (existing Ansible infrastructure, minimal Chef dependencies)

## Module Migration Plan

This repository contains demonstration examples that combine Ansible automation with Chef InSpec compliance testing:

### MODULE INVENTORY

**website-https-deployment**:
- Description: Apache web server deployment with HTTPS/SSL configuration, self-signed certificate generation, and virtual host setup for a "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, SSL certificate generation via OpenSSL, virtual host configuration, directory structure creation

**ssl-security-hardening**:
- Description: SSL/TLS security hardening playbook that disables vulnerable SSL protocols and enforces TLS 1.2+ for Apache
- Path: chef-and-ansible/poodle_fix.yml  
- Technology: Ansible (already migrated)
- Key Features: POODLE vulnerability mitigation, SSL protocol configuration, Apache SSL module management

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification in Vagrant environment
- `tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality, SSL protocol verification, and web service validation
- `tests/ssh_profile.rb`: Chef InSpec security compliance test for SSH root login restrictions (STIG compliance)
- `index.html`: Static HTML test content for web server validation
- `setup-automate/deploy-automate.sh`: Chef Automate and Chef Infra Server deployment script for demonstration environment
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible native testing modules (ansible.builtin.uri, ansible.builtin.service_facts, community.crypto.openssl_certificate_info)
- **Test Kitchen**: Replace with molecule for Ansible testing framework
- **Chef Automate/Server**: Remove deployment scripts as they are only needed for demonstration purposes

### Security Considerations

- **SSL/TLS Configuration Management**: Current playbooks properly implement SSL hardening and certificate management
  - Self-signed certificate generation using community.crypto collection
  - SSL protocol enforcement (TLS 1.2+) with proper Apache configuration
  - No hardcoded credentials detected in playbooks
- **SSH Security Compliance**: InSpec test validates SSH root login restrictions per STIG requirements
  - Migration should include Ansible tasks to enforce SSH hardening
  - Consider implementing ansible-hardening role for comprehensive security baseline
- **Vault/Secrets Management**: No sensitive credentials found in current implementation
  - Uses default passwords in deployment scripts (demonstration only)
  - Production migration should implement Ansible Vault for credential management

### Technical Challenges

- **InSpec Test Translation**: Converting Chef InSpec compliance tests to Ansible native verification
  - Port listening checks: Use ansible.builtin.wait_for module
  - HTTP response validation: Use ansible.builtin.uri module with return_content
  - SSL protocol verification: Use community.crypto.openssl_certificate_info module
  - SSH configuration validation: Use ansible.builtin.lineinfile with check mode
- **Test Kitchen Replacement**: Migrating from Test Kitchen to Molecule testing framework
  - Requires new molecule.yml configuration
  - Vagrant driver configuration for molecule
  - Test scenarios adaptation from InSpec to Ansible assertions
- **Compliance Reporting**: Replacing InSpec compliance reporting capabilities
  - Consider ansible-lint for static analysis
  - Implement custom Ansible modules for compliance validation
  - Integration with external compliance tools (OpenSCAP, Nessus, etc.)

### Migration Order

1. **SSL Hardening Module** (chef-and-ansible/poodle_fix.yml) - Already complete, add native Ansible testing
2. **Web Server Deployment** (chef-and-ansible/website_https.yml) - Already complete, enhance with compliance tasks
3. **Testing Framework Migration** - Replace Test Kitchen + InSpec with Molecule + native Ansible tests
4. **Compliance Integration** - Implement comprehensive security baseline using ansible-hardening or similar roles

### Assumptions

- **Demonstration Purpose**: Repository appears to be for educational/demonstration purposes rather than production infrastructure
- **Ubuntu Target Environment**: All configurations assume Ubuntu/Debian-based systems; migration to other distributions would require package manager and service name adjustments
- **Local Development Focus**: Current setup uses Vagrant for local testing; production deployment would require cloud provider or bare metal configurations
- **InSpec Dependency**: Current compliance validation relies heavily on Chef InSpec; organization may want to maintain InSpec alongside Ansible for compliance reporting
- **Security Requirements**: STIG compliance requirements (evidenced by ssh_profile.rb) suggest government or high-security environment standards must be maintained
- **Certificate Management**: Current implementation uses self-signed certificates; production migration should consider Let's Encrypt or enterprise CA integration
- **Apache Web Server**: All configurations assume Apache HTTP server; migration to Nginx or other web servers would require significant playbook modifications