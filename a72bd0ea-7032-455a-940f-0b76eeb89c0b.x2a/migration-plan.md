# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance testing with Ansible playbooks. The repository is relatively small and appears to be primarily for demonstration purposes rather than a full production infrastructure. The migration scope is limited, with the main focus being on standardizing the existing Ansible playbooks and integrating the Chef InSpec tests into an Ansible-native workflow.

**Timeline Estimate**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

## Module Migration Plan

This repository contains a mix of Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

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
- `tests/website_https_verify.rb`: InSpec test for verifying HTTPS website configuration
- `tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-lint for static analysis
  - Option 2: Integrate with Molecule for testing
  - Option 3: Convert InSpec tests to Ansible assert tasks or use the ansible.builtin.assert module
  - Option 4: Keep InSpec as a testing tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role/playbook testing
  - Option 2: Simple Vagrant/Docker workflow with custom test scripts

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Option 1: Ansible playbooks for deploying alternative compliance platforms
  - Option 2: Ansible AWX/Tower for centralized management

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should maintain:
  - Self-signed certificate generation
  - Proper SSL protocol settings (TLSv1.2 enforcement)
  - Disabling vulnerable protocols (SSLv3)

- **SSH Hardening**: The InSpec tests verify SSH security settings:
  - Ensure SSH root login remains disabled
  - Maintain compliance with security benchmarks (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy scripts

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native testing requires:
  - Understanding the InSpec resource model (port, http, ssl, sshd_config)
  - Creating equivalent assertions in Ansible
  - Solution: Use ansible.builtin.assert or consider keeping InSpec as a testing tool

- **Maintaining Compliance Reporting**: Chef InSpec provides compliance reporting that needs equivalent in Ansible:
  - Solution: Consider integrating with tools like Ansible AWX/Tower for reporting
  - Alternative: Use OpenSCAP with Ansible for compliance scanning

### Migration Order

1. **website_https.yml** (Priority 1): Already an Ansible playbook, needs minimal changes to follow best practices
2. **poodle_fix.yml** (Priority 1): Already an Ansible playbook, needs minimal changes to follow best practices
3. **InSpec Tests** (Priority 2): Convert to Ansible-native testing or integrate InSpec with Ansible workflow
4. **Chef Deployment Scripts** (Priority 3): Replace with Ansible playbooks for alternative solutions

### Assumptions

1. The repository is primarily for demonstration purposes rather than production use
2. The main goal is standardizing on Ansible rather than maintaining Chef components
3. Compliance testing is a key requirement that must be preserved in the migration
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. No external dependencies or integrations beyond what's visible in the repository
6. No complex data structures or state management requirements
7. No specific performance requirements for the deployed applications
8. No specific security requirements beyond what's tested in the InSpec profiles