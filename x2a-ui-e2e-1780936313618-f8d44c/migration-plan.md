# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. There are also Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate to a pure Ansible solution. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing the web server. Can be directly used in Ansible.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM setup

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Use Ansible's `assert` module for basic validation
  - Implement Ansible Molecule for comprehensive testing
  - Consider ansible-lint for static code analysis
  - For compliance testing, evaluate OpenSCAP integration with Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Ensure proper SSL settings are maintained during migration.
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented
  
- **SSH Security**: The InSpec tests verify SSH security configurations.
  - Migration approach: Convert InSpec tests to Ansible assert tasks or Molecule verify tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing mechanisms.
  - Mitigation: Use Ansible's assert module for basic tests and Molecule for more complex testing scenarios.
  
- **Chef Automate/Server Deployment**: Replacing Chef Automate and Chef Infra Server deployment scripts.
  - Mitigation: Create Ansible roles for deploying alternative compliance and configuration management tools or adapt to deploy Ansible AWX/Tower.

### Migration Order

1. **website_https.yml** (already in Ansible, low risk)
2. **poodle_fix.yml** (already in Ansible, low risk)
3. **InSpec Tests** (moderate complexity, requires conversion to Ansible testing)
4. **Chef Deployment Scripts** (high complexity, requires replacement with Ansible-based alternatives)

### Assumptions

1. The primary goal is to move away from Chef InSpec for testing while maintaining or enhancing compliance capabilities.
2. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are functioning correctly and can be used as-is or with minor modifications.
3. The deployment scripts for Chef Automate and Chef Infra Server need to be replaced with equivalent functionality using Ansible.
4. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs.
5. There is no requirement to maintain backward compatibility with Chef InSpec.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure alternatives.
7. The repository is primarily for demonstration/educational purposes rather than production use.