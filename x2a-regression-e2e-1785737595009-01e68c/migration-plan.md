# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Migrating Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks

The complexity is moderate, with most effort focused on converting InSpec tests to equivalent Ansible testing solutions. The estimated timeline for migration is 1-2 weeks, depending on team familiarity with Ansible testing frameworks.

## Module Migration Plan

This repository contains a combination of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security compliance (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be updated to use Ansible-native testing frameworks.
- `index.html`: Static HTML content for the website. Can be directly used in Ansible playbooks.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Keep InSpec but call it from Ansible using the `command` or `shell` module

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the `kitchen-ansible` plugin

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - Git repositories for configuration management
  - Optional CI/CD integration (Jenkins, GitLab CI, etc.)

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Ensure these security hardening measures are preserved in the migrated Ansible playbooks.
  - Migration approach: Maintain the same SSL protocol restrictions (TLSv1.2 only) in the migrated playbooks.

- **SSH Hardening**: The InSpec tests verify SSH security configurations. Ensure equivalent tests are implemented in the Ansible testing framework.
  - Migration approach: Create Ansible assertions or Molecule tests that verify the same SSH configuration parameters.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets in deploy scripts (username/password combinations)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks will require careful mapping of test assertions.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions.

- **Compliance Reporting**: InSpec provides built-in compliance reporting that needs to be replicated in Ansible.
  - Mitigation: Implement custom reporting using Ansible callbacks or integrate with external compliance tools.

- **Chef Server Functionality**: The Chef Server deployment scripts set up user management and organization structures that need Ansible equivalents.
  - Mitigation: Implement equivalent functionality using Ansible AWX/Tower or custom inventory management.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need review and potential refactoring.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity, requires conversion to Ansible testing framework.
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires complete rewrite as Ansible playbooks.

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production, based on the README content.
2. The InSpec tests are intended to be run against systems configured by the Ansible playbooks.
3. The deployment scripts are intended for setting up a Chef infrastructure, which would be replaced by Ansible infrastructure.
4. No external dependencies or integrations beyond what's visible in the repository.
5. No complex data structures or variable hierarchies that would require special handling in Ansible.
6. The migration will maintain the same level of security compliance checking currently provided by InSpec.
7. The target environment will continue to be Ubuntu 20.04 or compatible systems.