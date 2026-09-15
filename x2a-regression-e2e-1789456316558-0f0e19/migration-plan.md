# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains demonstration examples showing Chef InSpec integration with Ansible playbooks, rather than traditional Chef cookbooks requiring migration. The content is already primarily Ansible-based with Chef InSpec used for compliance testing. This represents a hybrid approach where Ansible handles configuration management while Chef InSpec provides compliance verification.

**Migration Scope**: Minimal - primarily involves standardizing existing Ansible playbooks and establishing proper testing frameworks.

**Complexity**: Low - existing Ansible playbooks need refinement rather than full migration.

**Timeline Estimate**: 1-2 weeks for standardization and documentation improvements.

## Module Migration Plan

This repository contains demonstration examples and deployment scripts that showcase Ansible and Chef InSpec integration:

### MODULE INVENTORY

**apache-https-website**:
- Description: Apache web server configuration with HTTPS/SSL setup, self-signed certificate generation, and virtual host management for a simple "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible
- Key Features: SSL certificate generation via OpenSSL modules, Apache virtual host configuration, package management for Ubuntu 20.04

**ssl-security-hardening**:
- Description: SSL/TLS security hardening playbook that disables vulnerable SSL protocols (specifically addresses POODLE vulnerability by enforcing TLS 1.2)
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible
- Key Features: Apache SSL configuration hardening, protocol restriction, service restart handling

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/index.html`: Static HTML content for web server testing
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script for on-premises/cloud VMs
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL protocol verification
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec security profile for SSH root login compliance (STIG-based controls)

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (explicitly specified in kitchen.yml and playbook package versions)
- **Virtual Machine Technology**: Vagrant (configured in Test Kitchen for local development and testing)
- **Cloud Platform**: Not specified (deployment scripts support both on-premises and cloud VMs)

## Migration Approach

### Key Dependencies to Address

- **apache2=2.4.41-4ubuntu3.10**: Specific Ubuntu package version pinned in playbook - update to use package facts or version ranges for flexibility
- **python3-openssl**: Required for Ansible OpenSSL modules - ensure availability across target environments
- **Test Kitchen with Vagrant**: Development/testing dependency - consider migrating to molecule with docker for CI/CD integration

### Security Considerations

- **SSL Certificate Management**: Current implementation uses self-signed certificates generated via Ansible OpenSSL modules
  - Migration approach: Implement proper certificate lifecycle management with Let's Encrypt or internal CA integration
- **Hardcoded Credentials in Deployment Scripts**: Chef server deployment scripts contain plaintext passwords and user details
  - Migration approach: Implement Ansible Vault for credential management and parameterize deployment variables
- **SSH Security Compliance**: InSpec tests verify SSH root login restrictions per STIG requirements
  - Migration approach: Integrate compliance testing into Ansible workflow using ansible-test or molecule with InSpec verifier

### Technical Challenges

- **Test Kitchen to Molecule Migration**: Current testing uses Test Kitchen with Vagrant and InSpec
  - Description: Migrate testing framework to Ansible-native molecule with docker/podman for better CI/CD integration
  - Mitigation strategy: Gradual migration maintaining InSpec tests while adopting molecule structure
- **Chef Infrastructure Dependencies**: Deployment scripts install Chef Automate/Server for InSpec execution
  - Description: Determine if Chef infrastructure is required or if InSpec can run standalone
  - Mitigation strategy: Evaluate InSpec standalone execution or alternative compliance frameworks like Ansible compliance scanning

### Migration Order

1. **apache-https-website** (low risk, high value) - Standardize existing Ansible playbook with best practices, variable management, and role structure
2. **ssl-security-hardening** (moderate complexity) - Integrate security hardening into main web server role, implement proper change detection
3. **Testing Framework Migration** (high complexity) - Migrate from Test Kitchen to molecule while preserving InSpec compliance verification

### Assumptions

- The repository serves as a demonstration/example rather than production infrastructure requiring migration
- Chef InSpec will continue to be used for compliance testing alongside Ansible configuration management
- Target environments will maintain Ubuntu/Debian-based systems as indicated by current playbook package management
- Test Kitchen/Vagrant development workflow may need migration to more CI/CD-friendly alternatives
- Chef infrastructure deployment scripts are for demonstration purposes and may not represent production deployment requirements
- SSL certificate management requirements (self-signed vs. CA-issued) are not clearly defined for production use
- Compliance requirements (STIG controls) indicated in InSpec tests will continue to apply in migrated environment