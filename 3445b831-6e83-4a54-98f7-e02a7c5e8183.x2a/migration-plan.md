# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for demonstration purposes related to compliance automation. The repository is relatively small and focused on showing how Chef InSpec can be used alongside Ansible for compliance testing. The migration effort is estimated to be low to medium complexity, as most of the content is already in Ansible format, with the main migration work focused on converting Chef InSpec tests to Ansible-compatible testing frameworks.

Estimated timeline: 1-2 weeks for a complete migration, including testing and documentation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH root login security compliance
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality
- `chef-and-ansible/index.html`: Sample HTML file used for testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or any cloud environment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions like:
  - Molecule for infrastructure testing
  - ansible-lint for playbook linting
  - testinfra for infrastructure validation

- **Test Kitchen (with Vagrant driver)**: Replace with:
  - Molecule for Ansible role/playbook testing
  - molecule-vagrant plugin if Vagrant is still needed as the driver

- **Chef Automate/Infra Server**: The deployment scripts should be converted to Ansible playbooks that can:
  - Install and configure equivalent compliance scanning tools
  - Set up users and organizations in the new tooling

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Ensure TLS 1.2 is enforced
  - Disable older protocols (SSL3)
  - Maintain proper certificate generation and management

- **SSH Hardening**: The SSH security profile tests must be converted to equivalent Ansible checks
  - Maintain the check for disabled root login
  - Consider expanding SSH hardening based on CIS benchmarks

- **Vault/secrets management**:
  - Hardcoded credentials in the setup-automate scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in the deployment scripts

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible testing frameworks
  - Mitigation: Use testinfra which has similar syntax and capabilities to InSpec
  - Consider ansible-test for some compliance checks

- **Maintaining Compliance Standards**: Ensuring the same level of compliance checking is maintained
  - Mitigation: Map each InSpec control to equivalent checks in the new testing framework
  - Document the mapping for audit purposes

- **Deployment Script Conversion**: Converting the bash deployment scripts to idempotent Ansible playbooks
  - Mitigation: Break down the scripts into discrete tasks with proper state checking
  - Use Ansible modules for package installation and service management instead of direct commands

### Migration Order

1. **website_https.yml** (already in Ansible format, low risk)
2. **poodle_fix.yml** (already in Ansible format, low risk)
3. **InSpec Tests** (convert to testinfra or other Ansible-compatible testing framework, medium complexity)
4. **Chef Deployment Scripts** (convert to Ansible playbooks, medium complexity)

### Assumptions

1. The repository is primarily for demonstration purposes and may not represent a complete production environment
2. The InSpec tests are used for compliance validation of infrastructure set up by Ansible
3. The deployment scripts are examples and may need customization for actual production use
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. No actual Chef cookbooks or recipes are present in the repository, only InSpec tests and deployment scripts
6. The migration will maintain the same level of security compliance checking
7. The current Test Kitchen setup is used for development and testing only