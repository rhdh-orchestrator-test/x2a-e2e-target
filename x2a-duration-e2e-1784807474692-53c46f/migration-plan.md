# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The repository also includes Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating the existing Ansible playbooks
3. Migrating Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks

Given the limited scope and small number of files, this migration is estimated to be of **low complexity** and could be completed within **1-2 weeks** by a single engineer familiar with both Chef and Ansible technologies.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

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
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (STIG)

- **deploy-automate**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **deploy-chef-server**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests. Will need to be updated to use Ansible-native testing frameworks.
- `index.html`: Simple HTML file used in the website deployment. Can be directly used in Ansible without changes.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the Ansible `community.general.inspec` module to continue using InSpec tests

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Continue using Test Kitchen with the `kitchen-ansible` plugin

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: Ansible AWX or Tower for enterprise automation
  - Option 2: GitLab CI/CD for pipeline-based automation
  - Option 3: Jenkins with Ansible plugins

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure the migration maintains or improves the security posture:
  - Continue enforcing TLSv1.2 and disabling older protocols
  - Consider upgrading to TLSv1.3 where supported
  - Maintain self-signed certificate generation or improve with Let's Encrypt integration

- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Ensure the migrated solution continues to enforce SSH security best practices
  - Maintain compliance with referenced security standards (STIG)

- **Vault/secrets management**:
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` (username, password)
  - These should be migrated to Ansible Vault or another secrets management solution

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing requires understanding the compliance requirements and implementing equivalent checks:
  - Challenge: InSpec has domain-specific language for compliance testing
  - Mitigation: Use Ansible's `assert` module with custom checks or maintain InSpec tests using the `community.general.inspec` module

- **Chef Automate Functionality**: Replacing Chef Automate's compliance and reporting features:
  - Challenge: Chef Automate provides integrated compliance reporting
  - Mitigation: Implement equivalent functionality using Ansible AWX/Tower with compliance scanning plugins or integrate with dedicated compliance tools

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and require minimal changes, making them the logical first step.

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert these to Ansible-compatible testing frameworks to maintain compliance validation capabilities.

3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert these bash scripts to Ansible playbooks, implementing proper secret management.

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production, as suggested by the README mentioning "examples" and "companion to a white paper."

2. The InSpec tests are used to validate the Ansible playbook configurations rather than being part of a larger compliance framework.

3. The deployment scripts are used for setting up test environments rather than production Chef infrastructure.

4. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with proper secret management in production.

5. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file, though the scripts might work on other distributions with minimal modifications.

6. The current setup uses Vagrant for local testing, but the migrated solution should be environment-agnostic.

7. There are no external dependencies or integrations beyond what's visible in the repository.