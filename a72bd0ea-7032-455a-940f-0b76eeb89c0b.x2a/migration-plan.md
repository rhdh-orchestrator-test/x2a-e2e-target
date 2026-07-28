# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, as the repository contains only a few Ansible playbooks and InSpec tests, along with some Chef Automate and Chef Infra Server setup scripts. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

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
    - Key Features: Disables vulnerable SSL protocols, enables only TLSv1.2

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Compliance testing for SSH configuration

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **chef-automate-setup**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

- **chef-server-setup**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/index.html`: Simple HTML file used for testing. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible compliance testing tools:
  - Option 1: Use Ansible's built-in assert module for basic compliance checks
  - Option 2: Integrate with OpenSCAP using the ansible-openscap role
  - Option 3: Keep InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen with Vagrant**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 only, disabling older protocols. This security practice should be maintained in the migrated Ansible roles.
  - Migration approach: Create an Ansible role for Apache that includes the same SSL hardening measures.

- **SSH Hardening**: The InSpec tests verify that SSH root login is disabled.
  - Migration approach: Create an Ansible role for SSH hardening that disables root login and implement testing with Ansible assert or OpenSCAP.

- **Self-signed Certificates**: The playbooks generate self-signed certificates for HTTPS.
  - Migration approach: Use the Ansible openssl_* modules in the same way, but consider adding support for Let's Encrypt as an improvement.

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - No other credentials detected in the repository

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible assertions or OpenSCAP checks.
  - Mitigation strategy: Create a mapping of InSpec resources to Ansible modules and gradually convert each test.

- **Chef Automate/Server Setup**: The setup scripts for Chef Automate and Chef Infra Server need to be replaced with equivalent Ansible roles.
  - Mitigation strategy: Create Ansible roles that perform the same setup steps, using the existing scripts as a reference.

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Review and refactor into a proper Ansible role structure
2. **poodle_fix.yml** (low risk, already Ansible): Incorporate into the Apache role created from website_https.yml
3. **InSpec tests** (moderate complexity): Convert to Ansible assertions or OpenSCAP checks
4. **Chef setup scripts** (high complexity): Create Ansible roles for Chef Automate and Chef Infra Server setup

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments.
2. The InSpec tests are used for compliance verification after Ansible playbook execution.
3. The Chef Automate and Chef Infra Server setup scripts are used for setting up a test environment.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. No external dependencies or complex configurations are required beyond what is explicitly defined in the playbooks.
6. The migration will maintain the same functionality but reorganize into proper Ansible role structure.
7. No specific CI/CD integration is required based on the repository content.