# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests used for compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible's native testing capabilities while preserving the existing Ansible playbooks. The repository also includes Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Sample HTML file used for testing the web server deployment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's native testing capabilities:
  - For basic tests: Use the `assert` module in Ansible
  - For more complex compliance testing: Implement Ansible Lint custom rules or migrate to Molecule testing framework with testinfra
  - Consider using ansible-test for integration testing

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality for testing Ansible roles with various drivers including Vagrant

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or alternative infrastructure management solution
  - Consider migrating to AWX/Tower for web UI and API access
  - Use Ansible Collections for configuration management

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLS 1.2 remains enforced
  - Consider updating to also include TLS 1.3 support

- **SSH Hardening**: The SSH security controls from ssh_profile.rb need to be implemented as Ansible tasks
  - Create equivalent checks using Ansible's assert module or Ansible Lint

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts need to be moved to Ansible Vault
  - Count: 2 credential sets (username/password) in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible's testing capabilities
  - Mitigation: Use Ansible's assert module for basic tests and consider Molecule with testinfra for more complex compliance testing
  - Create custom Ansible modules if needed for specialized tests

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs equivalent functionality
  - Mitigation: Consider implementing custom reporting using Ansible callback plugins or integrating with compliance tools like OpenSCAP

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible
  - Mitigation: Create Ansible roles for Chef server deployment or consider migrating to Ansible Automation Platform entirely

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may need minor updates for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible testing framework
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible playbooks
4. **Testing Infrastructure**: Replace Test Kitchen with Molecule

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as indicated in the README.md.
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and follow best practices.
3. There is no dependency on Chef beyond InSpec for compliance testing.
4. The deployment scripts are used for setting up a test environment rather than production infrastructure.
5. The hardcoded credentials in the deployment scripts are not used in production environments.
6. The target environment is Ubuntu 20.04 as specified in kitchen.yml.
7. The migration will maintain the same functionality and security posture as the original implementation.
8. No additional Chef cookbooks or resources are used beyond what is visible in the repository.