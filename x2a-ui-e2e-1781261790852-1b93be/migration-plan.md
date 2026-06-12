# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The primary focus is on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, focusing on two Ansible playbooks with associated InSpec tests, plus Chef Automate/Chef Server deployment scripts. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test profile that validates HTTPS configuration and website availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that validates SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file for the web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use ansible-lint for static analysis
  - Option 3: Implement custom Ansible playbooks with assert modules for validation

- **Test Kitchen**: Replace with Ansible-native testing frameworks:
  - Option 1: Migrate to Ansible Molecule for test orchestration
  - Option 2: Use simple Vagrant or Docker-based testing with direct Ansible invocation

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
  - Approach: Ensure the Ansible playbook continues to enforce the same Apache SSL configuration

- **SSH Security**: The InSpec test validates SSH root login security
  - Approach: Create an equivalent Ansible playbook to enforce and validate SSH security settings

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates are generated during deployment and should be handled securely

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native validation
  - Mitigation: Use Ansible assert modules or custom modules to perform equivalent validation checks
  - Consider implementing Ansible roles that include both configuration and validation tasks

- **Test Kitchen Workflow**: Replacing the Test Kitchen workflow with an Ansible-native approach
  - Mitigation: Implement Ansible Molecule for a similar development and testing workflow

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
   - Minimal changes needed, primarily reorganization into Ansible roles

2. **poodle_fix.yml** (low risk, already in Ansible format)
   - Minimal changes needed, consider merging into the website_https role as a security hardening task

3. **InSpec Tests** (moderate complexity)
   - Convert to Ansible-native validation using assert modules or Molecule verifiers

4. **Chef Automate Deployment Scripts** (high complexity)
   - Convert bash scripts to Ansible roles for infrastructure deployment

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being production infrastructure code
2. The InSpec tests are intended to validate both the initial deployment and ongoing compliance
3. The Chef Automate and Chef Server deployment scripts are separate from the main Ansible+InSpec demonstration
4. There is no complex state management or data persistence requirements beyond the basic web server configuration
5. The target environment is Ubuntu 20.04 running on Vagrant VMs
6. There are no external service dependencies beyond what's installed by the playbooks themselves
7. The hardcoded credentials in the deployment scripts are for demonstration purposes only
8. The repository does not include actual Chef cookbooks that need migration, only InSpec tests