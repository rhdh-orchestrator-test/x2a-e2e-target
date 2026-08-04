# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and infrastructure configuration. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Migrating Chef Automate and Chef Infra Server deployment scripts to Ansible

The complexity is low to moderate, with an estimated timeline of 1-2 weeks for a complete migration. The repository appears to be primarily educational/demonstration in nature rather than a production infrastructure codebase.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache by enforcing TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration compliance testing, STIG compliance checks

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening tests, HTTPS content verification, SSL/TLS protocol tests

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

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include converting to Ansible-native testing frameworks like Molecule.
- `chef-and-ansible/index.html`: Simple HTML file used for testing the web server. Can be directly used in Ansible content.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use ansible-test for integration testing
  - Option 2: Use Molecule with testinfra for infrastructure testing
  - Option 3: Continue using InSpec but invoke it from Ansible

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for orchestration
  - AWX/Tower for web UI and API
  - Git repositories for content management

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enforces TLSv1.2
  - Migration approach: Use Ansible's `lineinfile` or `template` modules with identical configuration values

- **SSH Hardening**: Ensure SSH root login remains disabled in the migrated solution
  - Migration approach: Use Ansible's `lineinfile` or `template` modules to configure sshd_config

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be generated using Ansible's crypto modules (already in use)
  - Count of credentials detected: 3 (username, password, email in setup scripts)

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to an Ansible-compatible testing framework
  - Mitigation: Map InSpec resources to equivalent testinfra or Molecule verifiers
  - Example: InSpec's `describe port(443)` becomes testinfra's `host.socket("tcp://0.0.0.0:443").is_listening`

- **Chef Server Deployment**: Replacing Chef Server deployment with equivalent Ansible management
  - Mitigation: Use AWX/Tower for web UI and API functionality
  - Consider if full Chef Server functionality is needed or if simpler Ansible-only approach is sufficient

### Migration Order

1. **website_https.yml** (Priority 1 - already Ansible, low risk)
   - No conversion needed, already in Ansible format
   - Review for best practices and optimization

2. **poodle_fix.yml** (Priority 1 - already Ansible, low risk)
   - No conversion needed, already in Ansible format
   - Review for best practices and optimization

3. **InSpec Tests** (Priority 2 - moderate complexity)
   - Convert to Ansible-compatible testing framework
   - Ensure same compliance checks are maintained

4. **Chef Deployment Scripts** (Priority 3 - high complexity)
   - Convert bash scripts to Ansible roles for deploying management infrastructure
   - Replace Chef-specific components with Ansible equivalents

### Assumptions

1. The repository is primarily for demonstration/educational purposes rather than production use
2. The InSpec tests are used for validating the Ansible playbooks rather than as part of a larger Chef ecosystem
3. There is no dependency on Chef-specific features that might be difficult to replicate in Ansible
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. The simple web application doesn't have complex application dependencies
6. The Chef Automate and Chef Server deployment scripts are standalone and not part of a larger Chef infrastructure
7. No external data sources or complex variable structures are in use
8. No complex orchestration or workflow is required beyond what's visible in the playbooks