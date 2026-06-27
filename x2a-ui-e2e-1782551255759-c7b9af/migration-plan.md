# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. There are also Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate to a pure Ansible solution. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, compliance with security standards

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML file used as a test page for the web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace with `ansible-test` for basic functionality testing
  - Use Ansible Molecule for more comprehensive testing
  - Consider ansible-lint for static code analysis
  - For compliance testing specifically, consider OpenSCAP integration with Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
  - Approach: Use Ansible's `lineinfile` or `template` module to manage SSL configuration

- **SSH Security**: The SSH root login restriction must be maintained
  - Approach: Use Ansible's `lineinfile` or `template` module to manage SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
    - Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing
  - Mitigation: Use Ansible's assert module for basic tests, and consider integrating with tools like Molecule for more complex testing scenarios

- **Chef Automate Deployment**: Replacing Chef Automate with Ansible automation
  - Mitigation: Consider using AWX/Ansible Tower as a replacement for Chef Automate's functionality

### Migration Order

1. **website_https.yml** (already in Ansible, no migration needed)
2. **poodle_fix.yml** (already in Ansible, no migration needed)
3. **website_https_verify.rb** (convert InSpec tests to Ansible assertions)
4. **ssh_profile.rb** (convert InSpec tests to Ansible assertions)
5. **deploy-automate.sh** and **deploy-chef-server.sh** (convert to Ansible roles for infrastructure setup)

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the same level of compliance testing
2. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't need modification
3. The deployment scripts for Chef Automate and Chef Infra Server need to be replaced with equivalent Ansible functionality
4. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs
5. There is no requirement to maintain backward compatibility with Chef InSpec
6. The security requirements (SSL configuration, SSH security) must be maintained in the migrated solution
7. No external dependencies or integrations beyond what's visible in the repository
8. The migration is primarily focused on the testing methodology rather than changing the actual infrastructure configuration