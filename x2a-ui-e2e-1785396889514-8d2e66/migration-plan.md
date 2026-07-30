# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment of Chef InSpec tests and Ansible playbooks focused on compliance automation and Chef server deployment. The migration scope is relatively small, with only a few Ansible playbooks and Chef InSpec tests that need to be consolidated into a pure Ansible solution. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, STIG compliance check

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL/TLS protocol verification

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/index.html`: Sample HTML file used for testing. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (identified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native solutions:
  - For SSH compliance checks: Use ansible-lint or OpenSCAP with Ansible
  - For web server verification: Use Ansible URI module and assert module
  
- **Chef Automate/Server**: Replace with Ansible Automation Platform or alternative CI/CD solution
  - Consider migrating to AWX/Ansible Tower for web UI and job scheduling
  - Use Ansible Vault for secrets management instead of Chef encrypted data bags

### Security Considerations

- **SSL/TLS Configuration**: The current implementation enforces TLSv1.2 and disables vulnerable protocols. Migration should maintain or enhance this security posture.
  - Migration approach: Use Ansible's crypto modules to generate certificates and configure Apache with secure defaults.

- **SSH Hardening**: Current InSpec tests verify SSH root login is disabled.
  - Migration approach: Create Ansible role for SSH hardening that applies the same controls and includes verification tasks.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 2 (username/password in deployment scripts)

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible verification tasks.
  - Mitigation strategy: Use Ansible's assert module with command/shell modules to perform equivalent checks, or consider integrating with Ansible Lint or OpenSCAP.

- **Chef Server Deployment**: Replacing Chef Server deployment scripts with Ansible roles.
  - Mitigation strategy: Create Ansible roles that perform equivalent setup tasks or consider if Chef Server is still needed after migration.

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
2. **poodle_fix.yml** (low risk, already in Ansible format)
3. **InSpec Tests** (moderate complexity, requires conversion to Ansible verification tasks)
4. **Chef Server Deployment Scripts** (high complexity, requires complete rewrite as Ansible roles)

### Assumptions

1. The primary purpose of this repository is for compliance testing and demonstration, not production deployment.
2. The Chef InSpec tests are used for validation only and not part of a larger Chef ecosystem.
3. The Chef Server deployment scripts are used for setting up test environments and not critical production infrastructure.
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions.
5. There are no external dependencies or integrations not visible in the repository.
6. The migration will consolidate all functionality into pure Ansible without maintaining Chef components.