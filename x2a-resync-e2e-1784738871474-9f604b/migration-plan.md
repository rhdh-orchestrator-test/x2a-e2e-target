# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate/Infra Server setup scripts. The migration scope is relatively small, focusing on:

1. Existing Ansible playbooks that configure web servers with HTTPS
2. Chef InSpec tests used for compliance verification of these Ansible-managed servers
3. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is **LOW to MEDIUM** as most of the content is already in Ansible format, with the main work being to integrate the Chef InSpec testing functionality into Ansible's native testing capabilities. Estimated timeline: **1-2 weeks** for a complete migration.

## Module Migration Plan

This repository contains Ansible playbooks and Chef components that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS configuration and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS content verification, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, security compliance checks with STIG references

- **automate-deploy**:
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
- `index.html`: Sample HTML content for the web server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's native testing capabilities:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Keep InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing
  - Or adapt existing kitchen.yml to work with Ansible-only workflow

- **Chef Automate/Infra Server**: Consider:
  - Migrating to Ansible Tower/AWX for enterprise management
  - Using GitLab CI/CD or other CI tools for pipeline management

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL security configuration that must be preserved:
  - Self-signed certificate generation
  - Protocol security (disabling SSLv3, enabling TLSv1.2)
  - Apache virtual host SSL configuration

- **SSH Security**: The InSpec tests verify SSH security configurations that must be maintained:
  - Root login restrictions
  - STIG compliance requirements

- **Vault/secrets management**:
  - No encrypted secrets detected in the repository
  - Hardcoded credentials in the deployment scripts should be migrated to Ansible Vault

### Technical Challenges

- **InSpec Testing Integration**: The primary challenge is replacing or integrating Chef InSpec tests with Ansible's testing capabilities
  - Mitigation: Use Ansible's assert module or Molecule for testing, or keep InSpec as a standalone tool

- **Chef Automate/Server Deployment**: The deployment scripts need to be converted to Ansible roles
  - Mitigation: Create Ansible roles that perform the same server setup and configuration

- **Security Compliance Verification**: The SSH profile contains specific STIG references and compliance checks
  - Mitigation: Ensure Ansible's testing framework can verify the same security controls with equivalent specificity

### Migration Order

1. **website_https playbook** (already in Ansible format, low risk)
2. **poodle_fix playbook** (already in Ansible format, low risk)
3. **InSpec tests** (medium complexity, requires testing framework decision):
   - website_https_verify.rb
   - ssh_profile.rb
4. **Chef deployment scripts** (higher complexity, requires Ansible role development)

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment
2. The InSpec tests are essential and their functionality must be preserved in the migration
3. The Chef Automate/Server deployment scripts are needed in the migrated solution
4. No external dependencies or integrations beyond what's visible in the repository
5. No CI/CD pipelines or automation workflows are currently in place
6. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
7. The migration will maintain the same level of security hardening present in the original code
8. Security compliance requirements (STIG references in ssh_profile.rb) must be maintained in the migrated solution