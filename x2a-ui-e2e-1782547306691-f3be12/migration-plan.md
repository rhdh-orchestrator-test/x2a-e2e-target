# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate to a pure Ansible solution. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing the web server. Can be directly used in Ansible.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM setup

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native solutions:
  - For compliance testing: Use ansible-lint for static analysis
  - For runtime verification: Use Ansible assert module or Molecule for testing
  - Alternative: Integrate with OpenSCAP or other compliance tools via Ansible

- **Test Kitchen (latest)**: Replace with Ansible Molecule for testing infrastructure

- **Vagrant (latest)**: Can continue to be used with Ansible Molecule, or replace with containerized testing using Docker

- **Apache2 (2.4.41-4ubuntu3.10)**: Continue to manage with Ansible, using the apache2_module and other relevant modules

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables vulnerable protocols (SSLv3) and enables only TLSv1.2
  - Migration approach: Use ansible.builtin.lineinfile or ansible.builtin.template to manage Apache SSL configuration

- **SSH Security Hardening**: The InSpec test for SSH root login must be converted to Ansible checks
  - Migration approach: Use ansible.posix.sshd_config module to manage SSH configuration and ansible.builtin.assert for verification

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible.builtin.openssl_* modules with proper secret management
  - Document the count and type of credentials detected per module:
    - chef-automate-deployment: 1 password in plaintext
    - chef-server-deployment: 1 password in plaintext

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible equivalents
  - Description: InSpec provides a domain-specific language for compliance testing that doesn't directly map to Ansible
  - Mitigation strategy: Use a combination of Ansible modules (uri, stat, command with assert) to replicate InSpec tests, or consider maintaining InSpec for testing while using Ansible for configuration management

- **Chef Automate/Server Deployment**: Replacing Chef infrastructure deployment
  - Description: The Chef Automate and Chef Infra Server deployment scripts need to be replaced with equivalent functionality
  - Mitigation strategy: Determine if Chef infrastructure is still needed; if not, remove these components. If Chef compliance tooling is still required, create Ansible playbooks to deploy Chef components or replace with alternative compliance solutions

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - Review and optimize existing Ansible playbook
   - Add idempotency improvements if needed
   - Implement Ansible Vault for any sensitive data

2. **poodle_fix.yml** (low risk, already Ansible)
   - Review and optimize existing Ansible playbook
   - Consider merging with website_https.yml as they manage the same service

3. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assertions or Molecule tests
   - Convert ssh_profile.rb to Ansible assertions or Molecule tests

4. **Chef Deployment Scripts** (high complexity, dependencies)
   - Determine if Chef infrastructure is still needed
   - If needed, create Ansible playbooks to deploy Chef components
   - If not needed, replace with pure Ansible solution

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance testing, not for production deployment.

2. The Chef Automate and Chef Infra Server deployment scripts are examples and may not be actively used in production.

3. The hardcoded credentials in the deployment scripts are examples and not actual production credentials.

4. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the actual deployment could be on any compatible system.

5. The Apache web server configuration is a simple example and may need additional security hardening for production use.

6. The self-signed certificates are for testing purposes only and would be replaced with proper certificates in production.

7. The repository is primarily educational/demonstrational rather than a production infrastructure codebase.

8. The migration to Ansible is intended to consolidate on a single tool rather than using both Chef and Ansible together.