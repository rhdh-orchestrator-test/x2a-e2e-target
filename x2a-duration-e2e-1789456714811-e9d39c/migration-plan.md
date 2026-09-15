# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains example code demonstrating Chef InSpec integration with Ansible for compliance automation. The repository is already primarily Ansible-based with InSpec used for compliance testing. This represents a **documentation and testing framework migration** rather than a traditional infrastructure-as-code migration, with minimal complexity and a short timeline estimate of 1-2 weeks.

## Module Migration Plan

This repository contains Ansible playbooks with Chef InSpec compliance tests that need migration planning:

### MODULE INVENTORY

**website-https**:
- Description: Apache web server configuration with SSL/TLS setup, self-signed certificate generation, and virtual host deployment for a "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL module activation

**poodle-fix**:
- Description: SSL security hardening playbook that disables vulnerable SSL protocols and enforces TLS 1.2 only to mitigate POODLE vulnerability
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL protocol configuration, TLS 1.2 enforcement, service restart handling

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification on Ubuntu 20.04
- `tests/website_https_verify.rb`: InSpec compliance tests verifying HTTPS functionality, SSL protocol configuration, and web service availability
- `tests/ssh_profile.rb`: InSpec security compliance test ensuring SSH root login is disabled (STIG compliance)
- `index.html`: Static HTML test file for web server verification
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script for testing infrastructure
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with Ansible compliance modules (ansible.posix.firewalld, community.crypto.openssl_certificate_info) or native Ansible testing
- **Test Kitchen**: Replace with molecule for Ansible playbook testing
- **Chef Automate/Server**: Remove dependency on Chef infrastructure components

### Security Considerations
- SSL/TLS certificate management: Current implementation uses self-signed certificates - consider integration with Let's Encrypt or enterprise CA
- SSH hardening: InSpec test verifies PermitRootLogin disabled - ensure Ansible playbooks enforce this configuration
- Apache security: SSL protocol restrictions properly configured to prevent POODLE attacks
- Credential patterns identified:
  - Hardcoded passwords in Chef server deployment scripts (userpassword='password')
  - SSL certificate and key file paths in Apache configuration
  - No encrypted data bags or vault usage detected

### Technical Challenges
- **InSpec to Ansible Testing Migration**: Converting Ruby-based InSpec tests to Ansible native testing or alternative compliance frameworks
- **Test Kitchen Replacement**: Migrating from Test Kitchen to Molecule for playbook testing and verification
- **Compliance Framework**: Establishing new compliance testing workflow without Chef InSpec dependency

### Migration Order
1. **Ansible Playbook Validation** (already complete - playbooks are functional)
2. **Testing Framework Migration** (replace Test Kitchen with Molecule)
3. **Compliance Test Conversion** (convert InSpec tests to Ansible native or alternative framework)

### Assumptions
- The repository serves as example/demonstration code rather than production infrastructure
- Current Ansible playbooks are functional and don't require structural changes
- InSpec compliance testing can be replaced with Ansible native testing capabilities or alternative compliance frameworks
- Chef Automate/Server deployment scripts are for testing purposes only and not part of the target production environment
- SSL certificate management will transition from self-signed to proper certificate authority integration
- Ubuntu 20.04 target environment assumption based on Test Kitchen configuration may need validation for production deployment