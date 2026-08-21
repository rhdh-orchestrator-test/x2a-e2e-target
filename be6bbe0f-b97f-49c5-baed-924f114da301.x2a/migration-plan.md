# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment with Chef InSpec tests and Ansible playbooks. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. There are no traditional Chef cookbooks present, but rather Chef InSpec tests that validate Ansible-managed configurations. Additionally, there are setup scripts for Chef Automate and Chef Infra Server.

The migration scope is relatively small, focusing on:
1. Preserving the compliance testing functionality currently provided by Chef InSpec
2. Maintaining the existing Ansible playbooks
3. Replacing the Chef Automate/Infra Server setup scripts with Ansible equivalents

**Estimated Timeline**: 1-2 weeks for a complete migration, with the majority of time spent on replacing InSpec tests with Ansible-native solutions.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS support, including self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that validates SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, CCI compliance mapping, STIG references

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Static HTML content for the website deployed by the Ansible playbook

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM setup

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic validation
  - Option 2: Implement Molecule for Ansible role testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Keep InSpec as a standalone tool but orchestrate it through Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the Ansible provisioner

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for orchestration and reporting
  - GitLab CI/CD or Jenkins for pipeline automation
  - Compliance scanning using OpenSCAP or similar tools integrated with Ansible

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Approach: Convert to an Ansible role with appropriate templates and handlers

- **Compliance Testing**: The InSpec tests contain security checks that must be preserved
  - Approach: Convert InSpec tests to Ansible assert tasks or Molecule verify tests

- **Vault/secrets management**:
  - No encrypted secrets were detected in the repository
  - The setup scripts contain hardcoded credentials that should be moved to Ansible Vault
  - Count of credentials detected:
    - automate-deploy: 3 (username, useremail, userpassword)
    - chef-server-deploy: 3 (username, useremail, userpassword)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Create custom Ansible modules or use the assert module with carefully crafted conditions

- **Compliance Reporting**: Chef InSpec provides rich compliance reporting that needs an equivalent in Ansible
  - Mitigation: Integrate with AWX/Tower for reporting or use OpenSCAP with Ansible

- **SSL Certificate Management**: The current solution uses Ansible's openssl modules
  - Mitigation: Preserve this approach but enhance with proper secret management for keys

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format
   - Convert to proper Ansible roles with variables, templates, and handlers
   - Implement Ansible Vault for any sensitive data

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity
   - Convert to Ansible assert tasks or Molecule tests
   - Ensure all compliance checks are preserved

3. **Chef Automate/Server Setup** (deploy-automate.sh, deploy-chef-server.sh): High complexity
   - Create Ansible playbooks to replace the bash scripts
   - Implement proper secret management for credentials
   - Consider integration with AWX/Tower for similar functionality

### Assumptions

1. The primary goal is to maintain the compliance testing functionality while moving away from Chef InSpec
2. The existing Ansible playbooks are working correctly and don't need functional changes
3. There's no requirement to maintain backward compatibility with Chef Automate/Infra Server
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
5. The security compliance requirements (STIG, CCI) mentioned in the InSpec tests must be preserved
6. No external data sources or integrations beyond what's visible in the repository
7. The migration will include implementing proper secret management for credentials currently hardcoded in scripts