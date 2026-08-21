# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate setup scripts and Ansible playbooks focused on deploying and testing web servers with HTTPS configuration and compliance testing. The migration scope is relatively small, with only a few Ansible playbooks and Chef InSpec tests that need to be consolidated into a pure Ansible solution. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration and port availability
- `tests/ssh_profile.rb`: InSpec test to verify SSH root login is disabled (compliance test)
- `index.html`: Sample HTML file for testing web server deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible's built-in assert module or community.general.assert for basic tests. For more complex compliance testing, consider:
  - Option 1: Use ansible-lint for static analysis
  - Option 2: Integrate with ansible.posix.mount, ansible.builtin.stat, and other modules for runtime verification
  - Option 3: Keep InSpec as a separate tool but invoke it from Ansible using command/shell modules

- **Test Kitchen (latest)**: Replace with Molecule for Ansible role testing
  - Molecule supports multiple drivers including Vagrant
  - Provides similar functionality for testing infrastructure code

### Security Considerations

- **SSL/TLS Configuration**: The playbooks handle SSL configuration and POODLE vulnerability remediation
  - Migration should preserve the security hardening that disables SSLv3
  - Self-signed certificate generation should be maintained or improved with proper key management

- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions
  - Ensure this security check is maintained in the Ansible migration
  - Consider adding more SSH hardening configurations using ansible.posix.sshd_config

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration should replace these with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible assertions or checks
  - Mitigation: Use ansible.builtin.assert or community.general.assert modules with appropriate conditions
  - For port checking, use wait_for module instead of InSpec port checks

- **Chef Automate Deployment**: Converting Chef Automate deployment scripts to Ansible
  - Mitigation: Create Ansible roles for Chef server deployment if still needed
  - Consider if Chef components are still required or if they can be fully replaced by Ansible

### Migration Order

1. **website-https.yml** (low risk, already in Ansible format)
   - Just needs review and potential refactoring into roles
   - Ensure idempotence and best practices

2. **poodle_fix.yml** (low risk, already in Ansible format)
   - Review and potentially combine with website-https role
   - Ensure idempotence and best practices

3. **InSpec Tests** (moderate complexity)
   - Convert to Ansible assertions or Molecule tests
   - Ensure all compliance checks are maintained

4. **Chef Deployment Scripts** (high complexity)
   - Determine if Chef components are still needed
   - If needed, create Ansible roles for Chef server deployment
   - If not needed, document the deprecation

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, based on the README indicating these are examples related to blog content.

2. The Chef InSpec tests are used for compliance verification of infrastructure deployed by Ansible, suggesting a hybrid approach that could be consolidated.

3. The setup-automate scripts are used for setting up Chef infrastructure, which may or may not be needed in a pure Ansible environment.

4. The hardcoded credentials in the setup scripts are for demonstration purposes and would need to be properly secured in a production environment.

5. The kitchen.yml configuration suggests this is primarily a testing environment rather than production code.

6. No complex Chef cookbooks or recipes are present, making the migration relatively straightforward.