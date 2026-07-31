# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the content is already in Ansible format. The main migration tasks will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Adapting the Chef Automate/Infra Server deployment scripts to Ansible playbooks

**Estimated Timeline**: 1-2 weeks for a complete migration, with minimal complexity due to the limited scope of Chef-specific components.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
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

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `tests/website_https_verify.rb`: Chef InSpec test for verifying HTTPS configuration
- `tests/ssh_profile.rb`: Chef InSpec test for verifying SSH security configuration
- `README.md`: Documentation files explaining the purpose of the examples

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible's `assert` module for basic testing
  - Option 2: Molecule for more comprehensive testing
  - Option 3: Maintain InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible-specific test frameworks

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: AWX/Ansible Tower for enterprise automation
  - Option 2: Ansible Automation Platform

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or enhance security:
  - Ensure TLS 1.2+ is enforced (already addressed in poodle_fix.yml)
  - Consider adding more modern cipher suites
  - Maintain self-signed certificate generation or enhance with Let's Encrypt integration

- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Ensure SSH root login remains disabled
  - Consider adding more SSH hardening parameters in the Ansible playbooks

- **Vault/secrets management**:
  - Current implementation has hardcoded credentials in the deployment scripts
  - Migrate to Ansible Vault for secure credential storage
  - Identified credentials:
    - User password in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native testing requires careful mapping of test assertions:
  - Challenge: InSpec has domain-specific language for compliance testing
  - Mitigation: Use Ansible assert module with careful condition mapping, or maintain InSpec as a separate tool

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible:
  - Challenge: The scripts perform Chef-specific operations that need Ansible equivalents
  - Mitigation: Create Ansible roles that install and configure AWX/Tower instead of Chef Server

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, just need review and potential enhancement
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Medium complexity to convert to Ansible-native testing
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Highest complexity, requiring complete rewrite as Ansible playbooks

### Assumptions

1. The primary goal is to move away from Chef components while maintaining the same functionality
2. The InSpec tests are essential and need to be preserved in some form
3. The deployment scripts are used for setting up test/demo environments rather than production
4. The current Ansible playbooks are compatible with modern Ansible versions
5. No external data sources or inventory files are being used
6. The repository is primarily for demonstration/educational purposes rather than production use
7. No complex state management or idempotency concerns exist beyond what's visible in the code
8. No external integrations or APIs are being called beyond what's visible in the scripts