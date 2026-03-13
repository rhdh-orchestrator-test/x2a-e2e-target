# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations, with a focus on Chef InSpec for compliance testing alongside Ansible playbooks. The migration scope is relatively small, primarily involving:

1. Chef InSpec test profiles that need to be migrated to Ansible-compatible testing frameworks
2. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
3. Existing Ansible playbooks that need to be reviewed and potentially refactored

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a small team, as the repository primarily contains examples rather than a complex production infrastructure.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configurations
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML file used as a test page for the web server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but deployment scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use ansible-test for integration testing
  - Option 3: Implement pytest-ansible for Python-based testing
  - Option 4: Keep InSpec but integrate it with Ansible using the inspec_exec module

- **Test Kitchen**: Replace with:
  - Option 1: Ansible Molecule for testing infrastructure
  - Option 2: Custom Vagrant-based testing workflow using Ansible directly

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: Ansible AWX/Tower for web UI and job scheduling
  - Option 2: GitLab CI/CD or Jenkins for pipeline orchestration
  - Option 3: Ansible Semaphore for lightweight GUI

### Security Considerations

- **SSL Certificate Generation**: The current playbook generates self-signed certificates. Migration should maintain or improve this process, potentially using Let's Encrypt for valid certificates.
  
- **SSH Hardening**: The SSH InSpec profile checks for root login restrictions. Ensure this security check is maintained in the Ansible-based testing.

- **TLS Configuration**: The POODLE fix playbook enforces TLSv1.2. Ensure this security hardening is maintained and consider updating to include TLSv1.3 support.

- **Credentials in Scripts**: The deployment scripts contain hardcoded credentials. These should be moved to Ansible Vault or another secure secret management solution.

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks will require understanding the compliance requirements and implementing equivalent checks.
  - Mitigation: Use ansible.builtin.assert or community.general.assert modules to implement similar checks

- **Chef Server Functionality**: Replacing Chef Server functionality with Ansible equivalents requires understanding the specific use cases.
  - Mitigation: Evaluate if AWX/Tower meets the requirements or if additional tools are needed

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, may need refactoring to follow best practices
2. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Medium complexity, requires converting Bash/Chef commands to Ansible tasks
3. **InSpec Test Profiles** (website_https_verify.rb, ssh_profile.rb): Higher complexity, requires converting Ruby-based tests to Ansible testing framework

### Assumptions

1. The repository appears to be primarily for demonstration purposes rather than production infrastructure, based on the README.md description.
2. The InSpec tests are used for compliance verification of infrastructure provisioned by Ansible, not for testing Chef cookbooks.
3. The deployment scripts are used for setting up Chef infrastructure, which will be replaced by Ansible infrastructure.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.
5. There are no complex data structures or state management requirements beyond what's visible in the repository.
6. The security requirements (SSH hardening, TLS configuration) need to be maintained in the migrated solution.
7. No external dependencies or integrations are required beyond what's explicitly mentioned in the files.