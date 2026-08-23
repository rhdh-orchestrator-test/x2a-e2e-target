# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec compliance profiles and Ansible playbooks that are used together to deploy and validate secure web servers. The repository also includes scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec compliance profiles to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Replacing Chef Automate/Infra Server deployment scripts with Ansible equivalents

**Estimated Timeline**: 2-3 weeks for a small team (1-2 engineers)
**Complexity**: Medium - The existing Ansible playbooks can be reused with minimal changes, but the InSpec tests will need conversion to an Ansible-compatible testing framework.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec profiles that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys a secure Apache web server with HTTPS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec profile that validates HTTPS configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Validates port 443 is listening, HTTPS is working, SSL3 is disabled, TLS1.2 is enabled

- **ssh_profile**:
    - Description: Chef InSpec profile that validates SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Validates SSH root login is disabled, follows security compliance standards

- **automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Configures system settings, downloads and installs Chef Automate, creates users and organizations

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Configures system settings, downloads and installs Chef Infra Server, creates users and organizations

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec
- `index.html`: Simple HTML template for the website

## Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic validation
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Convert InSpec tests to Python-based tests using pytest

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the Ansible provisioner

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for web UI and API
  - Git repositories for version control
  - CI/CD pipeline for automated testing and deployment

### Security Considerations

- **SSL/TLS Configuration**: The existing playbooks configure Apache with TLS 1.2 and disable vulnerable protocols. This security hardening should be preserved in the migrated solution.
  - Migration approach: Maintain the same SSL/TLS configurations in the Ansible playbooks

- **SSH Hardening**: The InSpec profile validates SSH security configurations.
  - Migration approach: Create an Ansible role for SSH hardening that implements the same controls

- **Self-signed Certificates**: The current solution generates self-signed certificates.
  - Migration approach: Consider integrating with Let's Encrypt for production environments

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Testing Framework Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation: Use Molecule's verifier plugins or implement custom verification using the Ansible assert module

- **Infrastructure Deployment**: Replacing Chef Automate/Infra Server with Ansible management infrastructure.
  - Mitigation: Create Ansible playbooks to deploy AWX/Ansible Tower with similar user/organization structure

- **Compliance Validation**: Ensuring the same level of compliance validation without InSpec.
  - Mitigation: Implement equivalent checks using Ansible's built-in modules or integrate with OpenSCAP

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
   - Review and optimize existing playbooks
   - Convert to Ansible roles for better organization
   - Update any deprecated syntax or modules

2. **Testing Framework** (website_https_verify.rb, ssh_profile.rb) - Medium complexity
   - Convert InSpec tests to Ansible assertions or Molecule tests
   - Ensure all compliance checks are preserved

3. **Infrastructure Deployment** (deploy-automate.sh, deploy-chef-server.sh) - High complexity
   - Create Ansible playbooks to deploy AWX/Ansible Tower
   - Implement user/organization management in Ansible

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation.
2. The existing Ansible playbooks are functional and follow best practices.
3. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
4. The deployment scripts are examples and not production-ready (they contain hardcoded credentials).
5. The migration will preserve all security controls and compliance checks.
6. Test Kitchen is used for development and testing, not for production deployments.
7. The repository is primarily educational/demonstrational rather than a production infrastructure codebase.