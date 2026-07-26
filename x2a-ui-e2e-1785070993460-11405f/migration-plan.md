# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need to be migrated to a unified Ansible solution. The repository appears to be a demonstration of how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, with only a few Ansible playbooks and InSpec test files to convert. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

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
    - Description: Chef InSpec profile that checks SSH security configurations
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `index.html`: Static HTML content for the website. Can be directly used in Ansible templates.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For compliance testing: Replace with Ansible Lint and custom modules
  - For infrastructure validation: Use Ansible assert module and molecule for testing
  - For security scanning: Consider integration with OpenSCAP or other security tools

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality for testing Ansible roles
  - Can use the same Vagrant driver for local testing

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or improve security settings:
  - Ensure TLSv1.2 or higher is enforced
  - Maintain self-signed certificate generation or improve with Let's Encrypt integration
  
- **SSH Hardening**: The InSpec tests verify SSH security. Migration should include:
  - Ansible tasks to enforce SSH security settings
  - Equivalent tests using Ansible assert or custom modules

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 sets of credentials in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible validation
  - Mitigation: Create custom Ansible modules or use assert module with appropriate conditions
  - Consider using Ansible's built-in testing capabilities or integrating with external testing frameworks

- **Chef Automate Deployment**: Replacing Chef Automate deployment with equivalent Ansible functionality
  - Mitigation: Evaluate if Chef Automate is still needed or if it can be replaced with Ansible Tower/AWX
  - If Chef Automate is still required, create Ansible roles to handle the installation and configuration

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, may need minor updates for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity, requires conversion to Ansible testing framework
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires evaluation of whether to replace Chef infrastructure or just the deployment method

### Assumptions

1. The primary goal is to consolidate on Ansible as the configuration management tool, eliminating Chef components where possible
2. The InSpec tests are used for validation and compliance checking, not for active configuration management
3. The deployment scripts for Chef Automate and Chef Server may be replaced with Ansible roles or eliminated if the Chef infrastructure is no longer needed
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. The security requirements represented in the InSpec tests need to be maintained in the Ansible solution
6. Test Kitchen is used only for development/testing and not in production environments