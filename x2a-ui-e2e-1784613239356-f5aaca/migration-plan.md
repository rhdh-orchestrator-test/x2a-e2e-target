# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Refactoring existing Ansible playbooks to follow best practices
3. Replacing Chef Automate and Chef Infra Server deployment scripts with Ansible equivalents

Given the limited scope and small number of components, this migration can be completed in approximately 1-2 weeks by a single engineer familiar with both Chef and Ansible technologies.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

After thorough scanning of the repository using file_search for:
- Puppet modules: `file_search(pattern="**/manifests/init.pp")` - No results found
- Chef cookbooks: `file_search(pattern="**/recipes/default.rb")` - No results found
- PowerShell modules: `file_search(pattern="**/*.psd1")` - No results found

No traditional infrastructure-as-code modules were found. The repository contains:

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

- **website_https_verify**:
    - Description: Chef InSpec test profile for verifying HTTPS configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: HTTPS port verification, SSL protocol verification, content verification

- **ssh_profile**:
    - Description: Chef InSpec test profile for verifying SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, security compliance checks

**CRITICAL PATH VERIFICATION:**
All paths listed above have been verified to exist using the `list_directory` tool:
- `chef-and-ansible/website_https.yml` - Confirmed exists
- `chef-and-ansible/poodle_fix.yml` - Confirmed exists
- `setup-automate/deploy-automate.sh` - Confirmed exists
- `setup-automate/deploy-chef-server.sh` - Confirmed exists
- `chef-and-ansible/tests/website_https_verify.rb` - Confirmed exists
- `chef-and-ansible/tests/ssh_profile.rb` - Confirmed exists

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the `kitchen-ansible` plugin

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for web UI and job scheduling
  - Git repositories for playbook storage
  - Ansible Vault for secrets management

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ is enforced (already implemented in poodle_fix.yml)
  - Consider adding modern cipher suite configurations
  - Implement automatic certificate renewal if moving to production

- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Ensure the Ansible equivalent maintains checks for root login restrictions
  - Consider expanding SSH hardening to include key-based authentication requirements

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely or replaced with Let's Encrypt integration
  - Count of credentials detected:
    - chef-automate-deploy: 5 credentials (username, longusername, useremail, userpassword, orgname)
    - chef-server-deploy: 5 credentials (username, longusername, useremail, userpassword, orgname)

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible assertions or Molecule tests requires understanding the testing logic and implementing equivalent checks.
  - Mitigation: Create a mapping document between InSpec resources and Ansible modules/assertions.

- **Chef Automate Replacement**: Chef Automate provides compliance scanning, infrastructure visibility, and application automation.
  - Mitigation: Implement AWX/Tower for automation, integrate with additional tools like Prometheus/Grafana for monitoring, and OpenSCAP for compliance.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need refactoring to follow best practices.
2. **InSpec Tests**: Moderate complexity, requires converting to Ansible-compatible testing framework.
3. **Chef Deployment Scripts**: High complexity, requires replacing Chef Automate/Infra Server with Ansible Tower/AWX or equivalent solution.

### Assumptions

1. The primary purpose of this repository is for demonstration/examples rather than production use, as indicated by the README.
2. The InSpec tests are used for validation of the Ansible playbook configurations rather than as part of a larger compliance framework.
3. The Chef Automate and Chef Infra Server deployment scripts are intended for setting up a test/demo environment rather than production infrastructure.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in a production environment.
5. The self-signed certificates are acceptable for the demonstration environment but would need to be replaced with proper CA-signed certificates in production.
6. The repository does not contain actual Chef cookbooks or recipes that need migration, only InSpec tests and Ansible playbooks.