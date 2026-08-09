# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef infrastructure setup scripts and Ansible playbooks with Chef InSpec tests. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, consisting of:

1. Two Ansible playbooks for configuring a web server with HTTPS
2. Two Chef InSpec test profiles for validating the configuration
3. Two bash scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **LOW** with an estimated timeline of **1-2 weeks** to fully migrate all components to pure Ansible solutions. The main effort will involve replacing Chef InSpec tests with Ansible-native testing solutions like Molecule and integrating with alternative compliance frameworks.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef components that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test profile that validates HTTPS configuration and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that validates SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec. Will need to be replaced with Ansible Molecule for testing.
- `index.html`: Simple HTML file used as a test page for the web server. Can be directly used in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule for infrastructure testing
  - Option 2: Integrate with OpenSCAP for compliance testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen with Vagrant**: Replace with:
  - Ansible Molecule for testing infrastructure code
  - GitHub Actions or other CI/CD pipeline for automated testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise automation
  - AWX (open source upstream of Ansible Tower) for smaller deployments
  - GitLab CI/CD or GitHub Actions for pipeline orchestration

### Security Considerations

- **SSL Configuration**: The current playbooks configure Apache with SSL. Migration should:
  - Maintain the same SSL security standards (TLSv1.2+)
  - Use Ansible vault for storing sensitive information
  - Consider using Let's Encrypt modules instead of self-signed certificates

- **SSH Hardening**: The current InSpec tests validate SSH security. Migration should:
  - Include equivalent SSH hardening roles from Ansible Galaxy
  - Implement equivalent compliance checks using Ansible assert modules or Molecule

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely, potentially using ansible-vault
  - Count of credentials detected: 3 (username, password, and SSL key)

### Technical Challenges

- **Compliance Testing**: Replacing Chef InSpec with equivalent Ansible testing capabilities:
  - Mitigation: Use Ansible Molecule with testinfra or OVAL/OpenSCAP integration
  - Consider ansible-lint for static analysis of security practices

- **Deployment Automation**: Replacing Chef Automate/Server deployment scripts:
  - Mitigation: Create equivalent Ansible roles for configuration management
  - Consider AWX/Ansible Tower for web UI and API capabilities

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (Priority 1, low risk)
   - Already Ansible playbooks, only need minor adjustments for best practices
   - Refactor into proper Ansible roles with variables

2. **InSpec Tests** (Priority 2, moderate complexity)
   - Convert to Ansible Molecule tests or equivalent
   - Ensure compliance metadata is preserved

3. **Chef Deployment Scripts** (Priority 3, high complexity)
   - Replace with Ansible roles for configuration management
   - Consider if Chef Automate/Server is still needed or can be replaced entirely

### Assumptions

1. The repository is primarily for demonstration purposes showing Chef InSpec with Ansible, not a production deployment
2. The target environment is Ubuntu 20.04 running on Vagrant VMs
3. There are no external dependencies or integrations not visible in the repository
4. The Chef Automate/Server deployment is intended for on-premises use
5. The hardcoded credentials in the scripts are for demonstration only and would be replaced in production
6. The SSL configuration is meant to demonstrate security hardening, not provide production-ready certificates
7. The InSpec tests are meant to validate both Ansible-managed and potentially other systems
8. No complex data structures or external inventory sources are being used