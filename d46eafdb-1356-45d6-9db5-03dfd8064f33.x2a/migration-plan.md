# MIGRATION FROM CHEF INSPEC TO ANSIBLE

This repository contains Chef InSpec compliance testing examples integrated with Ansible playbooks, rather than traditional Chef cookbooks. The migration scope is limited as the repository primarily demonstrates compliance automation patterns using InSpec for testing Ansible-managed infrastructure. The main migration effort involves transitioning from Chef InSpec tests to native Ansible testing approaches.

**Timeline Estimate**: 1-2 weeks
**Complexity**: Low to Medium
**Risk Level**: Low

## Module Migration Plan

This repository contains Chef InSpec compliance tests and demonstration Ansible playbooks that need migration planning:

### MODULE INVENTORY

**website-https-demo**:
- Description: Ansible playbook demonstrating HTTPS website deployment with Apache, SSL certificate generation, and virtual host configuration
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, self-signed SSL certificates via OpenSSL, virtual host configuration, SSL/TLS security hardening

**poodle-ssl-fix**:
- Description: Ansible playbook for SSL/TLS security hardening to address POODLE vulnerability by disabling SSLv3 and enforcing TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL protocol configuration, TLS 1.2 enforcement, service restart handlers

**inspec-compliance-tests**:
- Description: Chef InSpec compliance tests for HTTPS website verification and SSH security validation
- Path: chef-and-ansible/tests/
- Technology: Chef InSpec
- Key Features: Port 443 listening verification, HTTPS response validation, SSL protocol compliance checks, SSH root login security controls

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration using Vagrant driver with Ansible provisioner and InSpec verifier for compliance testing
- `index.html`: Static HTML test content for website deployment verification
- `setup-automate/deploy-chef-server.sh`: Chef Infra Server deployment script for on-premises or cloud VM installation
- `setup-automate/deploy-automate.sh`: Chef Automate and Chef Infra Server deployment script with user and organization setup

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible native testing modules (uri, assert, service_facts) or molecule with testinfra
- **Test Kitchen**: Replace with Molecule for Ansible role testing and validation
- **Chef Automate/Server**: Remove dependency as compliance testing will be handled natively in Ansible

### Security Considerations

- **SSL/TLS Configuration**: The existing Ansible playbooks already implement proper SSL hardening practices:
  - Self-signed certificate generation using OpenSSL modules
  - TLS 1.2 enforcement and SSLv3 disabling for POODLE mitigation
  - Proper certificate file permissions (0640)
- **SSH Security**: InSpec tests validate SSH root login restrictions - migrate to Ansible assert tasks
- **Secrets Management**: Current implementation uses hardcoded values in playbook variables - recommend migrating to Ansible Vault for sensitive data

### Technical Challenges

- **InSpec Test Migration**: Converting Ruby-based InSpec controls to Ansible native testing requires rewriting test logic using uri, assert, and service_facts modules
- **Compliance Reporting**: Chef InSpec provides detailed compliance reporting - need to implement equivalent reporting using Ansible callback plugins or integrate with external compliance tools
- **Test Kitchen Replacement**: Migrating from Test Kitchen to Molecule requires restructuring test scenarios and verification approaches

### Migration Order

1. **Ansible Playbooks** (already complete - no migration needed)
2. **InSpec Compliance Tests** (convert to Ansible native tests or molecule with testinfra)
3. **Test Kitchen Configuration** (replace with Molecule testing framework)
4. **Chef Server Setup Scripts** (optional - remove if Chef infrastructure is being decommissioned)

### Assumptions

- The target environment will continue using Ubuntu 20.04 LTS as specified in the current Test Kitchen configuration
- Compliance testing requirements will be met using Ansible native modules rather than external compliance frameworks
- The demonstration nature of this repository suggests it may not require full production-grade migration but rather serves as a reference implementation
- Chef Automate and Chef Infra Server deployment scripts may be retained for environments that need to maintain Chef infrastructure alongside Ansible
- SSL certificate management will continue using self-signed certificates for demonstration purposes, though production environments should integrate with proper CA or Let's Encrypt
- The existing Apache version pinning (2.4.41-4ubuntu3.10) suggests specific security requirements that should be maintained in the migrated solution