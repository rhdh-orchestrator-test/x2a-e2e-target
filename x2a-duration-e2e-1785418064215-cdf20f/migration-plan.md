# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be migrated to a unified Ansible approach. The repository primarily consists of:

1. Ansible playbooks with Chef InSpec tests for compliance validation
2. Bash scripts for deploying Chef Automate and Chef Infra Server

The migration scope is relatively small, with only a few Ansible playbooks and Chef-related deployment scripts. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible playbooks (already in Ansible format) and medium complexity for the Chef server deployment scripts that need to be converted to Ansible roles.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
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
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS website functionality
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Maintain InSpec as a separate testing tool but invoke it from Ansible

- **Chef Automate/Infra Server**: Replace with Ansible automation platform:
  - Option 1: Migrate to AWX/Ansible Tower for web UI and API
  - Option 2: Use Ansible Automation Platform for enterprise features
  - Option 3: Implement GitOps workflow with CI/CD pipeline for Ansible playbooks

### Security Considerations

- **SSL Configuration**: The existing playbooks configure SSL for Apache. Migration should:
  - Maintain or improve the TLS protocol restrictions (currently TLS 1.2 only)
  - Use Ansible's `openssl_*` modules consistently for certificate management
  - Consider using Let's Encrypt integration instead of self-signed certificates

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. Migration should:
  - Include SSH hardening in the Ansible roles
  - Implement equivalent assertions in Ansible for validation

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Recommend migration to Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible assertions or Molecule tests
  - Mitigation: Create equivalent Ansible assert tasks or use the `community.general.assert` module
  - Consider maintaining InSpec tests if already invested in that ecosystem

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible roles
  - Mitigation: Create an Ansible role that performs equivalent setup steps
  - Consider whether Chef Server is still needed or if complete migration to Ansible is preferred

### Migration Order

1. **website_https playbook** (low risk, already in Ansible format)
   - Review and refactor according to Ansible best practices
   - Convert InSpec tests to Ansible assertions

2. **poodle_fix playbook** (low risk, already in Ansible format)
   - Review and refactor according to Ansible best practices
   - Integrate with website_https playbook as appropriate

3. **Chef deployment scripts** (medium complexity)
   - Determine if Chef Server is still required
   - If not, skip this migration
   - If yes, create Ansible roles to deploy Chef infrastructure

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
2. Vagrant will continue to be used for development/testing environments
3. The organization wants to standardize on Ansible and phase out Chef usage
4. The InSpec tests are valuable and should be preserved in some form
5. The Chef Automate/Infra Server deployment may be replaced entirely by Ansible automation
6. No external dependencies or integrations beyond what's visible in the repository
7. No specific performance requirements for the deployed applications
8. No specific high availability or clustering requirements