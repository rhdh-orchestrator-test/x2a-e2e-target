# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The repository appears to be a demonstration or example repository rather than a production infrastructure codebase. The migration scope is relatively small, focusing on:

1. Ansible playbooks for configuring web servers with HTTPS
2. Chef InSpec tests for verifying configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, as most of the Ansible code can be reused directly. The primary focus will be on replacing Chef InSpec tests with Ansible-native testing solutions. Estimated timeline: 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **ssh-compliance-test**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, compliance with security standards

- **website-https-test**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTPS response testing, SSL protocol verification

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: If compliance reporting is needed, consider:
  - Ansible Automation Platform for centralized management
  - AWX (open-source Ansible Tower) for job scheduling and reporting
  - Custom reporting solutions using Ansible callbacks

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Migration should maintain or improve the security posture:
  - Ensure TLSv1.2 or higher is enforced (currently done in poodle_fix.yml)
  - Consider adding more modern cipher suites
  - Implement automatic certificate renewal if moving to production

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. Migration should:
  - Maintain this security check
  - Consider expanding SSH hardening with Ansible's openssh_config module

- **Vault/secrets management**:
  - No encrypted secrets were found in the repository
  - Hardcoded credentials exist in the Chef server deployment scripts (username, password)
  - Migration should replace these with Ansible Vault or another secrets management solution

### Technical Challenges

- **Testing Framework Replacement**: Replacing Chef InSpec with Ansible-native testing solutions is the main challenge. InSpec provides a domain-specific language for compliance testing that doesn't have a direct equivalent in Ansible.
  - Mitigation: Use a combination of Ansible assert module, custom modules, and external tools like Molecule to achieve similar testing capabilities.

- **Compliance Reporting**: If compliance reporting is a requirement, replacing Chef Automate's compliance features will require additional tooling.
  - Mitigation: Evaluate tools like Ansible Automation Platform, OpenSCAP, or custom reporting solutions.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they can be used directly with minimal changes.
2. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb): Convert to Ansible-native testing solutions.
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Replace with Ansible playbooks for infrastructure deployment if needed.

### Assumptions

1. The repository is primarily for demonstration purposes and not a production codebase.
2. The main goal is to showcase how Chef InSpec can work alongside Ansible for compliance automation.
3. The target environment is Ubuntu 20.04 running on Vagrant VMs.
4. There's no actual dependency between the Ansible playbooks and Chef components beyond testing.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only.
6. The repository doesn't contain actual infrastructure code for a specific environment.