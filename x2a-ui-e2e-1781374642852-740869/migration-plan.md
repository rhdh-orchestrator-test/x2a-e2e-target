# MIGRATION FROM CHEF AND BASH TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests, Ansible playbooks, and Bash scripts for deploying Chef infrastructure. The migration scope is relatively small, focusing on two main components:

1. Chef InSpec tests used alongside Ansible for compliance automation
2. Bash scripts for Chef Automate and Chef Infra Server deployment

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a single developer. The primary focus will be on converting InSpec tests to Ansible-native solutions and transforming the Chef server deployment scripts into Ansible playbooks.

## Module Migration Plan

This repository contains Chef InSpec tests and Bash scripts that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing of web servers
    - Path: chef-and-ansible/
    - Technology: Chef InSpec + Ansible
    - Key Features: HTTPS website deployment, SSL/TLS compliance testing, SSH security compliance testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash
    - Key Features: Chef server installation, user creation, organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible and InSpec integration. Will need to be replaced with Ansible-native testing framework like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure web server. Can be retained and integrated into the new Ansible structure.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Can be retained and integrated into the new Ansible structure.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Will need to be converted to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Will need to be converted to Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - For basic compliance checks: Use Ansible's `assert` module
  - For more complex compliance: Use `ansible-lint` or integrate with tools like OpenSCAP
  - For continuous compliance: Consider AWX/Ansible Tower with scheduled jobs

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality for testing Ansible roles
  - Supports multiple drivers including Vagrant

- **Chef Automate/Infra Server**: Determine if these are still needed or can be replaced with:
  - AWX/Ansible Tower for web UI and job scheduling
  - Git repositories for configuration management
  - CI/CD pipelines for automated deployments

### Security Considerations

- **SSL/TLS Configuration**: The current setup enforces TLSv1.2 and disables SSLv3 (POODLE vulnerability fix)
  - Migration approach: Maintain these security settings in Ansible playbooks
  - Consider updating to also include TLSv1.3 support

- **SSH Security**: InSpec tests verify SSH root login is disabled
  - Migration approach: Convert to Ansible assertions or use ansible-lint rules
  - Add additional SSH hardening measures in the Ansible playbooks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing
  - Mitigation: Use Ansible's assert module for basic tests, consider community modules for more complex tests
  - For HTTP/HTTPS and port testing, use the `uri` and `wait_for` modules

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible
  - Mitigation: If Chef server is still needed, create Ansible roles for deployment
  - If not needed, document the migration path to pure Ansible infrastructure

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Integrate existing `website_https.yml` and `poodle_fix.yml` into the new structure
   - Add Ansible Vault for any sensitive data

2. **InSpec Tests** (Medium complexity)
   - Convert `website_https_verify.rb` and `ssh_profile.rb` to Ansible assertions
   - Set up Molecule for testing

3. **Chef Server Deployment** (High complexity)
   - Convert deployment scripts to Ansible playbooks
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being production infrastructure code.
2. The Chef server deployment scripts are examples and not actively used in production.
3. There are no additional Chef cookbooks or resources not visible in the repository structure.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. There is no requirement to maintain backward compatibility with Chef InSpec after migration.
6. The hardcoded credentials in the deployment scripts are examples and not actual production credentials.
7. The migration will focus on functionality rather than maintaining the exact structure of the original repository.