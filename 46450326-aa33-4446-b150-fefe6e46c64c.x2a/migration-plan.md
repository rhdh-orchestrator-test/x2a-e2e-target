# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, with the primary components being:

1. Ansible playbooks for configuring a secure HTTPS website
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The main focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Ansible playbook that configures Apache with HTTPS, self-signed certificates, and a basic website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-https-compliance**:
    - Description: Chef InSpec test that verifies HTTPS configuration and website availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh-security-compliance**:
    - Description: Chef InSpec profile that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security control mapping (STIG)

- **chef-infrastructure-deployment**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for website testing
- `README.md`: Documentation files explaining the purpose of the examples

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Integrate with Ansible Automation Platform's compliance capabilities
  - Option 3: Convert InSpec tests to equivalent Ansible assert tasks or custom modules

- **Test Kitchen**: Replace with:
  - Option 1: molecule for Ansible role testing
  - Option 2: ansible-test for collection testing

- **Vagrant**: Can be retained or replaced with:
  - Option 1: Continue using Vagrant with Ansible provisioner
  - Option 2: Switch to molecule with docker or podman driver for lighter testing

### Security Considerations

- **SSL/TLS Configuration**: The current playbooks enforce TLSv1.2 and disable older protocols. Migration should maintain or enhance this security posture.
  - Migration approach: Preserve the same SSL/TLS hardening in the Ansible roles

- **SSH Hardening**: The InSpec profile checks for secure SSH configuration.
  - Migration approach: Create equivalent Ansible tasks to both configure and verify SSH security settings

- **Self-signed Certificates**: The current solution generates self-signed certificates.
  - Migration approach: Consider enhancing with Let's Encrypt integration for production environments

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification tasks.
  - Mitigation: Use Ansible's assert module and uri module to perform similar checks, or consider maintaining InSpec for testing while using Ansible for configuration.

- **Chef Server Deployment**: The shell scripts deploy Chef Automate and Chef Infra Server.
  - Mitigation: These can be replaced with Ansible roles that install and configure the necessary components if Chef infrastructure is still needed, or completely removed if moving entirely to Ansible.

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Review and refactor into a proper Ansible role structure
   - Add documentation and variables

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Incorporate into the HTTPS website role as a security hardening task
   - Add conditional logic for enabling/disabling specific security features

3. **InSpec Tests** (moderate complexity)
   - Convert to Ansible verification tasks or maintain as InSpec tests
   - Ensure test coverage is maintained during migration

4. **Chef Infrastructure Deployment** (high complexity)
   - Determine if Chef infrastructure is still needed
   - If not, remove these components
   - If yes, create Ansible roles to deploy Chef infrastructure

### Assumptions

1. The primary goal is to standardize on Ansible while maintaining the same functionality and security posture.
2. The InSpec tests are valuable and their functionality should be preserved, either as InSpec tests or converted to Ansible.
3. The deployment of Chef infrastructure (Automate and Infra Server) may no longer be needed if fully migrating to Ansible.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The current Vagrant-based testing approach is acceptable, but could be enhanced with more modern testing tools.
6. No external dependencies or integrations beyond what's visible in the repository need to be considered.
7. The security requirements (TLS 1.2, SSH hardening) must be maintained or enhanced in the migrated solution.