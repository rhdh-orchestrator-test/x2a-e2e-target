# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for demonstration purposes related to compliance automation. The repository appears to be a collection of examples rather than a production infrastructure codebase. The migration scope is relatively small, focusing on:

1. Ansible playbooks for configuring HTTPS websites
2. Chef InSpec tests for verifying configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a complete migration. The main effort will be in converting the Chef InSpec tests to Ansible-compatible testing frameworks like Molecule with TestInfra.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **ssh-profile**:
    - Description: Chef InSpec test profile that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, compliance testing

- **website-https-verify**:
    - Description: Chef InSpec test profile that verifies HTTPS website configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening verification, HTTPS response testing, SSL protocol verification

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Molecule for Ansible testing.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Molecule with TestInfra for infrastructure testing
  - Option 2: Use Ansible Assert module for simple tests
  - Option 3: Keep InSpec but integrate with Ansible using the inspec_exec module

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Infra Server**: Consider migrating to:
  - Ansible Automation Platform for orchestration
  - Ansible Semaphore or AWX for web UI
  - Compliance scanning can be handled by OpenSCAP integrated with Ansible

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ is enforced (already done in poodle_fix.yml)
  - Consider adding HSTS headers
  - Update cipher suites to modern recommendations

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. Migration should:
  - Maintain this security check
  - Consider expanding SSH hardening with Ansible's openssh_config module

- **Self-signed Certificates**: The playbook generates self-signed certificates. Migration should:
  - Maintain this capability using Ansible's openssl_* modules
  - Consider adding option for Let's Encrypt integration

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password)
  - Recommend migrating to Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to TestInfra/Molecule**: Converting InSpec tests to TestInfra requires understanding the different syntax and capabilities. Mitigation: Create a mapping of InSpec resources to TestInfra equivalents.

- **Test Kitchen to Molecule**: The testing workflow will change. Mitigation: Document the new workflow and provide examples for the team.

- **Chef Automate Deployment**: The Chef Automate deployment scripts need to be converted to Ansible roles. Mitigation: Create an Ansible role that performs the same setup steps.

### Migration Order

1. **website-https.yml** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to a proper Ansible role structure

2. **poodle-fix.yml** (low risk, already Ansible)
   - Integrate into the website-https role as a task
   - Add conditional logic for applying the fix

3. **InSpec Tests** (moderate complexity)
   - Convert to Molecule/TestInfra tests
   - Ensure they validate the same conditions

4. **Chef Deployment Scripts** (high complexity)
   - Create Ansible roles for Chef server deployment
   - Consider if Chef server is still needed or if complete migration to Ansible is desired

### Assumptions

1. The repository is primarily for demonstration purposes and not a production codebase
2. The InSpec tests are used for validating the Ansible playbook configurations
3. The deployment scripts are examples and not used in production environments
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. There is no complex data structure or external dependencies beyond what's visible in the code
6. The migration goal is to standardize on Ansible while maintaining the same functionality
7. The security requirements (SSL configuration, SSH hardening) need to be preserved
8. Test coverage should remain the same or improve after migration