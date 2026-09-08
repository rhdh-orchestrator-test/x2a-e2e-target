# MIGRATION FROM MIXED CHEF/ANSIBLE TO ANSIBLE

This repository is a demonstration/example repository that showcases using Chef InSpec for compliance testing alongside Ansible playbooks. The repository does not contain traditional Chef cookbooks requiring migration, but rather contains existing Ansible playbooks with Chef InSpec compliance tests and Chef server deployment scripts. The migration scope is minimal as the core automation is already in Ansible format.

## Module Migration Plan

This repository contains mixed technologies with limited migration requirements:

### MODULE INVENTORY

**website-https**:
- Description: Apache web server configuration with SSL/TLS setup, self-signed certificate generation, and virtual host deployment for a "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL module activation

**poodle-fix**:
- Description: SSL security hardening playbook that disables SSLv3 and enforces TLS 1.2 to mitigate POODLE vulnerability
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL protocol configuration, TLS 1.2 enforcement, service restart handlers

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification - can be retained for testing
- `tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality and SSL protocol verification - can be retained for compliance validation
- `tests/ssh_profile.rb`: Chef InSpec compliance test for SSH root login security controls (STIG compliance) - can be retained for security validation
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script - may be deprecated if moving away from Chef infrastructure
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script - may be deprecated if moving away from Chef infrastructure
- `index.html`: Static HTML test file - can be retained as test content

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver configuration)
- **Cloud Platform**: Not specified - designed for local development/testing environments

## Migration Approach

### Key Dependencies to Address
- **apache2 (2.4.41-4ubuntu3.10)**: Already using Ansible apt module - no migration needed
- **openssl**: Already using Ansible openssl_* modules - no migration needed
- **python3-openssl**: Already specified as Ansible dependency - no migration needed
- **Chef InSpec**: Currently used for compliance testing - can be retained alongside Ansible or replaced with Ansible compliance modules

### Security Considerations
- **SSL/TLS Configuration**: Both playbooks handle SSL certificate management and protocol hardening - already properly implemented in Ansible
- **Self-signed Certificates**: Current implementation generates self-signed certificates - consider migration to proper certificate management (Let's Encrypt, internal CA)
- **SSH Security**: InSpec tests validate SSH root login restrictions - ensure Ansible playbooks include SSH hardening tasks
- **Credential Management**: No hardcoded credentials detected in playbooks - variables are properly externalized

### Technical Challenges
- **InSpec Integration**: Decision needed on whether to retain Chef InSpec for compliance testing or migrate to Ansible-native compliance solutions (ansible-lint, molecule with testinfra)
- **Test Kitchen Workflow**: Current testing workflow uses Test Kitchen with Vagrant - may need migration to Ansible-native testing tools (molecule, ansible-test)
- **Chef Infrastructure Dependencies**: Deployment scripts assume Chef Automate/Server infrastructure - these may become obsolete in pure Ansible environment

### Migration Order
1. **Retain Current Ansible Playbooks** (no migration needed - already in target format)
2. **Evaluate InSpec Compliance Tests** (decide whether to retain or migrate to Ansible-native testing)
3. **Migrate Test Infrastructure** (replace Test Kitchen with molecule or similar Ansible testing framework)
4. **Deprecate Chef Infrastructure Scripts** (if moving to pure Ansible environment)

### Assumptions
- The organization wants to maintain compliance testing capabilities currently provided by Chef InSpec
- The current Ubuntu 20.04 target platform will be retained or upgraded to a newer LTS version
- The Vagrant-based testing environment is acceptable or will be replaced with a similar local testing solution
- The Chef Automate/Server infrastructure scripts may be deprecated if the organization is moving away from Chef entirely
- The existing Ansible playbook structure and variable management approach is acceptable for the target environment
- SSL certificate management strategy (self-signed vs. proper CA) will be determined as part of broader security architecture decisions