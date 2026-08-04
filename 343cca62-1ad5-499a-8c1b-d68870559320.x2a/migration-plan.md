# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The repository also includes scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating the existing Ansible playbooks
3. Migrating Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks

Given the limited scope and the fact that part of the codebase is already in Ansible, this migration is estimated to be of low complexity and could be completed within 1-2 weeks by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains a combination of Ansible playbooks, Chef InSpec tests, and Chef server deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to address the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTP response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance tagging

- **automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Will need to be updated to use pure Ansible testing approach.
- `index.html`: Static HTML file used in the website deployment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for both on-premises and cloud deployment (referenced in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the ansible-lint tool for static analysis
  - Option 4: Consider using the InSpec Ansible resource pack if maintaining InSpec is preferred

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or GitHub Actions for pipeline automation
  - Ansible Vault for secrets management

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. This needs to be preserved in the migrated solution.
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented in the existing playbooks.

- **SSH Security**: The InSpec tests verify SSH security configurations.
  - Migration approach: Convert InSpec tests to Ansible assertions or Molecule tests that verify the same security controls.

- **Credentials in Scripts**: The deployment scripts contain hardcoded credentials.
  - Migration approach: Move all credentials to Ansible Vault and use variables instead of hardcoded values.

- **Vault/secrets management**:
  - Hardcoded credentials found in both deployment scripts (username, password)
  - No encryption or secure storage mechanism currently in place
  - Total credentials detected: 2 sets of login credentials in plain text

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks may require different approaches for different test types.
  - Mitigation: Use a combination of Ansible's assert module, Molecule, and possibly custom modules where needed.

- **Chef Server Deployment**: Replacing Chef Server deployment with equivalent Ansible functionality.
  - Mitigation: Use Ansible AWX/Tower for web UI and job scheduling, GitLab CI/CD or GitHub Actions for pipeline automation.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format. May need minor updates for best practices.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-compatible testing frameworks.
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible playbooks and implement proper secrets management.

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, based on the README content.
2. The InSpec tests are intended to be run against systems provisioned by the Ansible playbooks.
3. The deployment scripts are used for setting up Chef infrastructure, which would be replaced by Ansible infrastructure in the migrated solution.
4. The current implementation uses Test Kitchen with Vagrant for local testing, which would be replaced by Molecule in the Ansible-only solution.
5. There are no external dependencies or integrations beyond what's visible in the repository.
6. The migration will maintain the same functionality but using Ansible-native approaches where possible.
7. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be properly secured in a production environment.