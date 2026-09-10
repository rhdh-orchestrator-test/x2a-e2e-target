# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains example code demonstrating Chef InSpec integration with Ansible playbooks, rather than traditional Chef cookbooks requiring migration. The primary content consists of Ansible playbooks with InSpec test verification and Chef server deployment scripts. The migration scope is minimal as the infrastructure automation is already implemented in Ansible - the focus should be on replacing Chef InSpec testing with native Ansible testing approaches.

## Module Migration Plan

This repository contains demonstration examples and deployment scripts rather than production Chef cookbooks:

### MODULE INVENTORY

**website-https-demo**:
- Description: Ansible playbook demonstrating Apache HTTPS configuration with SSL certificate generation, virtual host setup, and security hardening
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Self-signed SSL certificates via OpenSSL modules, Apache virtual host configuration, package management for Ubuntu 20.04

**poodle-security-fix**:
- Description: Ansible playbook for SSL/TLS security hardening by disabling SSLv3 and enforcing TLS 1.2 to mitigate POODLE vulnerability
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL protocol configuration, regex-based configuration file modification

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL protocol verification
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec security control for SSH root login compliance (STIG-based)
- `chef-and-ansible/index.html`: Static HTML test content for web server verification
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (explicitly specified in kitchen.yml and playbook package versions)
- **Virtual Machine Technology**: Vagrant with VirtualBox (based on Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec (latest)**: Replace with Ansible native testing using ansible-test, molecule, or testinfra
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing and verification
- **Chef Automate/Server**: Remove dependency on Chef infrastructure components for testing and compliance

### Security Considerations
- **SSL/TLS Configuration**: Current playbooks demonstrate proper SSL certificate management and protocol hardening
  - Self-signed certificate generation using Ansible OpenSSL modules
  - TLS 1.2 enforcement and SSLv3 disabling for POODLE mitigation
  - No hardcoded credentials detected in reviewed files
- **SSH Security**: InSpec tests verify SSH root login restrictions per STIG requirements
- **Compliance Testing**: Current InSpec controls follow NIST and STIG standards that need equivalent Ansible testing

### Technical Challenges
- **Testing Framework Migration**: Converting InSpec compliance tests to Ansible-native testing approaches
  - InSpec's declarative testing syntax needs translation to Ansible assert tasks or external testing tools
  - STIG compliance verification currently relies on InSpec's security-focused test library
- **Test Kitchen Replacement**: Migrating from Test Kitchen to Molecule for playbook testing
  - Kitchen.yml configuration needs conversion to molecule.yml format
  - Vagrant driver configuration requires adaptation to Molecule's driver model

### Migration Order
1. **Testing Infrastructure** (immediate priority - low risk)
   - Replace Test Kitchen with Molecule for playbook testing
   - Convert kitchen.yml to molecule.yml configuration
2. **Compliance Testing** (moderate complexity)
   - Convert InSpec tests to Ansible native assertions or integrate testinfra
   - Maintain STIG compliance verification capabilities
3. **Infrastructure Deployment** (low priority)
   - Remove Chef server deployment scripts if not needed for production environment
   - Document alternative compliance monitoring solutions

### Assumptions
- The Ansible playbooks (website_https.yml, poodle_fix.yml) are demonstration examples rather than production code requiring migration
- Chef InSpec is used solely for testing/compliance verification, not for infrastructure provisioning
- The target environment will continue using Ubuntu 20.04 or migrate to a newer LTS version
- Test Kitchen and Chef server components are not required in the target Ansible-only environment
- The organization wants to maintain the same level of security compliance testing without Chef dependencies
- SSL certificate management will continue using Ansible's OpenSSL modules rather than external certificate authorities