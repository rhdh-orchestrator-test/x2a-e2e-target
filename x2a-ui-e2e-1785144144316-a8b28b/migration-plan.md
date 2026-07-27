# MIGRATION FROM CHEF AND BASH SCRIPTS TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks, Chef InSpec tests, and Bash scripts for Chef Automate/Chef Infra Server deployment. The migration scope is relatively small, with only a few components to migrate. The estimated timeline for complete migration is 1-2 weeks, with low complexity as most components are already in Ansible format or are simple Bash scripts that can be easily converted.

## Module Migration Plan

This repository contains Ansible playbooks, Chef InSpec tests, and Bash scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS, creates self-signed certificates, and deploys a simple "Hello World" website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by enforcing TLSv1.2 and disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server on a VM
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server (without Automate) on a VM
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Used for local development and testing.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration on the web server.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test to verify SSH hardening compliance.
- `chef-and-ansible/index.html`: Sample HTML file used for testing the web server.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml and referenced in apt package versions)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing using:
  - ansible-lint for static code analysis
  - Molecule for integration testing
  - ansible.builtin.assert for runtime validation
  - Consider keeping InSpec tests and integrating them with Ansible using the ansible_inspec module

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for orchestration and UI
  - Ansible Collections for configuration management
  - GitLab CI/GitHub Actions for pipeline integration

### Security Considerations

- **SSL Configuration**: The playbooks enforce TLSv1.2 and disable older protocols. Migration should maintain or enhance this security posture.
  - Migration approach: Use ansible.builtin.lineinfile or ansible.builtin.template with proper validation

- **Self-signed Certificates**: The playbooks generate self-signed certificates for HTTPS.
  - Migration approach: Use community.crypto.openssl_* modules (already in use)

- **SSH Hardening**: InSpec tests verify SSH root login is disabled.
  - Migration approach: Implement equivalent checks using ansible.posix.sshd_config module

- **Vault/secrets management**:
  - Hardcoded credentials in Bash scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Integration**: The repository uses InSpec for compliance testing.
  - Mitigation: Either maintain InSpec tests alongside Ansible or migrate tests to Ansible's testing framework

- **Chef Server Deployment**: The Bash scripts deploy Chef Server components.
  - Mitigation: Create equivalent Ansible roles for deploying alternative configuration management solutions

### Migration Order

1. **website_https playbook** (already in Ansible format, low risk)
2. **poodle_fix playbook** (already in Ansible format, low risk)
3. **Chef deployment scripts** (moderate complexity, requires converting Bash to Ansible)
4. **InSpec tests** (higher complexity, requires converting Ruby tests to Ansible tests)

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or newer.
2. The deployment will continue to use self-signed certificates rather than certificates from a trusted CA.
3. The Chef Automate/Infra Server deployment is for testing/demo purposes given the hardcoded credentials.
4. The InSpec tests are used for compliance validation and will need equivalent functionality in the Ansible solution.
5. The migration will not change the fundamental architecture or functionality of the applications.
6. No external dependencies or integrations beyond what's visible in the repository.
7. The Apache version (2.4.41-4ubuntu3.10) is specifically required and not just an example.