# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository is a demonstration project showing Chef InSpec integration with Ansible for compliance automation, rather than a traditional Chef cookbook repository requiring migration. The repository contains existing Ansible playbooks with Chef InSpec test verification, deployment scripts for Chef infrastructure, and compliance testing examples. The migration scope is minimal as the core automation is already implemented in Ansible - the primary task is to replace Chef InSpec testing with native Ansible testing approaches.

## Module Migration Plan

This repository contains demonstration content that combines Ansible automation with Chef InSpec compliance testing:

### MODULE INVENTORY

**website-https-deployment**:
- Description: Apache web server deployment with SSL/TLS configuration, self-signed certificate generation, and virtual host setup for a "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL module activation

**poodle-vulnerability-fix**:
- Description: SSL/TLS security hardening to disable SSLv3 and enforce TLS 1.2 only, addressing the POODLE vulnerability
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL protocol configuration, TLS 1.2 enforcement, service restart handling

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification - needs replacement with native Ansible testing
- `tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality and SSL protocol verification
- `tests/ssh_profile.rb`: Chef InSpec security compliance test for SSH root login restrictions (STIG compliance)
- `setup-automate/deploy-automate.sh`: Chef Automate and Chef Infra Server deployment script for demonstration environment
- `setup-automate/deploy-chef-server.sh`: Chef Infra Server standalone deployment script
- `index.html`: Static HTML test content for web server verification

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with Ansible native testing modules (uri, assert, service, etc.)
- **Test Kitchen**: Replace with molecule for Ansible playbook testing
- **Chef Automate/Server**: Remove dependency - these are only needed for the demonstration environment

### Security Considerations
- **SSL/TLS Configuration**: The existing Ansible playbooks properly implement SSL security best practices:
  - Self-signed certificate generation with proper key management
  - SSL protocol hardening (TLS 1.2 enforcement, SSLv3 disabled)
  - Certificate file permissions (0640 for sensitive files)
- **SSH Security**: InSpec test verifies SSH root login is disabled - migrate to Ansible assert module
- **Vault/secrets management**: 
  - Hardcoded credentials in deployment scripts (userpassword='password')
  - SSL certificate paths and configuration embedded in playbook variables
  - No encrypted secrets or vault usage detected

### Technical Challenges
- **Testing Framework Migration**: Replace Chef InSpec tests with Ansible native testing approaches using uri, assert, and service modules for compliance verification
- **Compliance Reporting**: InSpec provides structured compliance reporting - need to implement equivalent reporting with Ansible facts and custom modules
- **STIG Compliance**: SSH security test follows STIG guidelines - ensure Ansible replacement maintains same compliance standards

### Migration Order
1. **Testing Infrastructure** (immediate priority): Replace Test Kitchen + InSpec with Molecule for Ansible testing
2. **Compliance Tests** (moderate complexity): Convert InSpec tests to Ansible assert and uri module tasks
3. **Documentation Update** (low complexity): Update README and examples to reflect pure Ansible approach

### Assumptions
- The existing Ansible playbooks are production-ready and do not require modification
- Chef InSpec testing can be replaced with equivalent Ansible native testing without loss of compliance verification capability
- The demonstration environment (Chef Automate/Server) is not required for production use
- Ubuntu 20.04 target platform will remain consistent for the migrated testing approach
- SSL certificate management approach (self-signed certificates) is acceptable for the target environment
- Test Kitchen vagrant driver configuration suggests this is a development/testing environment rather than production infrastructure