# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while standardizing them
3. Integrating Chef InSpec tests into an Ansible-native testing framework

Given the limited scope and the fact that part of the infrastructure is already using Ansible, this migration is estimated to be **LOW COMPLEXITY** with an estimated timeline of **1-2 WEEKS**.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef setup scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deploy**:
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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS website functionality
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `index.html`: Sample HTML file used for testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-test with custom modules
  - Option 2: Integrate with Molecule for testing
  - Option 3: Maintain InSpec as a testing tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/collection testing
  - AWX/Tower for workflow testing

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Tower for orchestration and management
  - Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or improve security:
  - Ensure TLS 1.2+ is enforced (already implemented in poodle_fix.yml)
  - Consider adding modern cipher suite configurations
  - Implement certificate renewal automation

- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Ensure PermitRootLogin is disabled
  - Implement as Ansible security role or include in base configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Recommend migrating to Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Automate/Infra Server Deployment**: Converting the bash scripts to Ansible:
  - Challenge: Ensuring idempotent installation of Chef components
  - Mitigation: Use Ansible's package management and command modules with creates/changed_when conditions

- **InSpec Test Integration**: Preserving compliance testing capabilities:
  - Challenge: Maintaining the same level of compliance testing without InSpec
  - Mitigation: Use Ansible assert modules or maintain InSpec as a separate tool called from Ansible

- **Test Kitchen Workflow**: Replicating the testing workflow:
  - Challenge: Maintaining the same development and testing experience
  - Mitigation: Set up Molecule with similar configuration to Test Kitchen

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml):
   - Low risk, already in Ansible format
   - Standardize style and structure
   - Add documentation

2. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh):
   - Medium complexity
   - Convert to Ansible roles for Chef server deployment
   - Consider if Chef components are still needed or can be replaced with Ansible equivalents

3. **Testing Framework** (InSpec tests, kitchen.yml):
   - Higher complexity
   - Set up Molecule testing
   - Integrate or replace InSpec tests

### Assumptions

1. The repository is primarily used for demonstration/examples rather than production deployment
2. The Chef Automate/Infra Server deployment is still required (rather than being replaced entirely by Ansible)
3. The InSpec tests are valuable and should be preserved in some form
4. The target environment will continue to be Ubuntu 20.04 or similar
5. The hardcoded credentials in the scripts are for demonstration purposes only
6. The Apache configuration is representative of actual production needs