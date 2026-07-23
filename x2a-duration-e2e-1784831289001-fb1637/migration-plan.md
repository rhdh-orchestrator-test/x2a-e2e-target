# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and demonstration purposes. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks

The complexity is low to moderate, with an estimated timeline of 1-2 weeks for a complete migration. The repository appears to be primarily for demonstration purposes rather than production infrastructure, which simplifies the migration process.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS is properly configured
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **deploy-automate**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **deploy-chef-server**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec. Migration considerations include replacing with Ansible Molecule for testing.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Use Ansible Molecule with Goss for simpler testing
  - Option 3: Convert InSpec tests to Ansible assert modules for basic validation

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for orchestration
  - Ansible Collections for configuration management
  - Compliance scanning can be handled by OpenSCAP or similar tools integrated with Ansible

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ is enforced (already in poodle_fix.yml)
  - Consider adding more modern cipher suites
  - Implement certificate management via Ansible Vault or external secret management

- **SSH Hardening**: The InSpec test verifies SSH root login is disabled. Migration should:
  - Implement the actual SSH hardening via Ansible
  - Maintain testing capability for SSH configuration

- **Credentials in Scripts**: The deployment scripts contain hardcoded credentials:
  - Migrate all credentials to Ansible Vault
  - Remove hardcoded passwords from scripts
  - Consider implementing dynamic password generation

- **Vault/secrets management**:
  - Chef deployment scripts: 2 hardcoded credentials (username/password)
  - No encrypted data bags or Chef Vault usage detected
  - SSL certificates are generated dynamically, not stored

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks may require learning new testing methodologies and syntax.
  - Mitigation: Use Ansible Molecule with Testinfra which has similar capabilities to InSpec

- **Chef Server Deployment**: Replacing Chef Server deployment with equivalent Ansible functionality.
  - Mitigation: Use AWX/Tower for orchestration and web UI, or consider simpler alternatives if full Chef Automate functionality isn't needed

- **SSL Certificate Management**: Ensuring proper certificate management in the migrated solution.
  - Mitigation: Use Ansible's crypto modules for certificate generation and management

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, just need review and potential optimization
2. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb): Convert to Ansible Molecule tests
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible roles for deploying alternative orchestration solutions

### Assumptions

1. The repository is primarily for demonstration purposes rather than production infrastructure
2. The InSpec tests are used for validation rather than continuous compliance monitoring
3. There's no dependency on Chef-specific features that might be difficult to replicate in Ansible
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
5. The deployment scripts are used for setting up test environments rather than production Chef infrastructure
6. No external data sources or complex data structures are being used
7. No integration with external systems beyond what's visible in the scripts
8. The migration doesn't need to preserve backward compatibility with Chef tools