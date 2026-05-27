# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a pure Ansible solution. The repository primarily consists of:

1. A Chef InSpec testing framework used alongside Ansible playbooks for compliance automation
2. Ansible playbooks for configuring HTTPS websites and SSL security
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **MEDIUM** with an estimated timeline of 2-3 weeks. The primary focus will be on replacing Chef InSpec tests with Ansible-native testing solutions while preserving the existing Ansible playbooks and converting the Chef server deployment scripts to Ansible roles.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing of web servers
    - Path: chef-and-ansible/
    - Technology: Chef InSpec + Ansible
    - Key Features: HTTPS website deployment, SSL configuration, compliance testing

- **setup-automate**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `website_https.yml`: Ansible playbook for deploying an HTTPS website with Apache. Can be preserved with minor modifications.
- `poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be preserved with minor modifications.
- `tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Needs to be converted to Ansible testing framework.
- `tests/ssh_profile.rb`: InSpec test for SSH security compliance. Needs to be converted to Ansible testing framework.
- `deploy-automate.sh` and `deploy-chef-server.sh`: Shell scripts for deploying Chef infrastructure. Need to be converted to Ansible roles.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or GitHub Actions for pipeline automation
  - Ansible Vault for secrets management

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should preserve:
  - Self-signed certificate generation
  - TLS 1.2 enforcement (disabling older protocols)
  - Apache SSL module configuration

- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Root login restrictions
  - SSH protocol security settings
  - These tests need to be converted to Ansible assertions or Molecule tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys should be managed securely
  - Count of credentials detected: 3 (username, password, organization name in setup scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions to ensure equivalent coverage.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules
  - Consider using Molecule's verifier plugins if direct conversion is challenging

- **Chef Server Replacement**: The Chef server deployment scripts need to be replaced with equivalent Ansible functionality.
  - Mitigation: Evaluate if Chef server is actually needed or if pure Ansible can meet requirements
  - If Chef server functionality is required, consider AWX/Tower deployment via Ansible

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, only need minor adjustments
2. **InSpec Tests**: Medium complexity, convert to Ansible assertions or Molecule tests
3. **Chef Server Deployment Scripts**: High complexity, requires redesigning deployment architecture for Ansible

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment.
2. The Chef server deployment scripts are used for setting up test environments rather than production infrastructure.
3. There are no external dependencies or integrations not visible in the repository.
4. The hardcoded credentials in the setup scripts are for demonstration purposes and not used in production.
5. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
6. The migration will maintain the same level of security compliance testing currently provided by InSpec.
7. There are no custom Chef resources or complex InSpec profiles beyond what's visible in the repository.