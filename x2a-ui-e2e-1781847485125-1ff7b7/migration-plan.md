# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment of Chef InSpec tests and Ansible playbooks that are used together for compliance automation. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for continuous compliance validation. Additionally, there are Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate to a pure Ansible solution. The estimated timeline for this migration is 1-2 weeks, with low complexity.

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
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Simple HTML file used as a template for the website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible alternatives:
  - For website_https_verify.rb: Use Ansible's uri module for HTTP checks and community.crypto modules for SSL validation
  - For ssh_profile.rb: Use ansible-lint or OpenSCAP integration with Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source alternatives like AWX

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
- **SSH Security**: The SSH root login restriction must be preserved in the migrated solution
- **Self-signed Certificates**: The process for generating self-signed certificates should be maintained or improved
- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts (username, password)
  - SSL certificate and key generation and storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing mechanisms will require careful mapping of test assertions
  - Mitigation: Use ansible-test, Molecule, or integrate with tools like OpenSCAP or Lynis

- **Compliance Reporting**: Chef InSpec provides built-in compliance reporting that needs to be replicated in Ansible
  - Mitigation: Consider integrating with compliance tools like OpenSCAP or using Ansible Automation Platform's compliance features

### Migration Order

1. **website_https.yml** (already in Ansible, no migration needed)
2. **poodle_fix.yml** (already in Ansible, no migration needed)
3. **website_https_verify.rb** (convert InSpec tests to Ansible tests)
4. **ssh_profile.rb** (convert InSpec compliance control to Ansible)
5. **chef-automate-deployment** and **chef-server-deployment** (replace with Ansible Automation Platform deployment)

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the same level of compliance automation
2. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't need modification
3. There is no requirement to maintain backward compatibility with Chef Automate or Chef Infra Server
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. The deployment scripts for Chef Automate and Chef Infra Server are used for setting up the infrastructure and not part of the regular compliance automation workflow
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with proper secret management in the migrated solution