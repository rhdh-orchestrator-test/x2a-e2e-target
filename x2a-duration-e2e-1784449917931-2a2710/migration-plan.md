# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and fixing SSL vulnerabilities
2. Chef InSpec test profiles for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing capabilities while standardizing on Ansible for all configuration management.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-https-verify**:
    - Description: Chef InSpec profile that verifies HTTPS website configuration and SSL security
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh-profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation with security tags (STIG compliance)

- **chef-automate-deploy**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Convert InSpec tests to Ansible assert tasks
  - Option 2: Use ansible-test framework
  - Option 3: Maintain InSpec as a standalone testing tool but invoke it through Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - ansible-test for integration testing

- **Chef Automate/Server**: Replace deployment scripts with:
  - Ansible playbooks for deploying alternative compliance platforms (options include:)
    - AWX/Ansible Tower for automation
    - Compliance as Code using OpenSCAP
    - GitLab CI/CD pipelines with integrated security scanning

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Maintain TLSv1.2 requirement
  - Consider upgrading to also allow TLSv1.3 for improved security

- **SSH Hardening**: Preserve the SSH security controls verified by the InSpec profile
  - Convert the InSpec control to an Ansible task that enforces the same configuration

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup scripts (username: jtonello, password: password)
  - Replace with Ansible Vault for secure credential storage
  - Consider implementing lookup plugins for dynamic credential retrieval

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions will require careful mapping of test semantics
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules
  - Consider maintaining some InSpec tests if they provide unique value difficult to replicate in Ansible

- **Compliance Reporting**: Chef Automate provides compliance reporting that needs an alternative
  - Mitigation: Implement structured output from Ansible compliance checks
  - Consider integration with tools like OpenSCAP or Prometheus for reporting

### Migration Order

1. **website-https.yml** (Priority 1 - already Ansible, low risk)
   - Review and optimize the existing Ansible playbook
   - Convert to Ansible role structure for better reusability

2. **poodle-fix.yml** (Priority 1 - already Ansible, low risk)
   - Integrate into the website-https role as a security hardening task
   - Update to include additional modern security best practices

3. **InSpec Tests** (Priority 2 - moderate complexity)
   - Convert to Ansible assertions or Molecule tests
   - Ensure all compliance checks are preserved

4. **Chef Deployment Scripts** (Priority 3 - high complexity)
   - Replace with Ansible playbooks for alternative compliance platforms
   - Implement secure credential management

### Assumptions

1. The primary goal is standardizing on Ansible while maintaining the same functionality
2. The InSpec tests are valuable and need to be preserved in some form
3. The deployment scripts for Chef Automate/Server will be replaced with equivalent Ansible automation
4. The target environment will remain Ubuntu 20.04 on Vagrant
5. No external dependencies or integrations beyond what's visible in the repository
6. The security compliance requirements (STIG references in ssh_profile.rb) need to be maintained
7. Test Kitchen workflow is important to the team and needs an equivalent in the Ansible ecosystem