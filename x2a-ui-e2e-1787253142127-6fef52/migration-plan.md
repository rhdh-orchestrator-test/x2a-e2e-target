# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate and Chef Infra Server setup scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more structured Ansible format and replacing Chef InSpec tests with Ansible-native testing solutions. The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks

- **automate_deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef_server_deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible Molecule for testing.
- `index.html`: Static HTML content for the website, can be directly used in Ansible.

## Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Implement Molecule for comprehensive testing
  - Option 3: Use ansible-lint for static code analysis

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Consider these options:
  - Option 1: Replace with AWX/Ansible Tower for enterprise management
  - Option 2: Use GitLab CI/CD with Ansible for automation
  - Option 3: Implement Ansible Semaphore for lightweight GUI management

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in Ansible:
  - Migrate the OpenSSL certificate generation tasks to use Ansible's crypto modules
  - Consider using Ansible Vault for storing sensitive certificate information

- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Implement equivalent checks using Ansible's assert module or Molecule
  - Create an Ansible role for SSH hardening that implements the same security controls

- **Credential Management**: 
  - The setup scripts contain hardcoded credentials that should be moved to Ansible Vault
  - Count: 2 credential sets (username/password) in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require understanding the equivalent assertions:
  - Challenge: InSpec has specific matchers for SSL/TLS protocols that need to be replicated in Ansible
  - Mitigation: Use Ansible's uri module with appropriate SSL parameters and assert module for validation

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible:
  - Challenge: The scripts install Chef-specific components that may not be needed in an Ansible-only environment
  - Mitigation: Determine if Chef components are still needed or if they can be replaced with Ansible Tower/AWX

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
2. **poodle_fix.yml** (low risk, already in Ansible format)
3. **InSpec Tests** (moderate complexity, requires conversion to Ansible testing)
4. **Chef Deployment Scripts** (high complexity, requires architectural decisions)

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
2. The existing Ansible playbooks are functional and don't require significant logic changes
3. There is no dependency on Chef-specific features that cannot be replicated in Ansible
4. The Chef InSpec tests are used for validation only and not integrated into a larger compliance framework
5. The deployment scripts are used for setting up test environments and not production infrastructure
6. No external data sources or inventory systems are being used that would require integration
7. The migration will maintain the same level of security hardening present in the current implementation