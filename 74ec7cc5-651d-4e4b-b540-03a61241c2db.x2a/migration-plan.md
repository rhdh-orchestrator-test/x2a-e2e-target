# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on deployment automation and compliance testing. The primary components are:

1. Ansible playbooks for configuring web servers with HTTPS
2. Chef InSpec tests for compliance verification
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration scope is relatively small, with only a few Ansible playbooks and Chef InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format or can be easily converted.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that addresses SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **inspec-website-tests**:
    - Description: Chef InSpec tests for verifying HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening tests, HTTP response validation, SSL protocol verification

- **inspec-ssh-profile**:
    - Description: Chef InSpec profile for SSH security compliance testing
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Migrate InSpec tests to Ansible Molecule for infrastructure testing
  - Consider using ansible-lint for static code analysis
  - For compliance testing, evaluate using OpenSCAP with Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that:
  - Install and configure equivalent monitoring and compliance tools
  - Consider AWX/Ansible Tower for web UI and control plane

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL/TLS. Migration should:
  - Maintain TLSv1.2 requirement and SSLv3 disablement
  - Update cipher suites to current best practices
  - Consider using Let's Encrypt instead of self-signed certificates

- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Ensure Ansible playbooks implement the same SSH hardening measures
  - Maintain compliance with referenced standards (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration should use Ansible Vault for credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing tools will require:
  - Mapping InSpec resources to equivalent Ansible modules
  - Ensuring the same level of compliance verification
  - Solution: Use Ansible assert modules and custom modules where needed

- **Chef Automate Replacement**: Finding equivalent functionality in the Ansible ecosystem:
  - AWX/Ansible Tower for UI and workflow
  - Consider additional tools for compliance reporting
  - Solution: Evaluate AWX/Tower with additional compliance tools like OpenSCAP

### Migration Order

1. **website-https playbook** (already in Ansible format, low risk)
2. **poodle-fix playbook** (already in Ansible format, low risk)
3. **InSpec tests** (moderate complexity, requires conversion to Ansible testing framework)
4. **Chef deployment scripts** (high complexity, requires replacement with Ansible equivalents)

### Assumptions

1. The repository is primarily used for demonstration/educational purposes rather than production, based on the README description.
2. The InSpec tests are used for compliance verification of systems managed by Ansible.
3. The Chef Automate and Chef Infra Server deployment scripts are used for setting up a Chef environment, which would be replaced by an Ansible-based solution.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in production.
5. The target environment is Ubuntu 20.04 running on Vagrant VMs for testing.