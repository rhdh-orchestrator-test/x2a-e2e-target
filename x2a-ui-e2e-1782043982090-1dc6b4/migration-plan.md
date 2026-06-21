# MIGRATION FROM CHEF AND BASH TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together for compliance automation, along with Bash scripts for Chef Automate and Chef Infra Server deployment. The migration scope is relatively small, with a focus on:

1. Preserving the existing Ansible playbooks
2. Converting Chef InSpec tests to Ansible-compatible testing frameworks
3. Converting Bash deployment scripts to Ansible playbooks

**Estimated Timeline**: 1-2 weeks for a single developer, with minimal complexity due to the small codebase and limited dependencies.

## Module Migration Plan

This repository contains Chef InSpec tests, Ansible playbooks, and Bash scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used for testing web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the ansible-lint tool for static analysis
  - Option 4: Consider maintaining InSpec as a separate tool called from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or maintain Test Kitchen with the kitchen-ansible plugin

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain proper certificate generation and management

- **SSH Hardening**: The SSH security controls tested by ssh_profile.rb must be implemented in Ansible
  - Ensure PermitRootLogin is properly configured
  - Maintain compliance with security standards (STIG)

- **Vault/secrets management**:
  - Hardcoded credentials in the Bash scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets (username/password) in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks
  - Challenge: InSpec has specific testing capabilities for SSL/TLS that may not have direct equivalents
  - Mitigation: May need to use custom Ansible modules or shell commands with assert

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible
  - Challenge: Ensuring idempotent installation and configuration
  - Mitigation: Use Ansible's package and command modules with appropriate conditionals

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml)
   - Low risk: These are already in Ansible format and only need review/optimization
   - Action: Review, optimize, and ensure they follow Ansible best practices

2. **Bash Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh)
   - Medium risk: Convert to Ansible playbooks with proper variable management
   - Action: Create Ansible roles for Chef server and Automate deployment

3. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb)
   - High risk: Requires conversion to a different testing framework
   - Action: Implement equivalent tests using Ansible's testing capabilities

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't need functional changes
2. The Test Kitchen setup is primarily used for testing and can be replaced with Ansible-native testing tools
3. The deployment scripts are used in a controlled environment where the hardcoded credentials are acceptable (though this should be changed)
4. The InSpec tests are used for compliance validation and their functionality needs to be preserved in the Ansible migration
5. The target environment will continue to be Ubuntu 20.04 or compatible systems
6. There are no external dependencies or integrations not visible in the provided files