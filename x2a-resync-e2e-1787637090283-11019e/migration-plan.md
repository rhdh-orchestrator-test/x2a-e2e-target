# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks that deploy a secure web server
3. Integrating Chef InSpec tests into an Ansible-native testing framework

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the small codebase.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration, including self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server on a VM
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server (without Automate) on a VM
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-test framework with custom modules
  - Option 2: Integrate with Molecule for testing
  - Option 3: Maintain InSpec as a separate testing tool called from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/collection testing
  - AWX/Tower for workflow testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Approach: Convert to an Ansible role with appropriate templates and handlers
  - Ensure TLS 1.2+ is enforced and older protocols are disabled

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled
  - Approach: Create an Ansible role for SSH hardening that implements the same controls
  - Include idempotent tasks to verify and remediate SSH configuration

- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates
  - Approach: Create an Ansible role for certificate management
  - Consider integrating with HashiCorp Vault or other secret management solutions

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible
  - Challenge: Ensuring proper system requirements and configuration
  - Mitigation: Create an Ansible role that handles prerequisites, downloads, and configuration

- **Testing Framework**: Replacing InSpec tests with Ansible-native testing
  - Challenge: Maintaining the same level of compliance verification
  - Mitigation: Use Ansible assert modules or integrate with a compliance tool like OpenSCAP

### Migration Order

1. **website-https and poodle-fix playbooks** (low risk, already Ansible)
   - Convert to proper Ansible roles with variables, templates, and handlers
   - Implement idempotency improvements
   - Add documentation

2. **InSpec Tests** (moderate complexity)
   - Convert to Ansible-native testing framework
   - Ensure all compliance checks are maintained
   - Integrate with CI/CD pipeline

3. **Chef Automate and Server Deployment Scripts** (high complexity)
   - Create Ansible roles for Chef server deployment
   - Implement variable substitution and Ansible Vault for credentials
   - Add proper error handling and idempotency

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment
2. The InSpec tests are essential and need to be maintained in some form
3. The Chef Automate deployment is still needed (rather than being replaced entirely)
4. No external dependencies or integrations beyond what's visible in the repository
5. No complex data migration is required
6. The target environment will continue to be Ubuntu 20.04 or compatible
7. The deployment will continue to use self-signed certificates rather than proper CA-signed certificates