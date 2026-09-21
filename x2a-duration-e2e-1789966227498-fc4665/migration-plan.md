# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains example code demonstrating Chef InSpec integration with Ansible for compliance automation. **No actual migration is required** as the infrastructure automation is already implemented in Ansible. This is a demonstration/example repository showing how to use Chef InSpec as a testing framework alongside existing Ansible playbooks.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec test profiles that demonstrate compliance automation patterns:

### MODULE INVENTORY

**apache-https-website**:
- Description: Apache web server configuration with HTTPS/SSL setup, self-signed certificate generation, and virtual host deployment for a simple "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible
- Key Features: SSL certificate generation via OpenSSL modules, Apache virtual host configuration, package management for Ubuntu 20.04

**ssl-security-hardening**:
- Description: SSL/TLS security hardening playbook that disables vulnerable SSL protocols (POODLE vulnerability fix)
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible
- Key Features: Apache SSL configuration hardening, TLS 1.2 enforcement, service restart handling

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification in Vagrant
- `tests/website_https_verify.rb`: InSpec compliance tests verifying HTTPS functionality, SSL protocol configuration, and web service availability
- `tests/ssh_profile.rb`: InSpec security compliance profile testing SSH root login restrictions (STIG compliance)
- `index.html`: Static HTML test file for web server verification
- `setup-automate/deploy-automate.sh`: Chef Automate and Chef Infra Server deployment script for demonstration environment
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (as specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured in Test Kitchen for local development/testing)
- **Cloud Platform**: Not specified (designed for on-premises or cloud VM deployment)

## Migration Approach

### Key Dependencies to Address

**No migration dependencies** - this repository is already using Ansible for infrastructure automation:
- **apache2 (2.4.41-4ubuntu3.10)**: Already managed via Ansible apt module
- **openssl/python3-openssl**: Already managed via Ansible for certificate generation
- **Chef InSpec**: Used as testing framework, not for infrastructure provisioning

### Security Considerations

**Existing security implementations that should be maintained**:
- SSL/TLS hardening: Current playbook properly disables SSL 3.0 and enforces TLS 1.2
- Self-signed certificate generation: Uses proper OpenSSL Ansible modules with appropriate file permissions (0640 for certs directory)
- SSH security compliance: InSpec tests verify SSH root login restrictions per STIG requirements
- Service isolation: Apache virtual hosts configured with proper directory permissions and access controls

**Credential management**:
- Hardcoded credentials present in setup scripts (userpassword='password') - should be externalized to Ansible Vault
- SSL certificates generated dynamically - no hardcoded certificate files
- No encrypted data bags or Chef Vault usage detected

### Technical Challenges

**No significant migration challenges** as infrastructure is already Ansible-based:
- InSpec integration: Current Test Kitchen + InSpec setup provides compliance testing - consider migrating to ansible-test or molecule for pure Ansible testing workflow
- Demonstration environment: Setup scripts use Chef Automate for demo purposes but don't affect the actual infrastructure automation

### Migration Order

**No migration required** - repository structure is already optimal:
1. Ansible playbooks are production-ready and follow best practices
2. InSpec tests provide compliance verification and can continue to be used
3. Consider consolidating testing framework to pure Ansible ecosystem (molecule + testinfra) if desired

### Assumptions

- This repository serves as example/demonstration code rather than production infrastructure
- The Chef components (InSpec, Automate setup scripts) are used for testing and demonstration purposes only
- The actual infrastructure automation is already implemented in Ansible and follows current best practices
- Ubuntu 20.04 target platform is appropriate for the intended use case
- Test Kitchen + Vagrant workflow is acceptable for development/testing, or team is willing to migrate to molecule for testing
- Hardcoded credentials in setup scripts are acceptable for demonstration purposes but would need to be externalized for production use