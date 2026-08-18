# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance testing. There are also Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate to a pure Ansible solution. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **deploy-automate**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **deploy-chef-server**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML file used for testing web server functionality

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in testing framework or integrate with Molecule for testing
  - Migrate `website_https_verify.rb` to Ansible assert tasks or Molecule verify
  - Migrate `ssh_profile.rb` to Ansible security scanning using ansible-lint or OpenSCAP

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Migrate `kitchen.yml` configuration to Molecule scenario

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or AWX
  - Migrate `deploy-automate.sh` and `deploy-chef-server.sh` to Ansible playbooks for infrastructure setup

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL/TLS configuration in Ansible migration:
  - Maintain TLSv1.2 requirement from `poodle_fix.yml`
  - Ensure self-signed certificate generation is properly implemented

- **SSH Security**: The InSpec profile checks SSH root login configuration. Ensure this security check is maintained:
  - Implement equivalent checks using Ansible's assert module or OpenSCAP integration

- **Vault/secrets management**:
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` (username, password)
  - Migration should use Ansible Vault for credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests
  - Mitigation: Use Ansible's assert module for basic tests and consider integrating with specialized testing tools for more complex compliance testing

- **Compliance Reporting**: InSpec provides structured compliance reporting that may need to be replicated
  - Mitigation: Consider using Ansible Automation Platform compliance features or integrate with tools like OpenSCAP

### Migration Order

1. Ansible Playbooks (`website_https.yml`, `poodle_fix.yml`) - Low risk, already in Ansible format
2. Test Kitchen to Molecule configuration - Moderate complexity
3. InSpec tests to Ansible/Molecule tests - Higher complexity
4. Chef Automate/Infra Server deployment scripts to Ansible playbooks - Moderate complexity

### Assumptions

1. The primary goal is to move all functionality to pure Ansible without relying on Chef components
2. Compliance testing is a critical requirement that must be maintained in the migration
3. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
4. No external data sources or complex state management is required
5. The deployment scripts are used for setting up test environments and not production infrastructure
6. No custom Chef resources or complex Chef-specific functionality is being used
7. The InSpec tests are standalone and not integrated with a larger compliance framework
8. The repository is primarily for demonstration purposes rather than production use