# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks used for compliance automation and Chef Automate/Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on:

1. Ansible playbooks that configure web servers with HTTPS
2. Chef InSpec tests for compliance validation
3. Shell scripts for Chef Automate and Chef Infra Server deployment

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The main focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure automation.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **website-https-verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh-profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, CCI compliance validation

- **chef-automate-deploy**:
    - Description: Shell script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Shell script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec
- `index.html`: Sample HTML file for web server testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Convert InSpec tests to Ansible assert modules
  - Option 2: Use ansible-lint for static analysis
  - Option 3: Keep InSpec as a testing tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Option 1: molecule for Ansible role testing
  - Option 2: ansible-test for collection testing

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: AWX/Ansible Tower for centralized automation
  - Option 2: GitLab CI/CD with Ansible for pipeline-based automation

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Migration approach: Convert to Ansible role with appropriate templates and handlers

- **SSH Hardening**: The SSH compliance checks must be maintained
  - Migration approach: Convert InSpec tests to Ansible assert modules or maintain as separate compliance tests

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions may require additional modules or custom scripts
  - Mitigation: Use the ansible.builtin.assert module with appropriate conditions or maintain InSpec as a separate testing tool

- **Chef Automate Replacement**: Finding equivalent functionality in Ansible ecosystem
  - Mitigation: AWX/Tower provides similar functionality for centralized automation management

### Migration Order

1. **website-https.yml** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to a proper Ansible role structure

2. **poodle-fix.yml** (low risk, already Ansible)
   - Integrate with the website-https role
   - Ensure idempotency and proper testing

3. **InSpec Tests** (moderate complexity)
   - Decide on testing strategy (convert to Ansible or keep InSpec)
   - Implement chosen approach

4. **Chef Deployment Scripts** (high complexity)
   - Create Ansible playbooks to replace the shell scripts
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary goal is to standardize on Ansible for all automation tasks
2. InSpec tests may be retained for compliance validation if they provide value
3. The Chef Automate and Chef Infra Server deployment is part of the migration scope
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
5. The migration will maintain or improve the security posture of the current implementation
6. No external dependencies or integrations beyond what's visible in the repository
7. Test Kitchen is used only for development/testing and not in production