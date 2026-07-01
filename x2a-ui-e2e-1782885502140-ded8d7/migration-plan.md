# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The primary focus is on demonstrating how Chef InSpec can be used for compliance testing alongside Ansible deployments. The migration scope is relatively small, focusing on two main Ansible playbooks and associated InSpec tests. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test profile that validates HTTPS website deployment and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that validates SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible alternatives:
  - Option 1: Use Ansible's built-in `assert` module for basic validation
  - Option 2: Integrate with Molecule for testing
  - Option 3: Convert InSpec tests to Ansible roles with test tasks

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing infrastructure
  - GitHub Actions or other CI/CD pipeline for automated testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
  - Approach: Convert the poodle_fix.yml playbook to an Ansible role with appropriate handlers

- **SSH Security**: The SSH root login check needs to be maintained
  - Approach: Convert the InSpec test to an Ansible task that validates the sshd_config

- **Self-signed Certificates**: The certificate generation process needs to be preserved
  - Approach: Maintain the openssl_* module usage in the Ansible playbook

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible validation
  - Mitigation: Create custom Ansible modules or use assert module with appropriate conditions
  - Consider implementing Ansible callback plugins for test reporting

- **Test Kitchen Replacement**: Finding an equivalent testing framework
  - Mitigation: Implement Molecule for Ansible role testing with similar functionality

- **Chef Automate Deployment**: Converting bash scripts to Ansible
  - Mitigation: Create an Ansible role for Chef server deployment if still needed, or replace with alternative configuration management monitoring

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
   - Convert to proper Ansible role structure
   - Add documentation

2. **poodle_fix.yml** (low risk, already in Ansible format)
   - Convert to proper Ansible role structure
   - Add documentation

3. **InSpec Tests** (moderate complexity)
   - Convert to Ansible assertions or Molecule tests
   - Ensure equivalent validation coverage

4. **Chef Automate Deployment Scripts** (high complexity)
   - Convert to Ansible roles if Chef infrastructure is still needed
   - Or replace with alternative monitoring/compliance solution

### Assumptions

1. The primary purpose of this repository is demonstrating Chef InSpec with Ansible rather than production deployment
2. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
3. Self-signed certificates are acceptable for the web server configuration
4. The Chef Automate and Chef Server deployment may not be needed if moving fully to Ansible
5. No external data sources or databases are required for the applications
6. No complex application dependencies exist beyond what's visible in the playbooks
7. The security compliance requirements (STIG references) in the InSpec tests must be maintained in the Ansible implementation