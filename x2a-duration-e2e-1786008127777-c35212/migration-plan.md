# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a pure Ansible solution. The repository appears to be primarily a demonstration/example repository showing how Chef InSpec can be used alongside Ansible for compliance automation. Additionally, there are shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and Chef InSpec profiles to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity due to the limited number of components and their straightforward nature.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec profiles that need individual migration planning:

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
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec profile for verifying HTTPS website functionality
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTP response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile for verifying SSH security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **automate-deploy**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/index.html`: Sample HTML file for the website example
- `README.md`: Repository overview documentation

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic validation
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Convert InSpec tests to Ansible roles that perform the same checks

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the Ansible provisioner

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain the same level of security in Apache configuration

- **SSH Security**: The SSH compliance checks in ssh_profile.rb must be preserved
  - Ensure root login remains disabled
  - Maintain compliance with security standards referenced (SRG-OS-000112, etc.)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible validation
  - Mitigation: Use Ansible assert module or custom modules to perform the same validation checks
  - Consider using Ansible's built-in `uri` module to replace the HTTP checks

- **Chef Automate Deployment**: Replacing Chef Automate deployment scripts with Ansible
  - Mitigation: Create Ansible roles that perform the same server setup and configuration
  - Consider if Chef Automate is still needed or if it should be replaced with an Ansible-native solution

### Migration Order

1. Ansible Playbooks (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
2. InSpec Tests (website_https_verify.rb, ssh_profile.rb) - Moderate complexity, requires conversion to Ansible testing
3. Deployment Scripts (deploy-automate.sh, deploy-chef-server.sh) - Higher complexity, requires architectural decisions

### Assumptions

1. The repository is primarily for demonstration/educational purposes and not a production system
2. The InSpec tests are used for validation only and not for ongoing compliance monitoring
3. The deployment scripts are examples and not used in production environments
4. There is no requirement to maintain Chef components after migration
5. The target environment will continue to be Ubuntu-based systems
6. The self-signed certificates are acceptable for the use case and don't need to be replaced with CA-signed certificates
7. The hardcoded credentials in the deployment scripts are for demonstration purposes only