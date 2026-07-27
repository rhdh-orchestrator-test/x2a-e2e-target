# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks
3. Integrating Chef InSpec tests into an Ansible-native testing framework

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the small codebase.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on any cloud or on-premises VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-test with custom Python test modules
  - Option 2: Integrate with Molecule for testing
  - Option 3: Maintain InSpec as a separate tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role/playbook testing
  - Option 2: Custom Ansible playbook for test environment provisioning

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration must preserve:
  - Self-signed certificate generation
  - TLS 1.2 enforcement (POODLE vulnerability mitigation)
  - Proper file permissions for certificates (mode 0640)

- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Root login restrictions
  - SSH protocol security settings

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Recommend migrating to Ansible Vault for secure credential storage

### Technical Challenges

- **Chef InSpec Tests**: Converting InSpec tests to equivalent Ansible verification methods:
  - Challenge: InSpec has a domain-specific language for compliance testing
  - Mitigation: Use Ansible assert modules or custom Python scripts for verification

- **Chef Automate Deployment**: Converting bash scripts to idempotent Ansible playbooks:
  - Challenge: Ensuring proper sequencing and error handling
  - Mitigation: Use Ansible's package management, command modules with creates/removes conditions

### Migration Order

1. **Existing Ansible Playbooks** (Low risk, already in Ansible format)
   - Verify and optimize existing website_https.yml and poodle_fix.yml playbooks
   - Update to use current Ansible best practices

2. **Chef Automate Deployment Scripts** (Medium complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement proper idempotence and error handling
   - Secure credentials with Ansible Vault

3. **Testing Framework** (High complexity)
   - Develop Ansible-native testing approach
   - Convert InSpec tests to equivalent Ansible verification

### Assumptions

1. The repository is primarily used for demonstration/examples rather than production deployment
2. The Chef InSpec tests are valuable and should be preserved in some form
3. The hardcoded credentials in the setup scripts are for demonstration purposes only
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The existing Ansible playbooks are functioning correctly and don't require significant modification
6. No external dependencies or integrations beyond what's visible in the repository