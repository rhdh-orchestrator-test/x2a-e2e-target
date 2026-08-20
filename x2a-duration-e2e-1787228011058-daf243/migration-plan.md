# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server setup. The migration scope is relatively small, focusing on:

1. Ansible playbooks for web server configuration with HTTPS
2. Chef InSpec tests for compliance verification
3. Shell scripts for Chef Automate and Chef Infra Server deployment

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a single engineer. The main focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure automation.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
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

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing framework or adapting to use Molecule.
- `chef-and-ansible/index.html`: Static HTML content for the web server. Can be directly used in Ansible content.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Keep InSpec but call it from Ansible using the `command` module

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality but is designed specifically for Ansible

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform
  - Create Ansible playbooks to deploy AAP instead of Chef Automate
  - Migrate user/organization management to AAP teams and organizations

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should:
  - Preserve the TLS 1.2 requirement and disabling of older protocols
  - Consider updating to include TLS 1.3 support
  - Maintain the self-signed certificate generation process

- **SSH Security**: The InSpec tests verify SSH root login is disabled. Migration should:
  - Include equivalent checks in Ansible
  - Consider expanding SSH hardening based on current best practices

- **Vault/secrets management**:
  - Hardcoded credentials in shell scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets (one in each shell script)
  - Type: Username/password pairs for Chef server admin

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or other testing frameworks may require additional logic and different syntax.
  - Mitigation: Use Ansible's `assert` module with appropriate conditions or consider maintaining InSpec for testing while using Ansible for configuration.

- **Chef Server Deployment**: The shell scripts deploy Chef Automate and Chef Infra Server, which won't be needed in an Ansible-only environment.
  - Mitigation: Replace with Ansible Automation Platform deployment playbooks or remove if not needed.

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Minimal changes needed, just standardize and optimize
2. **poodle_fix.yml** (low risk, already Ansible): Minimal changes needed, just standardize and optimize
3. **InSpec Tests** (moderate complexity): Convert to Ansible-native testing or integrate with Ansible
4. **Shell Scripts** (high complexity): Replace with Ansible playbooks for AAP deployment or remove if not needed

### Assumptions

1. The primary goal is to standardize on Ansible and remove Chef dependencies
2. InSpec tests are valuable and their functionality should be preserved
3. The deployment scripts for Chef Automate/Infra Server will be replaced with equivalent Ansible Automation Platform deployment
4. The target environment will remain Ubuntu 20.04 or compatible
5. The self-signed certificates are acceptable (not requiring integration with a CA)
6. The hardcoded credentials in scripts are for demonstration purposes and will be properly secured in the migration
7. The current Vagrant/Test Kitchen setup is for development/testing only and production deployment uses different methods