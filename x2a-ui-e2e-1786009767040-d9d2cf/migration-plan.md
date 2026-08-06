# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and Chef Automate/Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The repository appears to be primarily educational/demonstration in nature, showing how Chef InSpec can work alongside Ansible for compliance automation.

**Estimated Timeline**: 1-2 weeks for a complete migration, with minimal complexity due to the limited scope of the repository.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance tagging (STIG/CCI references)

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be updated to use Ansible-native testing frameworks.
- `index.html`: Simple HTML file used for testing web server functionality. Can be preserved as-is.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Molecule with Testinfra for infrastructure testing
  - Option 2: Ansible Test modules for compliance testing
  - Option 3: Convert InSpec tests to Ansible assert tasks within playbooks

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing
  - Molecule provides native Ansible testing capabilities
  - Supports multiple drivers including Vagrant

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks
  - Create roles for system requirements configuration
  - Create playbooks for installation and configuration

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL security hardening in the Apache configuration
  - Maintain TLSv1.2 requirement and disable older protocols
  - Ensure proper certificate generation and management

- **SSH Hardening**: The SSH compliance checks must be maintained
  - Convert InSpec SSH tests to equivalent Ansible assertions or Molecule/Testinfra tests
  - Preserve STIG/CCI compliance references for audit purposes

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - Count: 2 sets of credentials in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks
  - Challenge: Preserving the declarative testing style of InSpec in Ansible
  - Mitigation: Use Testinfra with Molecule which provides similar testing capabilities

- **Compliance Metadata**: Preserving compliance metadata (STIG IDs, CCI references)
  - Challenge: Ansible doesn't have native support for compliance metadata tagging
  - Mitigation: Use YAML comments or custom variables to store compliance metadata

- **Test Kitchen to Molecule**: Converting Test Kitchen workflow to Molecule
  - Challenge: Ensuring test scenarios match between platforms
  - Mitigation: Create equivalent Molecule scenarios that match the Test Kitchen configuration

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they can remain largely unchanged
2. **Test Framework** - Convert kitchen.yml to molecule.yml configuration
3. **InSpec Tests** - Convert InSpec tests to Testinfra or Ansible assertions
4. **Deployment Scripts** - Convert Chef Automate/Server deployment scripts to Ansible playbooks

### Assumptions

1. The repository is primarily for demonstration/educational purposes showing Chef InSpec with Ansible integration
2. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
3. Vagrant will continue to be used for development/testing environments
4. The security compliance requirements (STIG/CCI references) must be preserved in the migrated solution
5. The deployment scripts are intended for on-premises or cloud VM deployment
6. No external Chef cookbooks or complex Chef-specific features are in use
7. The existing Ansible playbooks can be preserved with minimal changes
8. The primary migration focus is on replacing Chef InSpec tests with Ansible-compatible testing