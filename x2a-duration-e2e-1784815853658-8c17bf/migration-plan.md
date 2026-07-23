# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for demonstrating compliance automation. The repository appears to be primarily educational in nature, showing how Chef InSpec can be used alongside Ansible for compliance testing. The migration scope is relatively small, focusing on:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks to fully migrate all components to pure Ansible solutions. The main challenge will be replacing Chef InSpec tests with equivalent Ansible-native testing solutions.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Will need to be converted to Ansible-compatible test format.
- `tests/ssh_profile.rb`: InSpec compliance profile for SSH security settings. Will need to be converted to Ansible-compatible test format.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Simple Vagrant or Docker-based testing scripts

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Option 1: Ansible playbooks for deploying alternative compliance platforms
  - Option 2: Ansible AWX/Tower for centralized management

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ is enforced (already implemented in poodle_fix.yml)
  - Consider adding more modern cipher suites
  - Add HSTS headers

- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions. Migration should:
  - Implement equivalent SSH hardening in Ansible
  - Ensure compliance with referenced security standards (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **Testing Framework**: Replacing InSpec tests with equivalent Ansible testing capabilities:
  - Challenge: InSpec provides rich, declarative testing syntax
  - Mitigation: Use combination of Ansible assert module and Molecule for testing

- **Compliance Reporting**: InSpec provides built-in compliance reporting:
  - Challenge: Replicating compliance reporting capabilities in Ansible
  - Mitigation: Integrate with tools like Ansible AWX/Tower for reporting or use community modules

### Migration Order

1. **website-https playbook** (low risk, already in Ansible)
   - Review and optimize existing Ansible code
   - Add idempotency improvements if needed

2. **poodle-fix playbook** (low risk, already in Ansible)
   - Review and optimize existing Ansible code
   - Consider merging with website-https as a role

3. **InSpec Tests** (moderate complexity)
   - Convert to Ansible assert statements or Molecule tests
   - Ensure equivalent coverage for compliance checks

4. **Chef Deployment Scripts** (high complexity)
   - Replace with Ansible playbooks for alternative compliance platforms
   - Or create Ansible playbooks to deploy Chef if it must be maintained

### Assumptions

1. The repository is primarily educational/demonstrative and not a production system
2. The InSpec tests are used for verification only and not part of a larger compliance framework
3. The deployment scripts are examples and not used for critical infrastructure
4. There is no requirement to maintain backward compatibility with Chef
5. The target environment will continue to be Ubuntu-based systems
6. The self-signed certificates are for testing only and not production use