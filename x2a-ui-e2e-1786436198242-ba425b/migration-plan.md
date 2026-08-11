# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The repository also includes shell scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `index.html`: Sample HTML file used in the website deployment example

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule with testinfra for testing
  - Option 2: Use community.general.assert module for basic compliance checks
  - Option 3: Integrate with ansible-lint for static analysis

- **Test Kitchen**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for test orchestration
  - Option 2: Use simple Vagrant or Docker-based testing scripts

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with specific security settings:
  - Ensure the TLS protocol restrictions (disabling SSLv3, enabling TLSv1.2) are maintained in the migrated solution
  - Maintain the self-signed certificate generation process

- **SSH Security**: The InSpec tests verify SSH root login restrictions:
  - Ensure equivalent checks are implemented in the Ansible-based testing solution

- **Credentials in Scripts**: The deployment scripts contain hardcoded credentials:
  - 2 instances of hardcoded passwords in deploy-automate.sh and deploy-chef-server.sh
  - Migrate these to Ansible Vault or another secure secret management solution

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible-based tests:
  - Challenge: InSpec has specific matchers and resource types that may not have direct equivalents
  - Mitigation: Map InSpec resources to appropriate Ansible modules or testinfra methods

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible:
  - Challenge: The scripts perform Chef-specific operations that need to be reimagined in an Ansible-only environment
  - Mitigation: Determine if Chef server deployment is still needed or if it can be replaced with Ansible automation controller

### Migration Order

1. **InSpec Tests** (High priority, moderate complexity)
   - Convert website_https_verify.rb to Ansible-compatible tests
   - Convert ssh_profile.rb to Ansible-compatible tests

2. **Test Kitchen Configuration** (Medium priority, low complexity)
   - Replace kitchen.yml with Ansible Molecule configuration

3. **Deployment Scripts** (Low priority, high complexity)
   - Convert deploy-automate.sh to Ansible playbook
   - Convert deploy-chef-server.sh to Ansible playbook

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependencies while preserving the existing Ansible playbooks.
2. The deployment scripts for Chef Automate and Chef Infra Server may no longer be needed in an Ansible-only environment.
3. The security compliance requirements currently implemented in InSpec tests still need to be verified in the migrated solution.
4. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs.
5. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) can be used as-is without modification.