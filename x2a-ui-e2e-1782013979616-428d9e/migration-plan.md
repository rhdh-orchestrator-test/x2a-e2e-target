# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing profiles and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, as most of the configuration is already in Ansible format. The main migration effort will involve replacing Chef InSpec tests with Ansible-native testing solutions.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration security check with STIG compliance metadata

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used for testing web server configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use ansible-test framework
  - Option 3: Implement tests using the Ansible assert module within playbooks

- **Test Kitchen**: Replace with Ansible Molecule for infrastructure testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
  - Approach: Preserve the same configuration in the Ansible playbooks

- **SSH Security**: The SSH root login restriction must be maintained
  - Approach: Create an Ansible task to enforce the same SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native testing
  - Mitigation: Use Ansible's assert module or Molecule to create equivalent tests
  - For complex tests, consider using the ansible.builtin.shell module to run external validation commands

- **Compliance Metadata**: InSpec tests contain compliance metadata (STIG, CCI identifiers)
  - Mitigation: Preserve this metadata in Ansible task documentation or use custom Ansible roles with appropriate tags

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they're already in Ansible format
   - Review and optimize existing playbooks
   - Implement idempotency improvements if needed

2. **Test Infrastructure** - Medium complexity
   - Replace Test Kitchen with Ansible Molecule
   - Set up equivalent test scenarios

3. **InSpec Tests** - Medium complexity
   - Convert website_https_verify.rb to Ansible tests
   - Convert ssh_profile.rb to Ansible tests

4. **Chef Automate Deployment Scripts** - High complexity
   - Convert bash scripts to Ansible roles for Chef server deployment
   - Implement secure credential handling with Ansible Vault

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance testing
2. The existing Ansible playbooks are functional and follow best practices
3. There is no requirement to maintain backward compatibility with Chef InSpec
4. The team has expertise in Ansible testing methodologies
5. The hardcoded credentials in the setup scripts are for demonstration purposes only and will be properly secured in the migrated solution
6. The Test Kitchen configuration is only used for development/testing and not in production pipelines