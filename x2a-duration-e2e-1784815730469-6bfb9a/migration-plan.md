# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and infrastructure configuration. The repository appears to be a demonstration or example repository showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and Chef InSpec tests to migrate. The estimated timeline for migration would be 1-2 weeks, with low complexity as most of the content is already in Ansible format.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using a self-signed certificate
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration testing, compliance verification

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS is properly configured on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port testing, HTTPS verification, SSL protocol testing

- **deploy-automate**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **deploy-chef-server**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration file for running Ansible playbooks and InSpec tests
- `chef-and-ansible/index.html`: Simple HTML file used as a template for the website
- `chef-and-ansible/README.md`: Documentation explaining the purpose of the examples

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for simple tests
  - Option 2: Use Molecule for Ansible role testing
  - Option 3: Use pytest-ansible for more complex testing scenarios
  - Option 4: Keep InSpec as a standalone testing tool that can be called from Ansible

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: A simple Vagrant or Docker-based testing workflow using Ansible directly

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure that:
  - The SSL protocols are updated to current security standards (TLSv1.3 should be preferred)
  - Self-signed certificates should be replaced with proper CA-signed certificates in production
  - The POODLE fix should be updated to address all current SSL/TLS vulnerabilities

- **SSH Security**: The InSpec tests verify SSH root login is disabled. Ensure:
  - This check is maintained in the Ansible-based testing
  - Additional SSH hardening is implemented (key-based authentication, proper cipher configuration)

- **Vault/secrets management**:
  - Hardcoded credentials in the deploy scripts (username, password) should be moved to Ansible Vault
  - No other credentials were detected in the repository

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks will require:
  - Understanding the InSpec resource model and mapping it to Ansible modules
  - Creating equivalent assertions using Ansible's testing capabilities
  - Ensuring the same level of compliance reporting is maintained

- **Chef Automate Deployment**: The bash scripts that deploy Chef Automate and Chef Infra Server will need to be:
  - Converted to Ansible playbooks
  - Updated to either deploy Chef products or replace their functionality with Ansible Tower/AWX

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (low risk, already in Ansible format)
   - Review and update to current best practices
   - Consolidate into a single role if appropriate

2. **InSpec Tests** (moderate complexity)
   - Convert to Ansible-compatible testing framework
   - Ensure all compliance checks are maintained

3. **Chef Deployment Scripts** (high complexity)
   - Convert to Ansible playbooks
   - Decide whether to maintain Chef deployment or replace with Ansible Tower/AWX

### Assumptions

1. The repository is primarily for demonstration purposes and may not represent a complete production environment
2. The InSpec tests are intended to verify compliance of systems managed by Ansible
3. The deployment scripts are examples and may contain placeholder credentials
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. The Apache configuration is basic and doesn't include complex customizations
6. There are no external dependencies or integrations beyond what's visible in the repository
7. The migration will maintain the same functionality but standardize on Ansible
8. No specific version requirements for Ansible are specified