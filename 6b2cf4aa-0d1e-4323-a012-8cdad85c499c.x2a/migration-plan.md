# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for continuous compliance. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Security hardening for Apache SSL configuration

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **Chef Automate/Server Deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash scripts
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML content for the web server

### Target Details

Based on the source repository:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Convert InSpec tests to Ansible roles with appropriate checks

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
- **SSH Hardening**: The SSH security checks in ssh_profile.rb need to be implemented as Ansible tasks
- **Self-signed Certificates**: The certificate generation process should be preserved in the Ansible roles

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions
- **Chef Automate Deployment**: The Chef server deployment scripts need to be replaced with appropriate Ansible roles for whatever compliance solution will replace Chef Automate

### Migration Order

1. **website_https.yml** (already in Ansible format, low risk)
2. **poodle_fix.yml** (already in Ansible format, low risk)
3. **InSpec Tests** (convert to Ansible testing framework, moderate complexity)
4. **Chef Deployment Scripts** (convert to Ansible roles, higher complexity)

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the same level of compliance automation
2. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
3. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't need significant changes
4. A replacement for Chef Automate's compliance capabilities will be needed
5. The repository is primarily for demonstration purposes as indicated by the README.md
6. No actual Chef cookbooks exist in this repository, only InSpec tests and Ansible playbooks
7. The migration will need to maintain the same level of security validation currently provided by InSpec tests