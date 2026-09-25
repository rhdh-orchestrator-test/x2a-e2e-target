# MIGRATION FROM CHEF INSPEC TO ANSIBLE

This repository contains Chef InSpec compliance tests and Ansible playbooks demonstrating hybrid automation approaches. The migration involves consolidating InSpec testing capabilities into native Ansible testing frameworks while preserving compliance validation functionality. The scope is limited with low complexity, estimated timeline of 1-2 weeks for a small team.

## Module Migration Plan

This repository contains Chef InSpec compliance tests and supporting infrastructure that need migration planning:

### MODULE INVENTORY

**website-https-compliance**:
- Description: Apache HTTPS website deployment with SSL/TLS configuration, self-signed certificate generation, and compliance validation
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, SSL certificate generation via OpenSSL, virtual host configuration, HTTPS compliance testing

**poodle-vulnerability-fix**:
- Description: SSL/TLS security hardening to address POODLE vulnerability by disabling SSLv3 and enforcing TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL protocol configuration, TLS 1.2 enforcement, SSLv3 disabling

**website-https-verification**:
- Description: InSpec compliance tests for HTTPS website functionality and SSL/TLS security validation
- Path: chef-and-ansible/tests/website_https_verify.rb
- Technology: Chef InSpec
- Key Features: Port 443 listening verification, HTTPS response validation, SSL protocol compliance checks

**ssh-security-profile**:
- Description: InSpec compliance profile for SSH security hardening, specifically root login prevention
- Path: chef-and-ansible/tests/ssh_profile.rb
- Technology: Chef InSpec
- Key Features: STIG compliance (RHEL-08-000227), SSH root login verification, security control mapping

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `index.html`: Static HTML test content for website deployment validation
- `setup-automate/deploy-chef-server.sh`: Chef Infra Server deployment script for testing infrastructure
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (based on kitchen.yml platform specification and apt package manager usage)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver configuration)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with Ansible's built-in testing modules (uri, assert, service_facts) and external tools like Testinfra or Molecule
- **Test Kitchen**: Replace with Ansible Molecule for testing and validation workflows
- **Chef Automate**: Remove dependency on Chef infrastructure components

### Security Considerations
- **SSL/TLS Certificate Management**: Current implementation uses self-signed certificates generated via OpenSSL Ansible modules - no migration needed for certificate generation, but consider certificate authority integration for production
- **SSH Security Hardening**: InSpec SSH compliance tests need conversion to Ansible assert tasks or integration with external security scanning tools
- **Compliance Validation**: STIG compliance checks (RHEL-08-000227) currently implemented in InSpec need conversion to Ansible validation tasks
- **Credential Management**: No hardcoded credentials detected in reviewed files - deployment scripts use variables that should be externalized to Ansible Vault

### Technical Challenges
- **InSpec to Ansible Test Conversion**: Converting Chef InSpec compliance tests to native Ansible testing requires rewriting test logic using Ansible's assert module, uri module for HTTP checks, and service_facts for system validation
- **Compliance Framework Integration**: STIG compliance mappings and security control references need preservation during migration to maintain audit trail and compliance documentation
- **Test Kitchen Replacement**: Kitchen.yml workflow needs conversion to Ansible Molecule for maintaining test-driven development practices

### Migration Order
1. **website-https-compliance** and **poodle-vulnerability-fix** (already Ansible - no migration needed)
2. **website-https-verification** (convert InSpec tests to Ansible assert tasks)
3. **ssh-security-profile** (convert InSpec compliance profile to Ansible security validation playbook)

### Assumptions
- The repository serves as a demonstration/example rather than production infrastructure, reducing migration complexity
- Target environment will continue using Ubuntu/Debian-based systems given the apt package manager usage
- Test Kitchen workflow can be replaced with Ansible Molecule without loss of functionality
- InSpec compliance tests can be adequately replaced with Ansible's native testing capabilities
- Chef Automate infrastructure is used only for demonstration and can be decommissioned post-migration
- SSL certificate management will remain self-signed for testing purposes, though production may require CA integration
- STIG compliance requirements will be maintained through converted Ansible validation tasks