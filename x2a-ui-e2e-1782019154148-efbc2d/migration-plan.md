# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2 in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security of the Apache web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configurations, specifically root login restrictions
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Sample HTML file used for testing the web server. Can be preserved as-is or incorporated into Ansible templates.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but deployment scripts suggest on-premises or generic cloud VM targets

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Ansible Molecule with Goss for infrastructure testing
  - Option 3: Ansible Molecule with Ansible assertions for simpler tests

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for orchestration and control
  - Ansible Collections for compliance automation (ansible.posix, community.general)

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Approach: Convert the existing Ansible task to an Ansible role with proper documentation of security implications

- **SSH Security**: The SSH security profile tests need to be converted to Ansible-compatible tests
  - Approach: Create Ansible tasks that verify the same SSH configuration parameters

- **Credentials Management**: 
  - The Chef deployment scripts contain hardcoded credentials that should be moved to Ansible Vault
  - Count: 1 password in each deployment script

- **Certificate Management**:
  - Self-signed certificates are generated in the website_https.yml playbook
  - Approach: Preserve the OpenSSL certificate generation tasks but consider adding options for using external certificates

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to equivalent Ansible/Molecule tests
  - Mitigation: Use Testinfra with Molecule which provides a similar testing experience to InSpec

- **Compliance Metadata**: InSpec tests contain rich compliance metadata (STIG IDs, CCI references) that need to be preserved
  - Mitigation: Use Ansible documentation strings and tags to maintain compliance metadata

- **Test Kitchen to Molecule**: Converting the test orchestration from Test Kitchen to Molecule
  - Mitigation: Molecule has similar concepts and can be configured to use Vagrant as a driver

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they can remain largely unchanged
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Convert to Molecule/Testinfra tests
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - Convert to Ansible roles/playbooks
4. **Test Infrastructure** (kitchen.yml) - Replace with Molecule configuration

### Assumptions

1. The existing Ansible playbooks are functioning correctly and don't require significant modifications beyond potential best practices improvements.
2. The target environment will continue to be Ubuntu 20.04 or compatible systems.
3. The InSpec tests are currently being used for post-deployment validation rather than continuous compliance monitoring.
4. The deployment scripts are used for setting up development/test environments rather than production systems, given the hardcoded credentials.
5. There is no requirement to maintain backward compatibility with Chef InSpec after migration.
6. The migration will not include setting up a full compliance reporting system to replace Chef Automate's compliance capabilities.
7. The self-signed certificates are acceptable for the target environment rather than requiring integration with a certificate authority.
8. The current Test Kitchen setup is primarily used for development testing rather than CI/CD pipelines.