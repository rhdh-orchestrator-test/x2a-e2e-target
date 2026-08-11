# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate/Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting the existing Ansible playbooks to follow modern Ansible best practices and integrating the Chef InSpec tests into an Ansible-native testing framework. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of playbooks and tests.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible Molecule for testing.
- `index.html`: Static HTML content for the web server. Can be directly used in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Convert InSpec tests to Ansible assert modules
  - Option 2: Use ansible-lint for static analysis
  - Option 3: Integrate with Molecule's verifier framework
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source alternatives like AWX

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure modern cipher suites and protocols are used in the migrated Ansible roles.
- **Self-signed Certificates**: The current implementation uses self-signed certificates. Consider integrating with Let's Encrypt for production environments.
- **SSH Hardening**: The InSpec tests check for SSH security configurations. Ensure these checks are maintained in the Ansible-native testing framework.
- **Vault/secrets management**: 
  - Hardcoded credentials in the Chef deployment scripts (username, password) should be moved to Ansible Vault
  - No other credentials were detected in the repository

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing requires understanding the equivalent assertions and test structure.
  - Mitigation: Use Ansible's assert module and custom modules to replicate InSpec functionality.
- **Chef Automate Deployment**: Replacing Chef Automate deployment with Ansible Automation Platform requires understanding the equivalent functionality.
  - Mitigation: Create Ansible playbooks that install and configure AWX or Ansible Automation Platform.

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Refactor to follow Ansible best practices and role structure
2. **poodle_fix.yml** (low risk, already Ansible): Refactor to follow Ansible best practices and role structure
3. **InSpec Tests** (moderate complexity): Convert to Ansible-native testing framework
4. **Chef Deployment Scripts** (high complexity): Create equivalent Ansible playbooks for deploying Ansible Automation Platform

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
2. The self-signed certificates are acceptable for the target environment, or a proper CA will be integrated.
3. The current SSH hardening requirements will remain the same in the target environment.
4. The deployment scripts for Chef Automate/Infra Server will be replaced with equivalent Ansible Automation Platform deployment.
5. The InSpec tests will be converted to Ansible-native testing rather than maintaining a dual-tool approach.
6. The current Apache configuration and virtual host setup will be maintained in the migrated solution.