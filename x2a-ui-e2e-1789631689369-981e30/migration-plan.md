# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains educational examples demonstrating Chef InSpec integration with Ansible playbooks rather than traditional Chef cookbooks requiring migration. The content is already primarily Ansible-based with InSpec used for compliance testing. Migration complexity is minimal as the core automation is already in Ansible format.

## Module Migration Plan

This repository contains demonstration examples that showcase Chef InSpec compliance testing alongside Ansible automation:

### MODULE INVENTORY

**website-https-deployment**:
- Description: Apache web server deployment with HTTPS/SSL configuration, self-signed certificate generation, and virtual host setup for a "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (with InSpec testing)
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL/TLS setup

**poodle-vulnerability-fix**:
- Description: SSL/TLS security hardening to address POODLE vulnerability by disabling SSLv3 and enforcing TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (with InSpec testing)
- Key Features: Apache SSL protocol configuration, TLS 1.2 enforcement, security compliance

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification on Ubuntu 20.04
- `tests/website_https_verify.rb`: InSpec compliance tests verifying HTTPS functionality, SSL protocols, and web service availability
- `tests/ssh_profile.rb`: InSpec security profile testing SSH root login restrictions (STIG compliance)
- `index.html`: Static HTML test page for web server validation
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script for demonstration environment
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (as specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with native Ansible testing modules (ansible.builtin.uri, ansible.builtin.service_facts) or external testing frameworks like Molecule with Testinfra
- **Test Kitchen**: Replace with Ansible Molecule for testing and validation workflows
- **Chef Automate/Server**: Remove dependency as these are only used for demonstration purposes

### Security Considerations
- **SSL/TLS Configuration**: Current playbooks already implement proper SSL hardening practices
  - Self-signed certificate generation using OpenSSL modules
  - TLS 1.2 enforcement and SSLv3 disabling
  - Proper file permissions on certificate files (0640)
- **SSH Security**: InSpec tests verify SSH root login restrictions
- **Credential Management**: No hardcoded credentials detected in the reviewed files
- **Certificate Management**: Uses Ansible's openssl_* modules for certificate lifecycle

### Technical Challenges
- **Testing Framework Migration**: Converting InSpec compliance tests to Ansible-native testing approaches
  - InSpec's rich compliance testing DSL needs mapping to Ansible testing modules
  - STIG compliance checks may require custom Ansible modules or external tools
- **Test Kitchen Replacement**: Migrating from Test Kitchen to Molecule for testing workflows
  - Kitchen's multi-platform testing capabilities need replication in Molecule
  - Vagrant integration patterns need adaptation

### Migration Order
1. **Testing Framework Assessment** (immediate priority - evaluate Ansible testing alternatives)
2. **Playbook Validation** (low complexity - playbooks are already Ansible-native)
3. **Documentation Update** (moderate effort - update examples to pure Ansible approach)

### Assumptions
- The primary goal is educational content migration rather than production infrastructure migration
- InSpec compliance testing capabilities need to be preserved in the target Ansible-only environment
- Test Kitchen workflows are essential and need equivalent functionality in the target state
- The demonstration environment setup scripts (Chef Automate/Server deployment) may be removed if not needed for the educational content
- Ubuntu 20.04 target platform will be maintained in the migrated examples
- Self-signed certificate approach is acceptable for demonstration purposes and doesn't require CA integration