# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for demonstrating compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible playbooks are already in place. The main migration effort will involve:
1. Converting the Chef InSpec tests to Ansible-native testing solutions
2. Replacing the Chef Automate/Infra Server deployment scripts with Ansible playbooks

**Estimated Timeline**: 1-2 weeks for a complete migration, with minimal complexity due to the small codebase and existing Ansible components.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS support, including self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality on a website
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTP response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance tagging (STIG, CCI)

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML file for the website example

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with on-premises focus

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Keep InSpec but run it from Ansible using the command module

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Simple Vagrant or Docker-based testing scripts

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: AWX/Ansible Tower for enterprise automation platform
  - Option 2: Ansible Semaphore for lightweight GUI
  - Option 3: GitLab CI/CD for pipeline-based automation

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should maintain the same security posture:
  - Ensure TLS 1.2 is enforced
  - Disable older protocols (SSL3, TLS 1.0, TLS 1.1)
  - Maintain self-signed certificate generation

- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Ensure PermitRootLogin is disabled
  - Maintain compliance with security standards (STIG, CCI)

- **Vault/secrets management**:
  - Hardcoded credentials in deploy scripts (username, password) should be moved to Ansible Vault
  - No other credential patterns detected in the repository

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions:
  - Challenge: InSpec has specialized resources (like ssl, http) that need equivalent Ansible testing methods
  - Mitigation: Use Ansible's uri module for HTTP testing and command module with openssl for SSL testing

- **Compliance Reporting**: InSpec provides rich compliance reporting:
  - Challenge: Maintaining the same level of compliance reporting in Ansible
  - Mitigation: Consider integrating with tools like Ansible Tower/AWX for compliance reporting or keeping InSpec as a testing tool called from Ansible

### Migration Order

1. **website_https.yml and poodle_fix.yml**: Already in Ansible format, no migration needed
2. **InSpec Tests**: Convert to Ansible-native testing or Molecule
   - website_https_verify.rb
   - ssh_profile.rb
3. **Deployment Scripts**: Convert to Ansible playbooks
   - deploy-automate.sh
   - deploy-chef-server.sh

### Assumptions

1. The primary goal is to move all functionality to Ansible, not just the infrastructure configuration
2. The InSpec tests are valuable and need to be preserved in some form
3. The deployment scripts for Chef Automate/Infra Server will be replaced with equivalent Ansible automation
4. The Test Kitchen setup is used primarily for development and testing, not production deployment
5. No external data sources or inventory systems are in use
6. No complex role structure or variable hierarchy exists in the current setup
7. The examples are primarily for demonstration purposes and not production workloads
8. The security configurations (SSL, SSH) are critical to maintain in the migration