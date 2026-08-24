# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate deployment scripts and Ansible playbooks with Chef InSpec tests. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, consisting of:

1. Two Ansible playbooks for configuring a web server with HTTPS
2. Two Chef InSpec test profiles for validating configurations
3. Two bash scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks to fully migrate all components to pure Ansible solutions. The main challenge will be replacing Chef InSpec with equivalent Ansible-native testing solutions.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Tests for port 443 listening, HTTPS response, and SSL protocol security

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Tests for SSH root login being disabled, compliance with security standards

- **deploy-automate**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Hostname configuration, system tuning, Chef Automate deployment, user and organization creation

- **deploy-chef-server**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Hostname configuration, system tuning, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `index.html`: Static HTML content for the web server. Can be directly used in Ansible.

## Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but the deployment scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider integrating with DISA STIG Ansible content for compliance testing

- **Test Kitchen**: Replace with Ansible-native testing frameworks:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible Runner for execution and testing

- **Chef Automate/Infra Server**: Replace with Ansible automation platform:
  - Option 1: Migrate to AWX/Ansible Tower for web UI and REST API
  - Option 2: Use Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL/TLS. Ensure the migration maintains or improves the security posture:
  - Update SSL/TLS configurations to current best practices (TLS 1.3 support)
  - Ensure proper certificate management
  - Consider integrating with Let's Encrypt for automated certificate management

- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Ensure Ansible playbooks apply the same SSH hardening measures
  - Consider using the `ansible.posix.ssh_config` module for SSH configuration

- **Vault/secrets management**:
  - Current repository has hardcoded credentials in the deployment scripts (username, password)
  - Migrate to Ansible Vault for secure credential storage
  - Consider integrating with external secret management solutions (HashiCorp Vault, AWS Secrets Manager, etc.)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test controls:
  - Challenge: InSpec has rich, declarative syntax for compliance testing
  - Mitigation: Use a combination of Ansible assert, custom modules, and external tools like ansible-test

- **Chef Automate Functionality**: Replacing Chef Automate's functionality with Ansible equivalents:
  - Challenge: Chef Automate provides compliance reporting and visualization
  - Mitigation: Consider AWX/Tower with custom dashboards or integration with compliance tools

- **Test Kitchen Workflow**: Recreating the Test Kitchen workflow in Ansible:
  - Challenge: Test Kitchen provides a standardized testing workflow
  - Mitigation: Implement Molecule testing with similar stages (create, converge, verify, destroy)

### Migration Order

1. **website_https.yml** (Priority 1): Core web server configuration playbook, already in Ansible format
2. **poodle_fix.yml** (Priority 1): Security-related playbook, already in Ansible format
3. **InSpec Tests** (Priority 2): Convert to Ansible-native testing solutions
4. **Chef Deployment Scripts** (Priority 3): Convert to Ansible playbooks for deploying alternative automation platforms

### Assumptions

1. The primary goal is to eliminate Chef dependencies while maintaining the same functionality
2. The existing Ansible playbooks can be used with minimal modifications
3. The team has expertise in both Chef and Ansible
4. There is no requirement to maintain backward compatibility with Chef
5. The deployment scripts for Chef Automate/Infra Server will be replaced with equivalent Ansible automation platform deployment
6. The security and compliance requirements will remain the same
7. The target environment (Ubuntu 20.04) will remain the same
8. The testing framework can be changed as long as it provides equivalent functionality