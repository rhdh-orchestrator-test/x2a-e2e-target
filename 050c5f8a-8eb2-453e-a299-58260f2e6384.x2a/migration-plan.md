# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on compliance automation and Chef server deployment. The migration scope is relatively small, with the primary focus being on converting Chef InSpec tests to Ansible-compatible testing frameworks and adapting Chef server deployment scripts to Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Chef server deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **Chef InSpec Tests**:
    - Description: InSpec tests for validating HTTPS website configuration and SSH security settings
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS validation, SSL protocol verification, SSH configuration compliance checks

- **Chef Automate/Server Deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts with Chef server commands
    - Key Features: User creation, organization setup, server configuration

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook for setting up an HTTPS website with Apache - already in Ansible format, can be reused
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities - already in Ansible format, can be reused
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing - needs conversion to Ansible-native testing framework
- `chef-and-ansible/index.html`: Sample HTML file for website testing - can be reused as-is
- `setup-automate/deploy-automate.sh`: Bash script for Chef Automate deployment - needs conversion to Ansible playbook
- `setup-automate/deploy-chef-server.sh`: Bash script for Chef Infra Server deployment - needs conversion to Ansible playbook

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml configuration)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for infrastructure testing
  - Option 2: Use ansible-lint for static analysis
  - Option 3: Integrate with pytest-ansible for Python-based testing
  - Option 4: Continue using InSpec with Ansible by installing InSpec separately

- **Chef Server CLI**: Replace with Ansible modules for configuration management:
  - Use Ansible's built-in modules for user management, file operations, and service configuration

### Security Considerations

- **SSL Configuration**: The repository includes SSL hardening (disabling SSLv3, enabling TLSv1.2) that must be preserved in the Ansible migration
  - Migration approach: Use Ansible's `lineinfile` or `template` modules to manage SSL configuration

- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Create equivalent Ansible tasks to enforce SSH security settings and verify compliance

- **Self-signed Certificates**: The current implementation generates self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules (already used in existing playbooks)

- **Hardcoded Credentials**: The deployment scripts contain hardcoded usernames and passwords
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Compliance Testing Framework**: Converting InSpec tests to an Ansible-compatible testing framework
  - Mitigation: Consider using Molecule with testinfra or maintaining InSpec as a separate tool called from Ansible

- **Chef Server Deployment**: Replacing Chef server deployment scripts with equivalent Ansible functionality
  - Mitigation: Create Ansible roles for server deployment with appropriate variable substitution

### Migration Order

1. **Existing Ansible Playbooks** (Low risk): Review and optimize existing Ansible playbooks (website_https.yml, poodle_fix.yml)
2. **InSpec Tests** (Moderate complexity): Convert InSpec tests to Ansible-compatible testing framework
3. **Chef Server Deployment Scripts** (High complexity): Convert bash scripts to Ansible playbooks with proper variable management and security

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, based on the README description
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are already functioning correctly and don't require significant changes
3. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
4. The hardcoded credentials in deployment scripts are for demonstration purposes only and will be replaced with secure alternatives
5. The team has expertise in both Chef and Ansible, allowing for a smooth transition
6. The InSpec tests are critical for compliance validation and must be preserved in functionality if not in exact form
7. The repository doesn't contain actual Chef cookbooks, only InSpec tests and deployment scripts
8. Test Kitchen integration will need to be replaced with an Ansible-native testing approach