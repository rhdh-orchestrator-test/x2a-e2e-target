# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains example code demonstrating Chef InSpec integration with Ansible for compliance automation. The repository is already primarily Ansible-based with InSpec used for compliance testing. This represents a **documentation and testing framework migration** rather than a traditional infrastructure-as-code migration, with minimal complexity and a short timeline estimate of 1-2 weeks.

## Module Migration Plan

This repository contains Ansible playbooks with Chef InSpec compliance tests that need migration planning:

### MODULE INVENTORY

**website-https-deployment**:
- Description: Apache web server deployment with HTTPS/SSL configuration, self-signed certificate generation, and virtual host setup for a "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL/TLS setup

**poodle-ssl-fix**:
- Description: SSL security hardening playbook that disables SSLv3 and enforces TLS 1.2 to mitigate POODLE vulnerability
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL protocol configuration, security compliance remediation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with Ansible provisioner and InSpec verifier
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality, SSL protocol validation, and web service verification
- `tests/ssh_profile.rb`: InSpec security compliance test for SSH root login restrictions (STIG compliance)
- `index.html`: Static HTML test file for web server validation
- `setup-automate/deploy-automate.sh`: Chef Automate and Chef Infra Server deployment script for testing infrastructure
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with Ansible compliance testing using ansible-lint, molecule, or native Ansible testing modules
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing and validation
- **Chef Automate/Server**: Remove dependency on Chef infrastructure components for testing

### Security Considerations
- **SSL/TLS Configuration**: Current playbooks implement proper SSL hardening (TLS 1.2 enforcement, SSLv3 disabling)
- **Certificate Management**: Self-signed certificates used for testing - production migration should integrate with proper CA or certificate management
- **SSH Security**: InSpec tests validate SSH root login restrictions per STIG requirements
- **Vault/Secrets Management**: No encrypted secrets detected in current configuration - all variables are plaintext in playbooks

### Technical Challenges
- **InSpec Test Migration**: Converting Ruby-based InSpec tests to Ansible native testing requires rewriting test logic in YAML/Jinja2
- **Test Kitchen Replacement**: Migrating from Test Kitchen to Molecule requires restructuring test scenarios and verification methods
- **Compliance Framework**: Maintaining STIG compliance validation without InSpec requires implementing equivalent Ansible-based compliance checks

### Migration Order
1. **InSpec Test Conversion** (low risk, high value) - Convert Ruby InSpec tests to Ansible native testing modules
2. **Test Kitchen to Molecule Migration** (moderate complexity) - Restructure testing framework to use Molecule instead of Test Kitchen
3. **Chef Infrastructure Removal** (low complexity) - Remove Chef Automate/Server deployment scripts and dependencies

### Assumptions
- The repository serves as example/demonstration code rather than production infrastructure
- Current Ansible playbooks are already functional and don't require significant modification
- InSpec compliance tests need to be converted to Ansible-native testing approaches
- Test Kitchen integration can be replaced with Molecule for consistent testing workflows
- Chef Automate/Server components are only used for testing and can be removed from the migration scope
- Ubuntu 20.04 target platform will remain consistent in the migrated environment
- Self-signed certificates are acceptable for testing scenarios in the target environment