# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains example code demonstrating Chef InSpec integration with Ansible playbooks for compliance automation. The migration scope is minimal as the core infrastructure automation is already implemented in Ansible. The primary migration task involves replacing Chef InSpec testing with native Ansible testing approaches while preserving the compliance validation capabilities.

## Module Migration Plan

This repository contains Ansible playbooks with Chef InSpec testing integration that requires migration to pure Ansible testing approaches:

### MODULE INVENTORY

**website-https-deployment**:
- Description: Apache web server deployment with HTTPS configuration, SSL certificate generation, and virtual host setup for a "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Self-signed SSL certificate generation, Apache virtual host configuration, package management, service handlers

**ssl-security-hardening**:
- Description: SSL/TLS security hardening playbook that disables vulnerable SSL protocols and enforces TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL protocol configuration, POODLE vulnerability mitigation, service restart handlers

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec security compliance test for SSH root login restrictions
- `chef-and-ansible/index.html`: Static HTML test file for web server validation
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec (latest)**: Replace with Ansible native testing modules (uri, assert, service_facts)
- **Test Kitchen**: Replace with molecule for Ansible testing framework
- **Vagrant**: Can be retained or replaced with container-based testing

### Security Considerations
- **SSL Certificate Management**: Current implementation uses self-signed certificates generated via openssl_* modules - consider integration with Let's Encrypt or proper CA for production
- **SSH Security Validation**: InSpec test validates SSH root login restrictions - migrate to Ansible assert module with service_facts
- **SSL Protocol Enforcement**: Existing Ansible playbook correctly disables SSL 3.0 and enforces TLS 1.2 - no migration needed
- **Vault/secrets management**: No encrypted credentials detected - hardcoded test values in deployment scripts need to be parameterized

### Technical Challenges
- **InSpec Test Migration**: Converting Ruby-based InSpec tests to Ansible native testing requires rewriting test logic using uri, assert, and service_facts modules
- **Test Framework Replacement**: Migrating from Test Kitchen to Molecule requires restructuring test configuration and execution workflow
- **Compliance Validation**: Ensuring migrated Ansible tests maintain the same security compliance validation coverage as original InSpec tests

### Migration Order
1. **website-https-deployment** (already complete - pure Ansible playbook)
2. **ssl-security-hardening** (already complete - pure Ansible playbook)
3. **InSpec test migration** (convert Ruby tests to Ansible native testing)
4. **Test framework migration** (replace Test Kitchen with Molecule)

### Assumptions
- The repository serves as an example/demo rather than production infrastructure code
- Target environment is development/testing focused rather than production deployment
- Current Ansible playbooks are considered the desired end state for infrastructure automation
- Chef InSpec is only used for compliance testing, not infrastructure provisioning
- The Chef Automate/Server deployment scripts are for setting up the testing environment rather than production Chef infrastructure
- SSL certificate requirements are for testing purposes only (self-signed certificates acceptable)
- No external Chef cookbooks or complex dependency chains need migration since this is a testing/example repository
- The existing Ansible playbooks follow current best practices and don't require refactoring beyond test integration