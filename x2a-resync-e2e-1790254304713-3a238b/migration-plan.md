# MIGRATION FROM MIXED ANSIBLE/CHEF INSPEC TO ANSIBLE

This repository is a demonstration/example repository that showcases using Chef InSpec alongside Ansible for compliance automation. It contains existing Ansible playbooks with Chef InSpec tests and Chef server deployment scripts. The migration scope is minimal as the primary automation is already in Ansible format, requiring only standardization and InSpec test conversion.

## Module Migration Plan

This repository contains mixed technologies with Ansible playbooks already present and Chef InSpec tests that need conversion:

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

**chef-automate-deployment**:
- Description: Bash script for deploying Chef Automate and Chef Infra Server with user and organization setup
- Path: setup-automate/deploy-automate.sh
- Technology: Bash script
- Key Features: Hostname configuration, system tuning, Chef Automate CLI deployment, user/org creation

**chef-server-deployment**:
- Description: Bash script for deploying standalone Chef Infra Server without Automate components
- Path: setup-automate/deploy-chef-server.sh
- Technology: Bash script
- Key Features: Hostname configuration, system tuning, Chef server deployment, user/org creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS functionality and SSL protocol validation
- `tests/ssh_profile.rb`: Chef InSpec security control for SSH root login verification (STIG compliance)
- `index.html`: Static HTML test file for web server validation
- `README.md`: Documentation explaining the Chef InSpec and Ansible integration approach

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace InSpec tests with Ansible native testing modules (ansible.builtin.uri, ansible.builtin.service_facts)
- **Test Kitchen**: Replace with Molecule for Ansible testing framework
- **Chef Automate/Server**: Evaluate need for centralized configuration management - may replace with Ansible Tower/AWX or maintain as compliance scanning tool

### Security Considerations
- **SSL/TLS Configuration**: Current playbooks use self-signed certificates - consider integration with Let's Encrypt or corporate PKI
- **Hardcoded Credentials**: Chef server deployment scripts contain plaintext passwords in variables - migrate to Ansible Vault
- **SSH Security**: InSpec tests verify SSH hardening - convert to Ansible assert tasks or maintain InSpec for compliance reporting
- **STIG Compliance**: SSH root login control (V-38607) needs conversion from InSpec to Ansible validation

### Technical Challenges
- **InSpec Test Conversion**: Converting Chef InSpec compliance tests to Ansible native assertions while maintaining STIG compliance validation
- **Test Framework Migration**: Replacing Test Kitchen workflow with Molecule for Ansible-native testing
- **Compliance Reporting**: Determining strategy for compliance reporting without Chef InSpec (consider Ansible compliance collections)
- **Chef Server Dependencies**: Evaluating whether Chef Automate/Server deployment is still needed in pure Ansible environment

### Migration Order
1. **Standardize Existing Playbooks** (Low risk, immediate value) - website_https.yml and poodle_fix.yml already functional
2. **Convert Bash Deployment Scripts** (Moderate complexity) - Transform Chef server deployment scripts to Ansible playbooks
3. **Replace InSpec Tests** (High complexity) - Convert compliance tests to Ansible native testing or maintain hybrid approach

### Assumptions
- The repository serves as a demonstration/example rather than production infrastructure code
- Ubuntu 20.04 target environment may need updating to more recent LTS version
- Chef InSpec may be retained for compliance scanning even in Ansible-native environment
- Test Kitchen configuration suggests development/testing workflow that needs Molecule replacement
- Chef server deployment may be unnecessary if migrating to pure Ansible automation
- Self-signed certificates are acceptable for demonstration purposes but production deployment would require proper PKI integration
- Current Ansible playbooks follow older syntax patterns that may benefit from modernization to current best practices