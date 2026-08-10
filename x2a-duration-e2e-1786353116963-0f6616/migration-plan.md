# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment with Ansible playbooks and Chef InSpec tests. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The repository also includes scripts for setting up Chef Automate and Chef Infra Server environments.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to convert. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible playbooks (which can be kept largely as-is) and moderate complexity for converting the InSpec tests to Ansible-native solutions.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Tests port 443 listening, HTTPS response, SSL protocol security

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Checks SSH root login settings, compliance with security standards

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `deploy-automate.sh`: Script to deploy Chef Automate and Chef Infra Server
- `deploy-chef-server.sh`: Script to deploy Chef Infra Server without Automate

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for testing Ansible roles
  - Option 4: Consider Red Hat Ansible Automation Platform with built-in compliance capabilities

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible Playbook integration tests using GitHub Actions or other CI/CD tools

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Approach: Keep the same configuration settings but convert to Ansible role format
  - Consider using the community.crypto collection for certificate management

- **SSH Security**: The SSH compliance checks need to be converted to Ansible
  - Approach: Create Ansible tasks that perform the same checks as the InSpec profile
  - Use Ansible's assert module to validate SSH configuration

- **Vault/secrets management**:
  - No explicit secrets management was detected in the current codebase
  - Hardcoded credentials were found in the setup scripts (username, password)
  - Recommendation: Use Ansible Vault to secure these credentials in the migrated solution

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing
  - Mitigation: Create custom Ansible modules or use assert statements to perform the same validation
  - Consider using the ansible.builtin.uri module to replace HTTP/HTTPS tests

- **Certificate Management**: Ensuring proper SSL certificate generation and management
  - Mitigation: Use the community.crypto collection which provides modules for managing SSL certificates

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs an equivalent
  - Mitigation: Consider integrating with Ansible Automation Platform for compliance reporting or use a third-party tool

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, can be kept largely as-is but should be converted to roles for better organization
2. **InSpec Tests** (website_https_verify.rb): Moderate complexity, convert to Ansible assertions or Molecule tests
3. **InSpec Profiles** (ssh_profile.rb): Higher complexity, convert to Ansible compliance checks
4. **Infrastructure Scripts**: Convert Chef Automate/Server setup scripts to Ansible roles if needed

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the same level of compliance testing
2. The existing Ansible playbooks are working correctly and don't need significant modification
3. There is no requirement to maintain backward compatibility with Chef tools
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
5. The deployment scripts for Chef Automate and Chef Server are not needed in the migrated solution
6. No external data sources or inventory systems are being used
7. No complex secret management is currently implemented
8. The migration will include improving the organization of code by using Ansible roles and collections