# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating compliance automation. The primary content consists of Ansible playbooks for configuring web servers with HTTPS support and security hardening, along with Chef InSpec tests for validation. There are also Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to convert to pure Ansible solutions.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium
**Primary Focus**: Converting InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS configuration and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec profile that validates SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `index.html`: Simple HTML file used for testing the web server configuration.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic validation
  - Option 2: Implement Molecule for Ansible role testing
  - Option 3: Use pytest-ansible for more complex test scenarios

- **Test Kitchen**: Replace with Molecule for Ansible role testing, which provides similar functionality but is designed specifically for Ansible

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that can:
  - Option 1: Deploy alternative compliance automation solution like Ansible Automation Platform
  - Option 2: Create playbooks that implement the compliance checks directly

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. This security hardening should be preserved in the migrated solution.
  - Migration approach: Maintain the same security configurations in the Ansible roles

- **SSH Hardening**: The InSpec tests validate SSH security configurations like disabling root login.
  - Migration approach: Create Ansible roles that implement the same security controls and include validation tasks

- **Self-signed Certificates**: The current solution generates self-signed certificates for HTTPS.
  - Migration approach: Use Ansible's `openssl_*` modules (already in use) but consider adding support for Let's Encrypt for production environments

- **Vault/secrets management**: 
  - Hardcoded credentials in the Chef deployment scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Test Conversion**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions.
  - Mitigation: Create a test mapping document that shows the equivalence between InSpec tests and Ansible assertions

- **Compliance Reporting**: InSpec provides rich compliance reporting that may not be directly available in Ansible.
  - Mitigation: Consider integrating with Ansible Automation Platform for compliance reporting or implement custom reporting solutions

- **Deployment Scripts**: The Chef deployment scripts contain specific configurations that need to be preserved.
  - Mitigation: Create equivalent Ansible roles for deploying alternative compliance automation solutions

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (low risk, already Ansible)
   - Convert to Ansible roles for better organization
   - Add documentation and variable customization

2. **InSpec Tests** (moderate complexity)
   - Convert to Ansible assertions or Molecule tests
   - Ensure equivalent coverage of compliance checks

3. **Chef Deployment Scripts** (high complexity)
   - Create Ansible playbooks for deploying alternative compliance solutions
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is to demonstrate compliance automation using Chef InSpec with Ansible playbooks.
2. The target environment is Ubuntu 20.04 running on Vagrant VMs.
3. The security configurations (TLS 1.2, SSH hardening) are requirements that must be preserved.
4. The Chef Automate and Chef Infra Server deployment scripts are used for setting up a compliance automation environment.
5. There are no external dependencies or integrations beyond what's visible in the repository.
6. The migration goal is to create a pure Ansible solution that provides equivalent functionality and compliance validation.
7. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) can be preserved with minimal changes.