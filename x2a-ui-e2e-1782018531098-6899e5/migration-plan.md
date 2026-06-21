# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing profiles and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also contains shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The primary migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks

Estimated timeline: 1-2 weeks for a complete migration, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **inspec_website_https_verify**:
    - Description: Chef InSpec profile that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **inspec_ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH server security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, STIG compliance check

- **chef_automate_deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef_server_deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used as a test page. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Use Ansible Molecule for more comprehensive testing
  - Option 3: Integrate with other tools like Goss or ServerSpec

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that can:
  - Set system parameters (vm.max_map_count, vm.dirty_expire_centisecs)
  - Install and configure equivalent monitoring/compliance solutions (options include AWX/Ansible Tower, Prometheus with Grafana)

### Security Considerations

- **SSL/TLS Configuration**: The poodle_fix.yml playbook addresses SSL POODLE vulnerability. This security hardening should be maintained in the migrated solution.
  - Migration approach: Incorporate the same Apache SSL hardening into a comprehensive web server role.

- **SSH Security**: The ssh_profile.rb InSpec test verifies SSH root login is disabled.
  - Migration approach: Create an Ansible task that ensures PermitRootLogin is not set to 'yes' in sshd_config.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely
  - Document the count and type of credentials detected per module:
    - chef_automate_deployment: 1 password (userpassword variable)
    - chef_server_deployment: 1 password (userpassword variable)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or other testing frameworks may require different approaches to validation.
  - Mitigation strategy: Use Ansible's assert module for basic tests, and consider integrating with specialized testing tools for more complex validations.

- **Chef Automate Functionality**: Replacing Chef Automate's compliance and reporting features with Ansible-native solutions.
  - Mitigation strategy: Evaluate AWX/Tower for reporting and compliance features, or integrate with third-party tools like Prometheus/Grafana for monitoring.

### Migration Order

1. **website_https.yml and poodle_fix.yml** (low risk, already Ansible): Review and optimize existing Ansible playbooks
2. **InSpec tests** (moderate complexity): Convert to Ansible assertions or Molecule tests
3. **Chef deployment scripts** (high complexity): Create Ansible playbooks to replace Chef Automate/Infra Server deployment

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can work alongside Ansible for compliance automation, not for production deployment.
2. The InSpec tests are used primarily for demonstration and educational purposes.
3. The deployment scripts are examples and may need customization for actual production environments.
4. There are no external dependencies or integrations beyond what's visible in the repository.
5. The target environment is Ubuntu 20.04 running on Vagrant VMs.
6. No complex data persistence or state management is required beyond what's in the scripts.
7. No specific performance requirements are defined for the applications.