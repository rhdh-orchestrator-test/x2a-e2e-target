# MIGRATION FROM ANSIBLE EXAMPLES TO ANSIBLE

This repository contains Ansible playbooks and Chef InSpec compliance tests that demonstrate integration between Ansible automation and Chef InSpec compliance validation. The migration scope is minimal as the core automation is already in Ansible format, but requires restructuring for production use and separation of concerns between automation and compliance testing.

## Module Migration Plan

This repository contains Ansible playbooks and supporting infrastructure that need reorganization and production-readiness improvements:

### MODULE INVENTORY

**website-https**:
- Description: Apache web server deployment with SSL/TLS configuration, self-signed certificate generation, and virtual host setup for a "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, SSL virtual host configuration, directory structure creation, service management

**poodle-ssl-fix**:
- Description: SSL security hardening playbook that fixes POODLE vulnerability by disabling SSLv3 and enforcing TLS 1.2 in Apache configuration
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible
- Key Features: Apache SSL protocol configuration, service restart handlers, security compliance remediation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with Ansible provisioner and InSpec verifier
- `chef-and-ansible/index.html`: Static HTML test file for web server validation
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality, SSL protocol validation, and web service verification
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec security compliance test for SSH root login restrictions (STIG control)
- `setup-automate/deploy-automate.sh`: Chef Automate and Chef Infra Server deployment script for infrastructure setup
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (based on Test Kitchen platform configuration and apt package manager usage)
- **Virtual Machine Technology**: Vagrant with VirtualBox (based on kitchen.yml driver configuration)
- **Cloud Platform**: Not specified (designed for on-premises or cloud VM deployment)

## Migration Approach

### Key Dependencies to Address
- **apache2 (2.4.41-4ubuntu3.10)**: Already using Ansible apt module, no migration needed
- **openssl**: Already using Ansible openssl_* modules for certificate management
- **python3-openssl**: Required for Ansible OpenSSL modules, already specified
- **curl**: Standard utility, already managed via Ansible apt module
- **Test Kitchen**: Ruby-based testing framework, consider migration to molecule for Ansible-native testing

### Security Considerations
- **SSL/TLS Certificate Management**: Currently uses self-signed certificates generated via Ansible openssl modules. Production deployment should integrate with proper CA or certificate management system
- **Hardcoded Credentials**: SSH and web service configurations use default security settings. No sensitive credentials detected in playbooks
- **STIG Compliance**: InSpec tests implement RHEL-08-000227 STIG control for SSH security. Ansible playbooks should include corresponding hardening tasks
- **SSL Protocol Security**: POODLE fix playbook addresses CVE-2014-3566 by disabling SSLv3. Consider implementing comprehensive SSL/TLS security baseline

### Technical Challenges
- **Testing Framework Migration**: Current Test Kitchen + InSpec setup needs migration to Ansible-native testing (Molecule + Testinfra/pytest)
- **Compliance Integration**: InSpec compliance tests are separate from automation. Consider integrating compliance checks directly into Ansible playbooks or implementing continuous compliance monitoring
- **Infrastructure Deployment**: Chef Automate deployment scripts are bash-based. Consider migrating to Ansible playbooks for consistent infrastructure-as-code approach
- **Hardcoded Variables**: Playbooks contain embedded configuration. Implement proper variable management with group_vars, host_vars, and Ansible Vault

### Migration Order
1. **website-https** (low risk, self-contained web server deployment)
2. **poodle-ssl-fix** (security hardening, depends on Apache configuration)
3. **Infrastructure deployment scripts** (convert bash scripts to Ansible playbooks)
4. **Testing framework** (migrate from Test Kitchen to Molecule)

### Assumptions
- The current Ansible playbooks are demonstration/example code and not production-ready
- Target environment will require proper certificate management instead of self-signed certificates
- Production deployment will need proper inventory management, variable separation, and secret management
- The Chef InSpec compliance tests indicate a requirement for ongoing compliance validation in the target environment
- The repository serves as educational material for Chef InSpec + Ansible integration rather than production infrastructure code
- Ubuntu package versions and Apache configuration paths may need updates for current LTS releases
- The bash deployment scripts assume specific Chef Automate licensing and network connectivity requirements