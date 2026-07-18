# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations with a focus on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for compliance verification
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing capabilities while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for HTTPS website deployment with InSpec compliance testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS website configuration, SSL security hardening, compliance testing

- **setup-automate**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that configures an Apache web server with HTTPS. Migration considerations include preserving the SSL certificate generation, virtual host configuration, and ensuring proper service restarts.

- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that addresses SSL POODLE vulnerability by enforcing TLSv1.2. Migration considerations include ensuring this security hardening is maintained.

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec. Migration considerations include replacing with equivalent Ansible testing framework or adapting to use Molecule with InSpec.

- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test profile for verifying HTTPS website functionality. Migration considerations include preserving these tests for use with Ansible.

- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test profile for SSH security compliance. Migration considerations include preserving these tests for use with Ansible.

- `setup-automate/deploy-automate.sh`: Shell script for deploying Chef Automate and Chef Infra Server. Migration considerations include replacing with Ansible role for deploying alternative compliance platforms.

- `setup-automate/deploy-chef-server.sh`: Shell script for deploying Chef Infra Server. Migration considerations include replacing with Ansible role for deploying alternative configuration management platforms.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package manager usage in Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Continue using InSpec with Ansible by installing InSpec and running via the `command` or `shell` module
  - Option 2: Replace with Ansible's built-in assert module for basic tests
  - Option 3: Use Ansible Lint for static analysis of playbooks
  - Option 4: Integrate with Molecule for testing Ansible roles

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: Ansible Tower/AWX for orchestration and compliance
  - Option 2: Ansible + OpenSCAP for compliance scanning
  - Option 3: Ansible + Prometheus + Grafana for monitoring and reporting

### Security Considerations

- **SSL/TLS Configuration**: The current playbooks enforce TLSv1.2 and disable vulnerable protocols. This security hardening must be preserved in the migrated Ansible roles.

- **Self-signed Certificates**: The current solution generates self-signed certificates. Consider enhancing with Let's Encrypt integration for production environments.

- **SSH Hardening**: The InSpec profile checks for SSH root login disablement. Ensure this security check is maintained and implemented in the Ansible configuration.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificate handling should use Ansible Vault for private keys

### Technical Challenges

- **Compliance Testing**: Preserving the compliance testing capabilities of InSpec while moving to an Ansible-centric workflow. Mitigation: Either continue using InSpec with Ansible or migrate to an alternative compliance tool that integrates well with Ansible.

- **Chef Automate Replacement**: Finding an equivalent compliance and reporting platform that works well with Ansible. Mitigation: Evaluate Ansible Tower/AWX, OpenSCAP, or other compliance tools that can be integrated with Ansible.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Migrate `website_https.yml` and `poodle_fix.yml` to Ansible roles for better organization
   - Update any deprecated syntax or modules to current Ansible best practices

2. **InSpec Tests** (Moderate complexity)
   - Either preserve as-is for use with Ansible or convert to equivalent Ansible testing mechanisms
   - Ensure compliance checks continue to function with the new Ansible roles

3. **Chef Automate/Server Deployment Scripts** (High complexity)
   - Replace with Ansible roles for deploying alternative compliance and configuration management platforms
   - Ensure user/organization management is handled appropriately in the new solution

### Assumptions

1. The primary goal is to consolidate on Ansible while maintaining the compliance testing capabilities currently provided by InSpec.

2. The current setup is used for demonstration/educational purposes rather than production, based on the repository description and simple configurations.

3. The hardcoded credentials in the setup scripts are for demonstration purposes and would be replaced with proper secret management in production.

4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.

5. The migration will preserve the security hardening measures currently implemented, particularly around SSL/TLS configuration.

6. The team has expertise in both Chef InSpec and Ansible, allowing for a smooth transition between technologies.

7. There are no external dependencies or integrations not visible in the provided repository that might complicate the migration.