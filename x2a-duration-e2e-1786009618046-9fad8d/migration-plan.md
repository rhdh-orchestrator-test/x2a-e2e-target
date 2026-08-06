# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Migrating Chef Automate and Chef Server deployment scripts to Ansible playbooks

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components and the fact that part of the infrastructure is already using Ansible.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Security hardening, SSL configuration

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTP response testing, SSL protocol validation

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH security compliance
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
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML template for the website

## Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use ansible-test framework
  - Option 3: Integrate with pytest-ansible for more complex test scenarios

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the ansible provisioner

- **Chef Automate/Server**: Replace deployment scripts with:
  - Ansible playbooks for infrastructure setup
  - Consider migrating to AWX/Ansible Tower for web UI and automation features

### Security Considerations

- **SSL Configuration**: The current playbooks configure SSL for Apache. Migration should:
  - Maintain the security hardening that disables vulnerable protocols
  - Consider using Ansible Vault for storing certificates and keys
  - Update to modern best practices for TLS configuration

- **SSH Hardening**: The InSpec tests verify SSH security. Migration should:
  - Convert the SSH compliance checks to Ansible-compatible tests
  - Consider implementing the actual SSH hardening as an Ansible role

- **Credentials Management**: The deployment scripts contain hardcoded credentials:
  - 2 instances of hardcoded passwords in the deployment scripts
  - Migration should use Ansible Vault to secure these credentials
  - Consider implementing a more robust secrets management solution

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks:
  - Challenge: InSpec has a domain-specific language for compliance testing
  - Mitigation: Use Ansible assert modules or integrate with pytest for similar functionality

- **Maintaining Compliance Standards**: The current InSpec tests reference specific compliance standards:
  - Challenge: Ensuring the same compliance standards are met with new testing tools
  - Mitigation: Map InSpec controls to equivalent Ansible checks, document compliance coverage

- **Chef Server Functionality**: Replacing Chef Server functionality:
  - Challenge: Chef Server provides configuration management capabilities
  - Mitigation: Implement equivalent functionality using Ansible inventory, collections, and AWX/Tower

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml):
   - Low risk as they're already in Ansible format
   - Only need review and potential optimization

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb):
   - Medium complexity to convert to Ansible testing framework
   - Critical for ensuring continued compliance validation

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh):
   - Highest complexity due to Chef-specific functionality
   - Requires designing equivalent Ansible infrastructure

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production, based on the README description.
2. The Chef InSpec tests are used alongside Ansible for compliance validation, not as part of a larger Chef deployment.
3. The deployment scripts are intended for setting up Chef infrastructure, which would be replaced by Ansible/AWX infrastructure in the migration.
4. The current setup uses Test Kitchen for local testing with Vagrant, which may need to be maintained or replaced with Molecule.
5. No external dependencies or integrations are referenced beyond what's visible in the repository.
6. The migration will maintain the same level of security compliance currently being tested.