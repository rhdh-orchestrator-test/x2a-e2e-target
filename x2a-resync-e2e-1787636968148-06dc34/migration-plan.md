# MIGRATION FROM CHEF/ANSIBLE HYBRID TO ANSIBLE

## Executive Summary

This repository contains a hybrid environment with both Chef and Ansible components, primarily focused on demonstration and testing purposes. The migration scope is relatively small, consisting of Chef InSpec tests alongside Ansible playbooks, plus Chef Automate/Chef Server deployment scripts. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already Ansible-based or can be directly converted to Ansible.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling older SSL protocols and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance testing

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port validation, HTTPS response testing, SSL/TLS protocol verification

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests. Will need to be replaced with Ansible-native testing framework like Molecule.
- `chef-and-ansible/index.html`: Static HTML file, can be directly used in Ansible content.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider maintaining InSpec as a complementary testing tool alongside Ansible

- **Chef Automate/Chef Server**: Replace with:
  - Ansible Automation Platform for enterprise automation management
  - AWX (open source upstream of Ansible Tower) for smaller deployments
  - GitLab CI/CD or GitHub Actions for pipeline-based automation

### Security Considerations

- **SSL/TLS Configuration**: The poodle_fix.yml playbook enforces TLSv1.2 only. This should be maintained or enhanced in the Ansible migration to use current best practices (TLSv1.3 where available).
  
- **SSH Security**: The ssh_profile.rb InSpec test verifies that root login is disabled. This check should be incorporated into the Ansible deployment or as an Ansible-based compliance check.

- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates. Consider enhancing this with Let's Encrypt integration for production environments.

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - No other credential patterns detected in the modules

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec tests to Ansible-native testing will require careful mapping of InSpec resources to Ansible modules.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules and develop reusable test playbooks.

- **Chef Automate/Server Deployment**: The bash scripts for Chef deployment will need complete replacement with Ansible roles.
  - Mitigation: Develop Ansible roles for configuration management platform deployment, potentially using AWX/Ansible Tower.

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (already Ansible, no migration needed)
2. **InSpec Tests** (convert to Ansible-native testing)
3. **Chef Deployment Scripts** (replace with Ansible roles for AWX/Tower deployment)

### Assumptions

1. The repository appears to be primarily for demonstration purposes rather than production use, based on the README reference to being companion examples to a white paper.
2. The Chef InSpec tests are used for validation of Ansible-deployed configurations, suggesting a hybrid approach is already in use.
3. The hardcoded credentials in the deployment scripts are for demonstration only and would be replaced with proper secret management in production.
4. The Test Kitchen configuration suggests this is a testing/development environment rather than production code.
5. The Apache configuration in the Ansible playbooks may need updates for newer versions of Ubuntu beyond 20.04.