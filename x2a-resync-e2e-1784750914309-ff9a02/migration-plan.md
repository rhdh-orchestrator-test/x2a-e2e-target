# MIGRATION FROM ANSIBLE AND CHEF INSPEC TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance validation alongside Ansible for configuration management. The migration scope is relatively small, focusing on:

1. Preserving the existing Ansible playbooks (website_https.yml and poodle_fix.yml)
2. Converting Chef InSpec tests to Ansible-compatible testing frameworks
3. Replacing Chef Automate/Chef Server deployment scripts with Ansible equivalents

Given the limited scope (2 Ansible playbooks, 2 InSpec tests, 2 deployment scripts), this migration is estimated to be a low-complexity effort that could be completed within 1-2 weeks by a single engineer familiar with both Chef InSpec and Ansible.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS using a self-signed certificate
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS configuration and SSL security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec test that validates SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, STIG compliance check

- **deploy-automate**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **deploy-chef-server**:
    - Description: Bash script that deploys Chef Infra Server (without Automate)
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec validation
- `chef-and-ansible/index.html`: Sample HTML file used in the examples
- `README.md`: Repository overview and documentation

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Convert InSpec tests to Ansible Molecule with Testinfra
  - Option 2: Use ansible-test framework
  - Option 3: Integrate with pytest-ansible for more complex testing scenarios

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing Ansible roles and playbooks
  - GitHub Actions or other CI/CD pipeline for automated testing

- **Chef Automate/Server**: Replace deployment scripts with:
  - Ansible playbooks for infrastructure deployment
  - Consider migrating to Ansible Tower/AWX for enterprise features

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in poodle_fix.yml
  - Ensure TLSv1.2 is enforced
  - Disable vulnerable SSL protocols
  - Maintain self-signed certificate generation

- **SSH Hardening**: Preserve the SSH security controls validated by ssh_profile.rb
  - Ensure root login remains disabled
  - Consider expanding SSH hardening based on CIS benchmarks

- **Vault/secrets management**:
  - Current repository has hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh
  - Migrate these to Ansible Vault for secure credential storage
  - Identified credentials: 1 username/password pair in each deployment script

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks
  - Challenge: InSpec has domain-specific language for compliance testing
  - Mitigation: Use Ansible Molecule with Testinfra or pytest-ansible for similar functionality

- **Deployment Script Conversion**: Converting Bash deployment scripts to idempotent Ansible playbooks
  - Challenge: Ensuring proper error handling and idempotence
  - Mitigation: Use Ansible's package, command, and service modules with appropriate state checking

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml)
   - Low risk: Keep as-is with minor improvements for idempotence and security
   - Add documentation and variable parameterization

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb)
   - Medium complexity: Convert to Ansible Molecule tests
   - Ensure all compliance checks are preserved

3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh)
   - Higher complexity: Convert to Ansible playbooks
   - Implement Ansible Vault for credential management

### Assumptions

1. The primary goal is to standardize on Ansible for both configuration management and testing
2. The existing Ansible playbooks are functional and should be preserved with minimal changes
3. Chef InSpec tests need to be converted to Ansible-compatible testing frameworks
4. The deployment scripts for Chef Automate/Server will be replaced with Ansible equivalents
5. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs
6. No external dependencies or integrations beyond what's visible in the repository
7. The migration will maintain the same level of security validation currently provided by InSpec