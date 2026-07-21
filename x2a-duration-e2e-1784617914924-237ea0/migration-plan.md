# MIGRATION FROM CHEF/INSPEC TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The repository appears to be a demonstration or example repository rather than a production infrastructure codebase. The migration scope is relatively small, focusing on:

1. Migrating Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Migrating Chef Automate/Chef Server deployment scripts to Ansible

Given the limited scope and example nature of the repository, this migration is estimated to be low complexity and could be completed within 1-2 weeks by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests, Ansible playbooks, and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

After thorough examination using file_search for patterns "**/manifests/init.pp", "**/recipes/default.rb", and "**/*.psd1", no traditional Puppet modules, Chef cookbooks, or PowerShell modules were found in this repository. The repository contains:

- **chef-and-ansible/tests/ssh_profile.rb**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: Compliance test for SSH configuration security

- **chef-and-ansible/tests/website_https_verify.rb**:
    - Description: Chef InSpec test that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: Tests port 443 listening, HTTPS response, SSL/TLS protocol security

- **chef-and-ansible/website_https.yml**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **chef-and-ansible/poodle_fix.yml**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables only TLSv1.2

- **setup-automate/deploy-automate.sh**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **setup-automate/deploy-chef-server.sh**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be updated to use Ansible-native testing frameworks.
- `chef-and-ansible/index.html`: Simple HTML file used as a template for website deployment. Can be migrated as-is to Ansible.
- `chef-and-ansible/README.md`: Documentation explaining the purpose of the examples.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the `kitchen-ansible` plugin

- **Chef Automate/Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or GitHub Actions for pipeline automation
  - Compliance scanning using OpenSCAP or similar tools integrated with Ansible

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Migration should maintain or improve the security posture:
  - Ensure continued enforcement of TLSv1.2+ only
  - Consider updating to include TLSv1.3 support
  - Maintain self-signed certificate generation or improve with Let's Encrypt integration

- **SSH Hardening**: The InSpec tests verify SSH security. Migration should:
  - Maintain testing for SSH root login restrictions
  - Consider expanding SSH hardening to include key-based authentication requirements
  - Implement equivalent tests in Ansible-compatible format

- **Vault/secrets management**:
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` should be migrated to Ansible Vault
  - Total credentials detected: 2 sets (username/password combinations in deployment scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach may require additional logic and careful validation to ensure equivalent test coverage.
  - Mitigation: Use Ansible's `assert` module with carefully crafted conditions that match InSpec's expectations

- **Chef Server Deployment**: Replacing Chef Server deployment with equivalent Ansible functionality requires understanding of what Chef Server components are actually needed.
  - Mitigation: Determine if a full Chef Server replacement is needed or if simpler Ansible inventory management is sufficient

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format. Consolidate and improve according to best practices.
2. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb): Moderate complexity to convert to Ansible-compatible testing.
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity, requiring replacement of Chef-specific functionality with Ansible equivalents.

### Assumptions

1. This repository appears to be a demonstration or example repository rather than production infrastructure code.
2. The primary purpose seems to be showing how Chef InSpec can work alongside Ansible for compliance testing.
3. The actual infrastructure being managed is minimal (just an Apache web server with SSL).
4. There are no external dependencies or integrations beyond what's visible in the repository.
5. The deployment scripts for Chef Automate/Server are intended for demonstration purposes and may not reflect production deployment requirements.
6. No traditional Chef cookbooks (with recipes/default.rb), Puppet modules (with manifests/init.pp), or PowerShell modules (.psd1) are present in the repository.
7. The migration goal is to consolidate everything to Ansible, including the testing currently done with InSpec.