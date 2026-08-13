# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstration and example purposes. The primary content consists of:

1. Ansible playbooks for configuring web servers with HTTPS
2. Chef InSpec tests for compliance verification
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration scope is relatively small, with most components already in Ansible format. The primary migration effort will involve converting the Chef InSpec tests to Ansible-compatible testing frameworks and replacing the Chef Automate/Infra Server deployment scripts with Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a complete migration, with minimal complexity due to the limited scope and example-focused nature of the repository.

## Module Migration Plan

This repository contains a mix of Ansible playbooks, Chef InSpec tests, and Chef server deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **ssh-compliance**:
    - Description: Chef InSpec test profile for verifying SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, compliance with security standards

- **website-https-verification**:
    - Description: Chef InSpec test profile for verifying HTTPS website functionality
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTPS response testing, SSL protocol verification

- **chef-automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be updated to use Ansible-native testing frameworks.
- `chef-and-ansible/index.html`: Static HTML file used in the website example. Can be directly incorporated into Ansible playbooks.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with on-premises focus

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible's built-in inventory management for multi-node testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - Git repositories for playbook/role storage
  - Ansible Vault for secrets management

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL configuration is maintained during migration.
  - Migration approach: Preserve the SSL configuration logic in the Ansible playbooks
  
- **SSH Security**: The InSpec tests verify SSH root login is disabled.
  - Migration approach: Create equivalent Ansible assertions or use ansible-lint to verify SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef server deployment scripts (username, password)
  - Migration approach: Move credentials to Ansible Vault

### Technical Challenges

- **Testing Framework Conversion**: Converting Chef InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation: Map InSpec resources to equivalent Ansible modules and assertions
  
- **Chef Server Replacement**: Replacing Chef Server functionality with Ansible-native solutions.
  - Mitigation: Document the equivalent Ansible AWX/Tower setup procedures

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format. May need minor updates for best practices.
2. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb): Convert to Ansible-compatible testing frameworks.
3. **Chef Server Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Replace with Ansible playbooks for AWX/Tower deployment.

### Assumptions

1. The repository is primarily for demonstration purposes and not a production deployment.
2. The InSpec tests are used for verification only and not part of a larger compliance framework.
3. There are no external dependencies or integrations not visible in the repository.
4. The hardcoded credentials in the deployment scripts are examples and not actual production credentials.
5. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
6. The migration will maintain the same functionality but using Ansible-native approaches.
7. Test Kitchen is only used for local testing and not part of a CI/CD pipeline.