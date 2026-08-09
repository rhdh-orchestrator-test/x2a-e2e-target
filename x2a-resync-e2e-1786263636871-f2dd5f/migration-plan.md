# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests that are used together for compliance automation. The primary technology is Ansible for configuration management with Chef InSpec for compliance testing. There are also Chef Automate and Chef Infra Server setup scripts. The migration scope is relatively small, focusing on converting the InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository contains a limited number of files with straightforward functionality

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables only TLSv1.2

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Compliance check for SSH configuration security

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS website functionality
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `setup-automate/deploy-automate.sh`: Bash script to deploy Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script to deploy Chef Infra Server without Automate

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml as the driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM setup

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - **Option 1**: Migrate to Ansible Molecule for testing
  - **Option 2**: Use pytest-ansible for Python-based testing
  - **Option 3**: Integrate with ansible-lint for static analysis

- **Test Kitchen**: Replace with:
  - Ansible Molecule for a complete testing framework
  - Or continue using Test Kitchen with Ansible provisioner (already in use)

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration and control
  - Ansible Content Collections for role and module management

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Migration should maintain:
  - Self-signed certificate generation
  - TLS 1.2 protocol enforcement (from poodle_fix.yml)
  - Proper certificate file permissions

- **SSH Security**: The InSpec test verifies SSH root login is disabled. Migration should:
  - Convert this test to an equivalent Ansible-compatible test
  - Consider adding an Ansible task to enforce this configuration

- **Vault/secrets management**:
  - No encrypted secrets were detected in the repository
  - Plain text passwords exist in the setup scripts (userpassword='password')
  - Migration should implement Ansible Vault for these credentials

### Technical Challenges

- **Testing Framework Transition**: Moving from InSpec to Ansible-native testing
  - Mitigation: Map InSpec resources to equivalent Ansible modules or testing tools
  - Example: InSpec's `describe port(443)` can be replaced with Ansible's `wait_for` module in tests

- **Compliance Reporting**: InSpec provides structured compliance reporting
  - Mitigation: Implement alternative compliance reporting with Ansible Tower/AWX or integrate with tools like OpenSCAP

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These can remain largely unchanged
2. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb): Convert to Ansible-compatible testing framework
3. **Test Kitchen Configuration**: Update or replace with Ansible Molecule
4. **Chef Automate/Server Scripts**: Replace with Ansible Tower/AWX setup

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance testing
2. The existing Ansible playbooks are functioning correctly and don't require significant changes
3. The target environment will continue to be Ubuntu 20.04 or similar
4. The deployment scripts for Chef Automate/Server are used for setting up a compliance environment, which will be replaced with an Ansible-based solution
5. No external data sources or complex inventory management is in use
6. The repository is primarily for demonstration/example purposes rather than production use (based on README content)