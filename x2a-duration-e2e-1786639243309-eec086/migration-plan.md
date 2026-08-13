# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate/Chef Infra Server setup scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more standardized Ansible structure while preserving the compliance testing capabilities currently provided by Chef InSpec. The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
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
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration on the web server
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration (root login disabled)

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles
- **Chef InSpec**: Replace with Ansible-compatible compliance testing tools:
  - Option 1: Convert InSpec tests to Ansible assertions
  - Option 2: Use ansible-lint for static analysis
  - Option 3: Maintain InSpec for testing but invoke it from Ansible

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in poodle_fix.yml
  - Approach: Convert to an Ansible role with appropriate templates for SSL configuration
  - Ensure the TLSv1.2 requirement is maintained

- **SSH Hardening**: The SSH security profile must be maintained
  - Approach: Convert InSpec SSH tests to Ansible assertions or maintain as separate compliance checks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible testing mechanisms
  - Mitigation: Consider using ansible.builtin.assert or maintaining InSpec as a compliance tool called from Ansible

- **Chef Automate/Server Setup**: Replacing Chef infrastructure setup scripts with Ansible equivalents
  - Mitigation: Create Ansible roles for Chef server deployment or consider migrating to alternative compliance platforms

### Migration Order

1. **website_https.yml** (Priority 1 - low risk, high value)
   - Convert to Ansible role with proper directory structure
   - Create templates for Apache configuration
   - Implement idempotent certificate management

2. **poodle_fix.yml** (Priority 2 - low complexity)
   - Integrate into the Apache role as a security hardening task
   - Ensure proper handlers for service restarts

3. **InSpec Tests** (Priority 3 - moderate complexity)
   - Convert to Ansible testing framework or maintain as separate compliance checks
   - Ensure all security checks are preserved

4. **Chef Deployment Scripts** (Priority 4 - high complexity)
   - Evaluate if Chef infrastructure is still needed
   - If needed, create Ansible roles for Chef server deployment
   - If not needed, document alternative compliance approaches

### Assumptions

1. The primary goal is to standardize on Ansible while maintaining compliance capabilities
2. The existing InSpec tests represent required security controls that must be preserved
3. The Chef Automate/Server setup scripts may be optional depending on the future compliance strategy
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. Vagrant will continue to be used for development/testing environments
6. No external dependencies or integrations beyond what's visible in the repository
7. No complex data structures or environment-specific configurations are in use