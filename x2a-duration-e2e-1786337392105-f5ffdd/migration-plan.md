# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance testing alongside Ansible deployments. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for deploying and configuring a web server with HTTPS
2. Chef InSpec tests for validating the deployment
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks to fully migrate all components to pure Ansible. The primary focus will be on replacing Chef InSpec tests with Ansible-native testing solutions while preserving the existing Ansible playbooks.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test profile that validates HTTPS configuration and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS content validation, SSL protocol security verification

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `chef-and-ansible/index.html`: Static HTML file for the website. Can be directly incorporated into Ansible content.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Implement Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or Ansible's built-in testing capabilities

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible playbooks for infrastructure deployment
  - Consider migrating to Ansible Tower/AWX for enterprise features

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL security configurations that must be preserved:
  - Self-signed certificate generation
  - Protocol security (disabling SSLv3, enabling TLSv1.2)
  - These should be migrated to Ansible roles with appropriate security hardening

- **Hardcoded Credentials**: The deployment scripts contain hardcoded credentials:
  - Username, password, and email in deploy-automate.sh and deploy-chef-server.sh
  - These should be moved to Ansible Vault or another secure secret management solution

- **Vault/secrets management**:
  - No existing vault implementation detected
  - 2 credential sets identified in deployment scripts (username/password)
  - Recommend implementing Ansible Vault for all credentials

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions:
  - Port checks can use Ansible's wait_for module
  - HTTP content checks can use uri module with return_content: yes
  - SSL protocol validation may require custom modules or external commands

- **Chef Server Deployment**: The Chef server deployment scripts need to be completely rewritten as Ansible playbooks:
  - Consider whether Chef Automate/Server is still needed or if Ansible Tower/AWX would be a suitable replacement
  - If Chef is still required, create Ansible roles for Chef server deployment

### Migration Order

1. **website_https playbook** (low risk, already Ansible): Minimal changes needed, just reorganize into proper Ansible role structure
2. **poodle_fix playbook** (low risk, already Ansible): Minimal changes needed, incorporate into a security hardening role
3. **InSpec tests** (moderate complexity): Convert to Ansible-native testing framework
4. **Chef deployment scripts** (high complexity): Rewrite as Ansible playbooks or evaluate if they're still needed

### Assumptions

1. The primary purpose of this repository is for demonstration/examples rather than production use
2. The Chef InSpec tests are used for validation but could be replaced with Ansible-native testing
3. The deployment scripts are examples and not critical production infrastructure
4. There are no external dependencies or integrations not visible in the repository
5. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file
6. No specific compliance frameworks are being targeted beyond the SSL/TLS security hardening
7. No external data sources or dynamic inventory is being used
8. The repository is primarily focused on demonstrating Chef InSpec with Ansible rather than being a comprehensive infrastructure solution