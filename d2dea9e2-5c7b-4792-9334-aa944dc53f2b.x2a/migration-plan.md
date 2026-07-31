# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Migrating Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks

The migration complexity is low to medium, with an estimated timeline of 1-2 weeks for a single developer or 3-5 days for a small team. The repository appears to be primarily for demonstration purposes rather than production infrastructure.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

- **inspec-website-https**:
    - Description: Chef InSpec test profile for verifying HTTPS configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **inspec-ssh-profile**:
    - Description: Chef InSpec test profile for SSH security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance tagging (STIG/CCI)

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration considerations include replacing with Ansible Molecule for testing.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Use Ansible assert modules for basic compliance checks
  - Option 3: Maintain InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for orchestration and UI
  - GitLab CI/GitHub Actions for pipeline execution
  - Ansible Vault for secrets management

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ is enforced
  - Consider adding more modern cipher suites
  - Implement certificate management via Ansible Vault or external secret management

- **SSH Hardening**: The InSpec tests verify SSH security configurations. Migration should:
  - Incorporate SSH hardening into Ansible roles
  - Maintain compliance with security benchmarks (STIG/CCI referenced in tests)

- **Vault/secrets management**:
  - Hardcoded credentials in deploy scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible testing frameworks will require mapping InSpec resources to Ansible modules or Testinfra methods.
  - Mitigation: Create a mapping document for InSpec resources to Ansible/Testinfra equivalents

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs to be replicated in the Ansible ecosystem.
  - Mitigation: Implement custom reporting using Ansible callback plugins or integrate with compliance tools like OpenSCAP

- **Chef Server Deployment**: The Chef Server deployment scripts need to be converted to idempotent Ansible playbooks.
  - Mitigation: Break down the script into discrete tasks with proper state checking

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need consolidation and best practices applied
2. **InSpec Tests**: Medium complexity, requires conversion to Ansible-compatible testing framework
3. **Chef Deployment Scripts**: Higher complexity, requires converting imperative bash scripts to declarative Ansible playbooks

### Assumptions

1. The repository is primarily for demonstration purposes and not running production workloads
2. The InSpec tests are used for validation only and not part of a larger compliance reporting framework
3. The hardcoded credentials in the deployment scripts are for demonstration and would be replaced in production
4. The self-signed certificates are for testing only and would be replaced with proper certificates in production
5. The Apache configuration is basic and doesn't include complex rewrite rules or custom modules
6. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file
7. There are no external dependencies or integrations not visible in the repository
8. The migration will maintain the same level of functionality and security posture