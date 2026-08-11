# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance testing. The repository also includes scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the content is already in Ansible format. The main migration tasks will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Updating the Chef Automate/Infra Server deployment scripts to Ansible playbooks
3. Ensuring all compliance requirements are maintained during migration

Estimated timeline: 1-2 weeks for a small team (1-2 engineers)

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 for security compliance

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user creation, organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user creation, organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration on the web server
- `tests/ssh_profile.rb`: InSpec test to verify SSH security compliance (root login disabled)

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml as the driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks
  - Option 4: Consider using Ansible's built-in `--check` mode with custom plugins

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the `kitchen-ansible` plugin

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook:
  - Ensure TLSv1.2 is enforced
  - Disable older protocols (SSLv3)
  - Maintain proper certificate generation and management

- **SSH Security**: The SSH compliance checks in ssh_profile.rb must be preserved:
  - Ensure root login remains disabled
  - Consider adding additional SSH hardening based on CIS benchmarks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of InSpec resources to Ansible modules:
  - Challenge: InSpec's declarative testing style vs. Ansible's procedural approach
  - Mitigation: Create custom Ansible modules or use assert with register for complex tests

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible:
  - Challenge: Ensuring idempotence and proper error handling
  - Mitigation: Use Ansible's command/shell modules with creates/changed_when to ensure idempotence

### Migration Order

1. **website_https.yml** (already in Ansible format, low risk)
   - Review and optimize existing playbook
   - Add documentation and comments

2. **poodle_fix.yml** (already in Ansible format, low risk)
   - Review and optimize existing playbook
   - Add documentation and comments

3. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assertions
   - Convert ssh_profile.rb to Ansible assertions
   - Integrate with CI/CD pipeline

4. **Chef Deployment Scripts** (high complexity)
   - Convert deploy-automate.sh to Ansible playbook
   - Convert deploy-chef-server.sh to Ansible playbook
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment
2. The InSpec tests are critical for compliance validation and must be preserved in functionality
3. The deployment scripts are used for actual Chef infrastructure setup
4. No external dependencies or integrations beyond what's visible in the repository
5. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
6. The migration will not change the fundamental architecture or deployment patterns
7. No custom Chef resources or complex Chef-specific functionality needs to be migrated