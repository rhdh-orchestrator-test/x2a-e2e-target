# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing profiles and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also contains Chef Automate and Chef Infra Server setup scripts.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec test profiles to migrate. The estimated timeline for migration would be 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec profiles that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec profile that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **automate-deploy**:
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

- `kitchen.yml`: Test Kitchen configuration file that uses Ansible provisioner and InSpec verifier to test the website_https playbook
- `index.html`: Simple HTML file used as a template or test file

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM setup

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate InSpec tests to Ansible assert modules
  - Option 2: Use Molecule for Ansible role testing
  - Option 3: Keep InSpec but integrate with Ansible using the ansible_inspec module

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Simple Vagrant-based testing scripts

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: Ansible AWX/Tower for orchestration
  - Option 2: GitLab CI/CD or Jenkins for pipeline automation

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or improve the security posture:
  - Ensure TLSv1.2 or higher is enforced
  - Consider adding modern cipher suite configurations
  - Replace self-signed certificates with Let's Encrypt integration

- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions:
  - Ensure Ansible roles enforce the same SSH hardening measures
  - Consider using ansible.posix.ssh_config module for consistent SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests will require understanding the compliance requirements and implementing equivalent checks.
  - Mitigation: Create a mapping document between InSpec resources and Ansible modules

- **Chef Automate Functionality**: If Chef Automate is being used for compliance reporting, an alternative solution will be needed.
  - Mitigation: Evaluate Ansible AWX/Tower compliance capabilities or integrate with third-party compliance tools

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (low risk, already in Ansible format)
   - Only need to be reviewed and potentially refactored to follow best practices
   - Convert to Ansible roles for better organization

2. **InSpec Tests** (moderate complexity)
   - Convert to Ansible assert tasks or Molecule tests
   - Ensure all compliance checks are maintained

3. **Chef Automate/Server Setup Scripts** (high complexity)
   - Replace with Ansible playbooks for setting up Ansible AWX/Tower
   - Migrate user/organization management to AWX/Tower API calls

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments
2. The InSpec profiles are used for compliance validation rather than extensive functional testing
3. There are no external dependencies or integrations not visible in the repository
4. The setup scripts are used for initial environment setup and not for ongoing management
5. No custom Chef resources or complex logic is being used that would require special handling
6. The migration target is a standard Ansible deployment without specialized modules
7. No specific compliance framework requirements beyond what's visible in the InSpec profiles