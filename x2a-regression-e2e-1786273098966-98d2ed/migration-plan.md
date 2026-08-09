# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef Automate/Infra Server setup scripts. The migration scope is relatively small, focusing on:

1. Existing Ansible playbooks that configure web servers with HTTPS
2. Chef InSpec tests used for compliance verification of Ansible-managed systems
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary work involves:
- Consolidating the existing Ansible playbooks into a proper Ansible role structure
- Converting Chef InSpec tests to Ansible-native testing frameworks
- Replacing Chef Automate/Infra Server deployment scripts with Ansible playbooks

## Module Migration Plan

This repository contains Ansible playbooks and Chef components that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS configuration and SSL security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS content verification, SSL protocol security verification

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Static HTML content for the web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - ansible-test for collection testing

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for web UI and job scheduling
  - Git repositories for playbook/role storage
  - CI/CD pipeline integration for automated testing and deployment

### Security Considerations

- **SSL Configuration**: The current playbooks configure Apache with SSL. Migration should:
  - Maintain or improve the SSL security posture
  - Use Ansible's crypto modules for certificate generation
  - Consider integrating with Let's Encrypt for proper certificates

- **Hardening**: The POODLE fix playbook addresses specific SSL vulnerabilities. Migration should:
  - Incorporate this into a comprehensive security role
  - Add additional hardening based on CIS benchmarks
  - Use Ansible security automation roles from Ansible Galaxy

- **Vault/secrets management**:
  - Current scripts contain hardcoded passwords in the Chef server deployment scripts
  - Migration should use Ansible Vault to secure sensitive values

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests will require careful mapping of test functionality
  - Mitigation: Create a test mapping document and validate each test case individually

- **Chef Server Functionality**: If Chef Server is being used for configuration management, additional Ansible roles will need to be developed
  - Mitigation: Inventory Chef Server usage and develop equivalent Ansible functionality

### Migration Order

1. **website_https playbook** (low risk, already Ansible)
   - Refactor into a proper Ansible role structure
   - Add documentation and variables

2. **poodle_fix playbook** (low risk, already Ansible)
   - Incorporate into a security hardening role
   - Add additional security best practices

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible assert tasks or Molecule tests
   - Validate test coverage

4. **Chef Automate/Server deployment scripts** (high complexity)
   - Create Ansible playbooks for AWX/Tower deployment
   - Develop user/organization management playbooks

### Assumptions

1. The current Ansible playbooks are used in production and need to be preserved functionally
2. The Chef InSpec tests are essential for compliance verification
3. Chef Automate/Infra Server is being used for infrastructure management
4. No custom Chef cookbooks are in use beyond what's visible in the repository
5. The target environment will continue to be Ubuntu 20.04 or similar
6. The migration will consolidate all configuration management to Ansible
7. No external dependencies or integrations exist beyond what's visible in the repository